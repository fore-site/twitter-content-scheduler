from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.db import db_pool
from routes import user, post, media
from starlette_context.middleware import ContextMiddleware
from starlette_context import plugins
import logging

@asynccontextmanager
async def lifespan(instance: FastAPI):
    """FastAPI startup/shutdown event"""
    
    print("Starting FastAPI server...")

    await db_pool.open()

    yield

    print("Shutting down FastAPI server...")
    await db_pool.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    ContextMiddleware,
    plugins=(
        plugins.RequestIdPlugin(),
        plugins.CorrelationIdPlugin(),
    )
)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(media.router)