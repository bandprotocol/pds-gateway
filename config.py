import os

config = {
    "ENDPOINT_URL": os.environ.get("ENDPOINT_URL"),
    "BANDCHAIN_REST_ENDPOINT": os.environ.get("BANDCHAIN_REST_ENDPOINT", None),
    "ALLOW_DATA_SOURCE_IDS": os.environ.get("ALLOW_DATA_SOURCE_IDS", "").split(","),
    "HEADER_KEY": os.environ.get("HEADER_KEY", None),
    "HEADER_VALUE": os.environ.get("HEADER_VALUE", None),
}
