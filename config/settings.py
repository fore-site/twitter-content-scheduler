from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

DB_URI = os.environ.get("DB_CONNECTION_STRING")
SQLALCHEMY_URI = os.environ.get("SQLALCHEMY_DB_CONNECTION_STRING")
REDIS_URI = os.environ.get("REDIS_URI")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get("REDIRECT_URI")
token_uri = str("https://api.x.com/2/oauth2/token")
authorize_url = str('https://x.com/i/oauth2/authorize')
scope = "tweet.read tweet.write users.read offline.access media.write"
MEDIA_UPLOAD_ENDPOINT = str("https://api.x.com/2/media/upload")
WASABI_SECRET_KEY = os.environ.get("WASABI_SECRET_KEY")
WASABI_ACCESS_KEY = os.environ.get("WASABI_ACCESS_KEY")

# use "openssl rand -hex 32" to generate secret key
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"