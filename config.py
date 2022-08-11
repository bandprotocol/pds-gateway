import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "MODE": os.environ.get("MODE", "development").lower(),
    # VERIFICATION
    "VERIFY_REQUEST_URL": os.environ.get("VERIFY_REQUEST_URL", None),
    "ALLOWED_DATA_SOURCE_IDS": os.environ.get("ALLOWED_DATA_SOURCE_IDS", "").split(","),
    "CACHE_SIZE": int(os.environ.get("CACHE_SIZE", "1000")),
    "TTL_TIME": os.environ.get("TTL_TIME", "10m"),
    # ADAPTER
    "ADAPTER_TYPE": os.environ.get("ADAPTER_TYPE", None),
    "ADAPTER_NAME": os.environ.get("ADAPTER_NAME", None),
}
