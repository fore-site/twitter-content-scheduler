from config.settings import token_uri, JWT_SECRET_KEY, ALGORITHM
from config import db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from starlette_context import context
from typing import Annotated
from utils.AuthUtils import auth_url
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
    """Verify and validate each jwt token. Access or refresh."""
    
    def __init__(self, verify_type: bool = True, refresh: bool = False, dict_format: bool = False):
        """Initialize validation and return type values."""
        self.verify_type = verify_type
        self.refresh = refresh
        self.dict_format = dict_format

        self.credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. JWT token invalid.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    async def __call__(self, token: Annotated[str, Depends(oauth2_scheme)]):
        """Callable that runs in a path operation function."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        except InvalidTokenError:
            raise self.credentials_exceptions
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
            elif self.verify_type is True:
                if self.refresh is False and token_type == "refresh":
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Access token required")
                elif self.refresh is True and token_type == "access":
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                    detail="Refresh token required.")
            elif self.dict_format is True:
                return payload
            else:
                context["user_id"] = user_id
                return user_id
    