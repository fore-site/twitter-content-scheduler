from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from config.settings import SQLALCHEMY_URI 
from datetime import timezone

job_stores = {
    'postgres': SQLAlchemyJobStore(url=SQLALCHEMY_URI)
}

executors = {
    'default': AsyncIOExecutor()
}

job_defaults = {
    'coalesce': True,
}

scheduler = AsyncIOScheduler(jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone=timezone.utc)