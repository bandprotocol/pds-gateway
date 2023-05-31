import pymongo
from typing import Optional, Callable

from motor import motor_asyncio

from app.report.models import Report


class DB:
    """A MongoDB wrapper class for storing Reports.

    Attributes:
        report: AsyncIOMotorClient instance to connect with MongoDB and get the "report" collection.
    """

    def __init__(
        self, mongo_db_url: str, db_name: str, expiration_time: int, report_class: Callable[..., Report]
    ) -> None:
        """Initializes DB with the MongoDB URL and database name.

        Args:
            mongo_db_url: MongoDB URL.
            db_name: Database name.
        """
        self.report = motor_asyncio.AsyncIOMotorClient(mongo_db_url)[db_name].get_collection("report")
        self.report_class = report_class
        self.create_index_for_expiration(expiration_time)

    async def get_latest_report(self) -> Optional[Report]:
        """Gets the latest request information from the database.

        Returns:
            A report containing the latest report
        """
        cursor = self.report.find({}, {"user_ip": 0}).sort("created_at", -1).limit(1)
        latest_request_info = await cursor.to_list(length=1)

        if len(latest_request_info) == 0:
            return None

        return self.report_class(**latest_request_info[0])

    async def get_latest_failed_report(self) -> Optional[Report]:
        """Gets the detail of the latest failed request from the database

        Returns:
            A report containing the latest failed report
        """
        cursor = (
            self.report.find({"$or": [{"response_code": {"$ne": 200}}]}, {"_id": 0, "user_ip": 0})
            .sort("created_at", -1)
            .limit(1)
        )

        latest_request_info = await cursor.to_list(length=1)

        if len(latest_request_info) == 0:
            return None

        return self.report_class(**latest_request_info[0])

    def save(self, report: Report) -> None:
        """Saves the given report to the database.

        Args:
            report: The Report object to be saved.
        """
        self.report.insert_one(report.to_dict())

    def create_index_for_expiration(self, expiration_time: int) -> None:
        """Creates an index for the report collection to expire documents after a given time.

        Args:
            expiration_time (int): The time in seconds after which the documents will expire.
        """
        # Drop all indexes that exist before creating a new one
        self.report.drop_indexes()
        self.report.create_index([("created_at", pymongo.ASCENDING)], expireAfterSeconds=expiration_time)
