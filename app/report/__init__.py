from logging import Logger
from .db import DB


def init_db(url: str, collection_name: str, log: Logger) -> DB:
    if url and collection_name:
        db = DB(url, collection_name)
        log.info(f"DB : init report data on mongo db")
        return db
    else:
        log.info(
            f"DB : No DB config -> if you want to save data on db please add [MONGO_DB_URL, COLLECTION_DB_NAME] in env"
        )
        return None
