from logging import Logger
from typing import Optional

from app.report import DB


def init_db(url: Optional[str], collection_name: Optional[str], log: Logger) -> Optional[DB]:
    """Initializes the database if the URL and collection name are provided.

    Args:
        url: The URL of the MongoDB instance.
        collection_name: The name of the collection to store reports in.
        log: The logger instance.

    Returns:
        The DB instance if the url and collection_name are provided, or None if not.
    """
    if url and collection_name:
        db = DB(url, collection_name)
        log.info(f"DB: Report data is being stored on MongoDB collection {collection_name}.")
        return db
    else:
        log.info(
            f"DB: No DB config -> if you want to save data on db please add [MONGO_DB_URL, COLLECTION_DB_NAME] in env"
        )
        return None
