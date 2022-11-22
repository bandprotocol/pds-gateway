import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config(BaseSettings):
    MODE: str = os.environ.get("MODE", "development").lower()
    # VERIFICATION
    VERIFY_REQUEST_URL: str = os.environ.get("VERIFY_REQUEST_URL", None)
    ALLOWED_DATA_SOURCE_IDS: str = os.environ.get("ALLOWED_DATA_SOURCE_IDS", "")
    CACHE_SIZE: int = int(os.environ.get("CACHE_SIZE", "1000"))
    TTL_TIME: str = os.environ.get("TTL_TIME", "10m")
    MAX_DELAY_VERIFICATION: str = os.environ.get("MAX_DELAY_VERIFICATION", "0")
    # ADAPTER
    ADAPTER_TYPE: str = os.environ.get("ADAPTER_TYPE", None)
    ADAPTER_NAME: str = os.environ.get("ADAPTER_NAME", None)

    MONGO_DB_URL: str = os.environ.get("MONGO_DB_URL", None)
    COLLECTION_DB_NAME: str = os.environ.get("COLLECTION_DB_NAME", None)
