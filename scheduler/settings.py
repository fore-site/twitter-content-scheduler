from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from config.db import DB_URI
from pytz import utc

job_stores = {
    'postgres': SQLAlchemyJobStore(url=DB_URI)
}

executors = {
    'default': ThreadPoolExecutor(20)
}

job_defaults = {
    'coalesce': True,
}

scheduler = AsyncIOScheduler(jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone=utc)