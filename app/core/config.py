from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # GitHub
    GITHUB_APP_ID: str = ""
    GITHUB_APP_PRIVATE_KEY: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_PAT: str = ""
    
    # GCP / Vertex AI / AI Studio
    GEMINI_API_KEY: str = ""
    GCP_PROJECT_ID: str = ""
    GCP_LOCATION: str = "us-central1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/reviewmind"
    
    # Redis / Celery
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
