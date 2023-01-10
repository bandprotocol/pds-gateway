from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    MODE: str = "development"
    LOG_LEVEL: str = "INFO"

    # VERIFICATION
    VERIFY_REQUEST_URL: HttpUrl
    ALLOWED_DATA_SOURCE_IDS: list[int]
    CACHE_SIZE: int = 1000
    TTL_TIME: str = "10m"
    MAX_DELAY_VERIFICATION: int = 0

    # ADAPTER
    ADAPTER_TYPE: str
    ADAPTER_NAME: str

    MONGO_DB_URL: str = None
    COLLECTION_DB_NAME: str = None

    class Config:
        env_file = ".env"
