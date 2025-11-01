from utils.AuthUtils import auth_url
from config.settings import JWT_SECRET_KEY, ALGORITHM
from config import db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from typing import Annotated
import jwt

oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="login", authorizationUrl=auth_url)

async def check_jwt(token: Annotated[str, Depends(oauth2_scheme)], verify_type=True, refresh=False, dict_format=False):
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. JWT token missing or invalid.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise credentials_exceptions
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="JWT token expired")
    else:
        # CHECK IF TOKEN EXISTS IN REDIS BLOCKLIST
        jti = payload.get("jti")
        token_exists_in_redis = await db.redis_client.exists(jti)
        
        if token_exists_in_redis:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="JWT token revoked.")
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
             detail="User not found.")
        elif verify_type is True:
            if refresh is False and token_type == "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Access token required")
            elif refresh is True and token_type == "access":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                    detail="Refresh token required.")
        elif dict_format is True:
            return payload
        else:
            return user_id
    