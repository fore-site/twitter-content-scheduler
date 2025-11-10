from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.db import db_pool
from routes import user, post

@asynccontextmanager
async def lifespan(instance: FastAPI):
    """FastAPI startup/shutdown event"""
    
    print("Starting FastAPI server...")

    await db_pool.open()

    yield

    print("Shutting down FastAPI server...")
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(post.router)