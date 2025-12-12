from apscheduler.events import EVENT_JOB_ERROR
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.db import db_pool
from routes import user, post
from scheduler.settings import scheduler
from scheduler.listener import event_listener
from starlette_context.middleware import ContextMiddleware
from starlette_context import plugins
import logging
import logging.config

@asynccontextmanager
async def lifespan(instance: FastAPI):
    """FastAPI startup/shutdown event"""
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger()
    
    logger.info("Starting FastAPI server...")

    await db_pool.open()
    logger.info("Database connection pool opened...")

    scheduler.start()
    logger.info("Scheduler instance started...")

    scheduler.add_listener(event_listener, EVENT_JOB_ERROR)

    yield

    logger.info("Shutting down FastAPI server...")
    await db_pool.close()
    scheduler.shutdown()

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