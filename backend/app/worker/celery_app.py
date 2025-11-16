"""
Celery Application Configuration
"""

from celery import Celery

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "clipkit",
    broker=settings.worker.broker_url,
    backend=settings.worker.result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.worker.task_time_limit,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.worker"])
