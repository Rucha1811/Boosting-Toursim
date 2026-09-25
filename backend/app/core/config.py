from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Virsa — Community Tourism Ecosystem"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Comma separated allowed origins
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174"

    # Defaults to SQLite for a zero-dependency prototype run.
    # Set a postgres URL (e.g. postgresql+psycopg://...) in production / docker.
    DATABASE_URL: str = "sqlite:///./virsa.db"

    JWT_SECRET: str = "virsa-demo-secret-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    SEED_ON_STARTUP: bool = True
    # Label appended to analytics so demo/simulated data is unambiguous.
    DEMO_MODE: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()