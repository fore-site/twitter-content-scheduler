from dotenv import load_dotenv, find_dotenv
from os import environ
# import sys

# sys.path.append('.')

load_dotenv(find_dotenv())

DB_URI = environ.get("DB_CONNECTION_STRING")