from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "reviewmind_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.review_tasks"]
)

celery_app.conf.task_routes = {
    "app.tasks.review_tasks.*": "main-queue"
}
