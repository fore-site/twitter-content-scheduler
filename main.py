from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.db import db_pool
from routes import user, post
from starlette_context import plugins
from starlette_context.middleware import ContextMiddleware

@asynccontextmanager
async def lifespan(instance: FastAPI):
    """FastAPI startup/shutdown event"""
    
    print("Starting FastAPI server...")

    instance.async_pool = db_pool

    yield

    print("Shutting down FastAPI server...")
    await instance.async_pool.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    ContextMiddleware,
    plugins=(
        plugins.RequestIdPlugin,
        plugins.CorrelationIdPlugin
    )
)
app.include_router(user.router)
app.include_router(post.router)