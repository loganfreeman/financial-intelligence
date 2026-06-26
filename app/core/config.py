from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Financial Intelligence Platform"
    database_url: str = "sqlite:///./financial_intelligence.db"
    seed_on_startup: bool = True
    sec_user_agent: str = "stock-intelligence admin@example.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
