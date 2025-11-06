"""Configuração do Celery."""

from celery import Celery
from app.core.config import settings

# Cria instância do Celery
celery_app = Celery(
    "bulk_email_sender",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.infrastructure.tasks.email_tasks"],
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
