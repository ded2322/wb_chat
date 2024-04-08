from celery import Celery
from celery.schedules import crontab

from core.config import settings

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["core.tasks.tasks"]
)
