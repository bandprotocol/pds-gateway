from typing import Literal

from pydantic import BaseSettings, HttpUrl

MODES = Literal["production", "development"]
LOG_LEVELS = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
CACHE_TYPES = Literal["local", "redis"]


class Settings(BaseSettings):
    MODE: MODES = "development"
    LOG_LEVEL: LOG_LEVELS = "INFO"

    # Verification
    VERIFY_REQUEST_URL: HttpUrl
    ALLOWED_DATA_SOURCE_IDS: list[int]
    MAX_DELAY_VERIFICATION: int = 0

    # Cache
    CACHE_TYPE: CACHE_TYPES = "local"
    TTL: str = "10m"
    PENDING_TIMEOUT: str = "30s"

    # For local cache
    CACHE_SIZE: int = 1000

    # For redis cache
    REDIS_URL: str = None
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Adapter
    ADAPTER_TYPE: str
    ADAPTER_NAME: str

    # Database
    MONGO_DB_URL: str = None
    COLLECTION_DB_NAME: str = None
    MONGO_DB_EXPIRATION_TIME: int = None

    class Config:
        env_file = ".env"


settings = Settings()
