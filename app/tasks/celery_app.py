from celery import Celery

from app.config import settings

celery_instance = Celery(
    "tasks",
    include=["app.email.send_email_async"],
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
    broker_connection_retry_on_startup=True,
)

# Данные команды нужны для запуска в консоли в среде Windows при локальном запуске
"celery -A app.tasks.celery_app:celery_instance worker --loglevel=info -P gevent"
"celery --app=app.tasks.celery_app:celery_instance flower"
