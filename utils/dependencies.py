from config.settings import token_uri, JWT_SECRET_KEY, ALGORITHM
from config import db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from redis.exceptions import ConnectionError as RedisConnectionError
from starlette_context import context
from typing import Annotated
from utils.auth_utils import auth_url
from utils.exceptions import redis_connection_exception
import jwt

oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl=token_uri, 
                                              authorizationUrl=auth_url, 
                                              refreshUrl=token_uri, 
                                              scopes={
                                                  "tweet.read": "App can read user's tweets",
                                                  "tweet.write": "App can create tweets for users.",
                                                  "users.read": "App can view other users' profiles",
                                                  "media.write": "App can upload media for users.",
                                                  "offline.access": "Oauth provider returns refresh token for unlimited access"
                                              })

class CheckJwt:
    """Verify and validate jwt token. Access or refresh."""
    
    def __init__(self, verify_type: bool = True, refresh: bool = False, dict_format: bool = False):
        self.verify_type = verify_type
        self.refresh = refresh
        self.dict_format = dict_format

        self.credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. JWT token invalid.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    async def __call__(self, token: Annotated[str, Depends(oauth2_scheme)]) -> int:
        """Callable that runs in a path operation function."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="JWT token expired")
        except InvalidTokenError:
            raise self.credentials_exceptions
        else:
        # CHECK IF TOKEN EXISTS IN REDIS BLOCKLIST
            jti = payload.get("jti")
            try:
                token_exists_in_redis = await db.redis_client.exists(jti)
            except RedisConnectionError:
                raise redis_connection_exception
            if token_exists_in_redis:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="JWT token revoked.")
            user_id = payload.get("sub")
            token_type = payload.get("type")
        
            if self.verify_type:
                if not self.refresh and token_type == "refresh":
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Access token required")
                elif self.refresh and token_type == "access":
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                    detail="Refresh token required.")
            if self.dict_format:
                return payload
            # STORE USER ID IN REQUEST-RESPONSE CONTEXT
            context["user_id"] = user_id
            return int(user_id)
    