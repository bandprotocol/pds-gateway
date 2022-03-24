import os

config = {
    "VERIFY_REQUEST_URL": os.environ.get("VERIFY_REQUEST_URL", None),
    "ENDPOINT_URL": os.environ.get("ENDPOINT_URL", None),
    "ALLOW_DATA_SOURCE_IDS": os.environ.get("ALLOW_DATA_SOURCE_IDS", "").split(","),
    "HEADER_KEY": os.environ.get("HEADER_KEY", None),
    "HEADER_VALUE": os.environ.get("HEADER_VALUE", None),
}
