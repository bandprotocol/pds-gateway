import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MODE = os.environ.get("MODE", "development").lower()
    # VERIFICATION
    VERIFY_REQUEST_URL = os.environ.get("VERIFY_REQUEST_URL", None)
    ALLOWED_DATA_SOURCE_IDS = os.environ.get("ALLOWED_DATA_SOURCE_IDS", "").split(",")
    CACHE_SIZE = int(os.environ.get("CACHE_SIZE", "1000"))
    TTL_TIME = os.environ.get("TTL_TIME", "10m")
    MAX_DELAY_VERIFICATION = os.environ.get("MAX_DELAY_VERIFICATION", "0")
    # ADAPTER
    ADAPTER_TYPE = os.environ.get("ADAPTER_TYPE", None)
    ADAPTER_NAME = os.environ.get("ADAPTER_NAME", None)

    MONGO_DB_URL = os.environ.get("MONGO_DB_URL", None)
    COLLECTION_DB_NAME = os.environ.get("COLLECTION_DB_NAME", None)
