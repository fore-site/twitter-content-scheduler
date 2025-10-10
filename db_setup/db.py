from psycopg_pool import AsyncConnectionPool
from config.settings import DB_URI

db_pool = AsyncConnectionPool(conninfo=DB_URI, open=True)