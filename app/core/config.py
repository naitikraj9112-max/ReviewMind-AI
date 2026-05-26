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

    @property
    def get_private_key(self) -> str:
        """
        Fixes newline issues from cloud environments (like Render)
        where multiline strings get flattened or escaped.
        """
        if not self.GITHUB_APP_PRIVATE_KEY:
            return ""
        # Fix literal '\n' strings that might have been escaped
        key = self.GITHUB_APP_PRIVATE_KEY.replace("\\n", "\n")
        # If it was completely flattened without any \n or \\n (rare but happens)
        if "-----BEGIN RSA PRIVATE KEY-----" in key and "\n" not in key:
            key = key.replace("-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----\n")
            key = key.replace("-----END RSA PRIVATE KEY-----", "\n-----END RSA PRIVATE KEY-----")
            # The middle part is base64, which usually wraps at 64 chars, but jwt.decode
            # handles it fine as a single long line as long as the headers have newlines.
        return key

settings = Settings()
