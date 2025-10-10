from contextlib import asynccontextmanager
from fastapi import FastAPI
from db_setup.db import db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI startup/shutdown event"""
    
    print("Starting FastAPI server...")
    await db_pool.open()

    yield

    print("Shutting down FastAPI server...")
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello world"}