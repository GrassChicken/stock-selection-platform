from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 5100
    APP_ENV: str = "development"
    REDIS_URL: str = "redis://localhost:6379/0"
    DB_URL: str = "sqlite:///./stock_platform.db"
    SCHEDULE_HOUR: int = 16
    SCHEDULE_MINUTE: int = 0
    SCHEDULE_ENABLED: bool = True
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""
    FEISHU_WEBHOOK: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
