from logging import Logger
from typing import Optional

from app.report import DB


def init_db(url: Optional[str], collection_name: Optional[str], log: Logger) -> Optional[DB]:
    """Helper function to help initialize the database.

    Args:
        url: MongoDB URL.
        collection_name: DB collection name.
        log: Logger.

    Returns:
        The database if url and collection_name is given or None if not.
    """
    if url and collection_name:
        db = DB(url, collection_name)
        log.info(f"DB : init report data on mongo db")
        return db
    else:
        log.info(
            f"DB : No DB config -> if you want to save data on db please add [MONGO_DB_URL, COLLECTION_DB_NAME] in env"
        )
        return None
