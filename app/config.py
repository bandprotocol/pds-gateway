from typing import Literal

from pydantic import BaseSettings, HttpUrl


Modes: Literal["production", "development"]
LoggingLevels: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]


class Settings(BaseSettings):
    MODE: Modes = "development"
    LOG_LEVEL: LoggingLevels = "INFO"

    # VERIFICATION
    VERIFY_REQUEST_URL: HttpUrl
    ALLOWED_DATA_SOURCE_IDS: list[int]
    CACHE_SIZE: int = 1000
    TTL: str = "10m"
    MAX_DELAY_VERIFICATION: int = 0

    # ADAPTER
    ADAPTER_TYPE: str
    ADAPTER_NAME: str

    MONGO_DB_URL: str = None
    COLLECTION_DB_NAME: str = None

    class Config:
        env_file = ".env"
