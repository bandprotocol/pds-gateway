from pydantic import BaseSettings


class Settings(BaseSettings):
    MODE: str = "development"
    # VERIFICATION
    VERIFY_REQUEST_URL: str
    ALLOWED_DATA_SOURCE_IDS: str
    CACHE_SIZE: int = 1000
    TTL_TIME: str = "10m"
    MAX_DELAY_VERIFICATION: str = "0"
    # ADAPTER
    ADAPTER_TYPE: str
    ADAPTER_NAME: str

    MONGO_DB_URL: str
    COLLECTION_DB_NAME: str

    class Config:
        env_file = ".env"
