from typing import Literal
from pydantic import PostgresDsn, AmqpDsn, RedisDsn
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    environment: Literal["development", "staging", "production"]
    debug: bool
    api_v1_prefix: str
    log_level: str

    database_url: PostgresDsn
    celery_broker_url: AmqpDsn
    celery_result_backend: RedisDsn
    redis_url: RedisDsn
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()