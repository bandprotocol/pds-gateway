import os

config = {
    "DEBUG": os.environ.get("DEBUG", False),
    "HOST": os.environ.get("HOST", "0.0.0.0"),
    "PORT": os.environ.get("PORT", "8000"),
    "ENDPOINT_URL": os.environ.get("ENDPOINT_URL"),
    "ALLOW_DATA_SOURCE_IDS": os.environ.get("ALLOW_DATA_SOURCE_IDS", "").split(","),
    "BANDCHAIN_REST_ENDPOINT": os.environ.get("BANDCHAIN_REST_ENDPOINT", None),
    "API_KEY": os.environ.get("API_KEY"),
    "REDIS": os.environ.get("REDIS", None),
}
