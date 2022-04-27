import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MODE = os.environ.get("MODE", "development").lower()
    # VERIFICATION
    VERIFY_REQUEST_URL = os.environ.get("VERIFY_REQUEST_URL", None)
    ALLOWED_DATA_SOURCE_IDS = os.environ.get("ALLOWED_DATA_SOURCE_IDS", "").split(",")
    # ADAPTER
    ADAPTER_TYPE = os.environ.get("ADAPTER_TYPE", None)
    ADAPTER_NAME = os.environ.get("ADAPTER_NAME", None)
