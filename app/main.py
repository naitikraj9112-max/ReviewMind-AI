import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.endpoints import github, review, health

app = FastAPI(
    title="ReviewMind AI",
    description="AI-Powered Pull Request Code Review Bot using Google Gemini",
    version="2.0.0",
)

# API routes
app.include_router(github.router, prefix="/webhook/github", tags=["github"])
app.include_router(review.router, prefix="/review", tags=["review"])
app.include_router(health.router, prefix="/health", tags=["health"])

# Serve frontend static files (CSS, JS)
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    async def serve_landing_page():
        return FileResponse(str(frontend_dir / "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "Welcome to ReviewMind AI", "docs": "/docs"}
