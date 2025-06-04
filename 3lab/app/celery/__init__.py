from celery import Celery

broker_url = backend_url = "redis://localhost:6379/0"


celery_app = Celery("encryption_tasks", broker=broker_url, backend=backend_url)
# Celery будет отслеживать и сохранять статус задачи, когда она переходит в состояние "started" (началась выполнение)
celery_app.conf.task_track_started = True

# Регистрируем задачи при старте
from app.celery import tasks