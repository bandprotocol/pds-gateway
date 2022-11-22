from .db import DB


def init_db(url: str, collection_name: str) -> DB:
    if url and collection_name:
        db = DB(url, collection_name)
        print(f"DB : init report data on mongo db")
        return db
    else:
        print(
            f"DB : No DB config -> if you want to save data on db please add [MONGO_DB_URL, COLLECTION_DB_NAME] in env"
        )
        return None
