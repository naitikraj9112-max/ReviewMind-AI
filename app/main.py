from fastapi import FastAPI

from app.core.celery_app import celery_app
from app.api.endpoints import github, review, health

app = FastAPI(
    title="ReviewMind AI",
    description="Cloud-Native AI Code Review Assistant for Engineering Teams",
    version="1.0.0",
)

app.include_router(github.router, prefix="/webhook/github", tags=["github"])
app.include_router(review.router, prefix="/review", tags=["review"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ReviewMind AI"}


