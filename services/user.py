from config import db
from fastapi import Depends, HTTPException, status
from psycopg.rows import dict_row
from typing import Annotated
from utils.auth_utils import twitter_client, create_access_token, create_refresh_token
from utils.db_utils import check_or_update_user_status
from utils.dependencies import CheckJwt
from utils.twitter_utils import fetch_user
from utils.common import fetch_oauth_from_redis
from utils.exceptions import redis_connection_exception
from models.UserModel import BaseUser, UserOut
from models.TypeModel import UserStatus
from models.TokenModel import Token
from redis.exceptions import ConnectionError as RedisConnectionError
import json
import logging

logger = logging.getLogger()

async def create_user_in_db(user: BaseUser) -> tuple:
    """Logic to create new user in database"""
    async with db.db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            INSERT INTO users (id, username, display_name, profile_img, is_premium)
            VALUES
                (%s, %s, %s, %s, %s)
            """, (user.id, 
                  user.username, 
                  user.display_name, 
                  user.profile_img, 
                  user.is_premium))
        
    # SAVE OAUTH TOKEN TO REDIS
    serialized_token = json.dumps(twitter_client.token)
    try:
        await db.redis_client.set(f"{user.id}:oauth", serialized_token)
    except RedisConnectionError:
        raise redis_connection_exception
    # CREATE AND RETURN JWT ACCESS TOKEN 
    payload = {"sub": user.id}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return access_token, refresh_token

async def get_access_refresh_token() -> Token:
    """Logic to get new access and refresh token."""
    current_user = await fetch_user()
    
    # VALIDATE AGAINST PYDANTIC MODEL
    validated_user = BaseUser(id=current_user["data"].get("id"),
                  username=current_user["data"].get("username"),
                  display_name=current_user["data"].get("name"),
                  profile_img=current_user["data"].get("profile_image_url"), 
                  is_premium=current_user["data"].get("verified"))

    # CHECK IF USER ALREADY EXISTS IN DATABASE, ELSE CREATE NEW USER
    payload = {"sub": validated_user.id}
    try:
        user_exists_in_db = await db.redis_client.exists(f"{validated_user.id}:oauth")
    except RedisConnectionError:
        raise redis_connection_exception
    
    if user_exists_in_db:
        # CHECK AND/OR UPDATE USER STATUS
         
        user_status = await check_or_update_user_status(db.db_pool, validated_user.id)
        if user_status == UserStatus.DISABLED:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                    detail="User suspended.")
        # SAVE NEW OAUTH TOKEN TO REDIS
        serialized_token = json.dumps(twitter_client.token)

        try:
            await db.redis_client.set(f"{validated_user.id}:oauth", serialized_token)
        except RedisConnectionError:
            raise redis_connection_exception
        
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
    else:
        tokens = await create_user_in_db(validated_user)
        access_token = tokens[0]
        refresh_token = tokens[1]
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

async def get_current_user(user_id: Annotated[int, Depends(CheckJwt())]):
    """Logic to get authenticated user."""
    async with db.db_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                    SELECT 
                        u.*, 
                        (SELECT COUNT(*) FROM posts WHERE posts.user_id = %(user_id)s AND posts.post_status ='pending') AS pending_posts, 
                        (SELECT COUNT(*) FROM posts WHERE posts.user_id = %(user_id)s AND posts.post_status = 'sent') AS sent_posts, 
                        (SELECT COUNT(*) FROM posts WHERE posts.user_id = %(user_id)s AND posts.post_status = 'failed') AS failed_posts 
                        FROM users AS u
                        WHERE u.id = %(user_id)s               
                    """, {"user_id": user_id})
            result = await cur.fetchall()
            if not result:
                raise HTTPException(status_code=404, detail=f'User {user_id} does not exist')
    result_dict = result[0]
    user = UserOut(**result_dict)
    return user
        
async def get_current_active_user(current_user: Annotated[UserOut, Depends(get_current_user)]):
    """Logic to get authenticated user with an active status."""
    if current_user.user_status == UserStatus.DEACTIVATED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="User deactivated.")
    elif current_user.user_status == UserStatus.DISABLED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                        detail="User suspended.")
    else:
        return current_user       

async def get_new_access_token(user_id: Annotated[int, Depends(CheckJwt(refresh=True))]):
    """Logic to get new access token."""
    new_access_token = create_access_token({"sub": user_id})
    return Token(access_token=new_access_token, token_type="bearer")

async def revoke_tokens(payload: Annotated[dict, Depends(CheckJwt(verify_type=False, dict_format=True))]):
    """Logic to revoke both access and refresh tokens"""
    jti = payload.get("jti")
    ttype = payload.get("type")
    try:
        # ADD TOKEN TO BLOCKLIST, SET TO EXPIRE IN EXACT TIME ITS REFRESH/ACCESS TOKEN EXPIRES
        await db.redis_client.set(jti, "", ex=604800 if ttype == "refresh" else 1800)
    except RedisConnectionError:
        raise redis_connection_exception
    
    return {"detail": f"{ttype} token revoked successfully."}

async def update_user(user_id: Annotated[int, Depends(CheckJwt())]):
    """Logic to update user details from X api."""
    # FETCH OAUTH TOKEN FROM REDIS
    token = await fetch_oauth_from_redis(f"{user_id}:oauth")

    # RETRIEVE USER DETAILS FROM TWITTER/X
    current_user = await fetch_user(token=token)

    # VALIDATE AGAINST PYDANTIC MODEL
    validated_user = BaseUser(id=user_id,
                  username=current_user["data"].get("username"),
                  display_name=current_user["data"].get("name"),
                  profile_img=current_user["data"].get("profile_image_url"), 
                  is_premium=current_user["data"].get("verified"))

    async with db.db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            UPDATE users
            SET username = %(username)s, 
                display_name = %(name)s,
                profile_img = %(profile_image_url)s,
                is_premium = %(verified)s
            WHERE users.id = %(user_id)s
            """, {"username": validated_user.username, 
                "name": validated_user.display_name, 
                "profile_image_url": validated_user.profile_img, 
                "verified": validated_user.is_premium, 
                "user_id": user_id})
    return validated_user

async def deactivate_user(user_id: Annotated[int, Depends(CheckJwt())]):
    async with db.db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
        UPDATE users
        SET user_status = %(deactivated)s
        WHERE users.id = %(user_id)s
    """, {"deactivated": UserStatus.DEACTIVATED.value,
      "user_id": user_id})
    
    return {"message": f'User {user_id} deactivated.'}