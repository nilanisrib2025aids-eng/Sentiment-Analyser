from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentiment Intelligence Platform"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./sentiment.db"
    JWT_SECRET_KEY: str = "change-me-dev-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    GEMINI_API_KEY: str = ""
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    GEMINI_TIMEOUT_SECONDS: float = 45.0
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DATABASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[2] / ".env", extra="ignore")


settings = Settings()
