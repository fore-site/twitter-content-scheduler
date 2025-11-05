from authlib.integrations.httpx_client import AsyncOAuth2Client
from config.settings import client_id, client_secret, token_uri, redirect_uri, authorize_url, scope, JWT_SECRET_KEY, ALGORITHM
from datetime import timedelta, datetime, timezone
from utils.tokenUtils import update_oauth_token
import base64
import hashlib
import jwt
import os
import re
import uuid

# GENERATE TWITTER CLIENT SESSION
twitter_client = AsyncOAuth2Client(client_id=client_id,
                                   client_secret=client_secret,
                                   token_endpoint=token_uri,
                                   redirect_uri=redirect_uri,
                                   update_token=update_oauth_token,
                                   scope=scope,
                                   code_challenge_method='S256',
                                   )

# GENERATE CODE VERIFIER AND CODE CHALLENGE FOR PKCE
def generate_verifier():
    code_verifier = base64.urlsafe_b64encode(os.urandom(48)).decode()
    code_verifier = re.sub("[^a-zA-Z0-9]+","", code_verifier)

    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode()
    code_challenge = code_challenge.replace("=", "")
    
    return code_verifier, code_challenge

# CREATE JWT ACCESS TOKEN
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "jti": uuid.uuid4(), "type": "access"})
    encoded_access_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire, "jti": uuid.uuid4(), "type": "refresh"})
    encoded_refresh_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token

code_verifier, code_challenge = generate_verifier()
auth_url, state = twitter_client.create_authorization_url(url=authorize_url, code_verifier=code_verifier)

