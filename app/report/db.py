from typing import Optional

from motor import motor_asyncio

from app.report.models import Report


class DB:
    """A MongoDB wrapper class for storing Reports.

    Attributes:
        report: AsyncIOMotorClient instance to connect with MongoDB and get the "report" collection.
    """

    def __init__(self, mongo_db_url: str, db_name: str) -> None:
        """Initializes DB with the MongoDB URL and database name.

        Args:
            mongo_db_url: MongoDB URL.
            db_name: Database name.
        """
        self.report = motor_asyncio.AsyncIOMotorClient(mongo_db_url)[db_name].get_collection("report")

    async def get_latest_request_info(self) -> Optional[Report]:
        """Gets the latest request information from the database.

        Returns:
            A report containing the latest report
        """
        cursor = self.report.find().sort("created_at", -1).limit(1)
        latest_request_info = await cursor.to_list(length=1)

        if len(latest_request_info) == 0:
            return None

        return Report(**latest_request_info[0])

    async def get_latest_failed_request_info(self) -> Optional[Report]:
        """Gets the detail of the latest failed request from the database

        Returns:
            A report containing the latest failed report
        """
        cursor = (
            self.report.find(
                {"$or": [{"verify.response_code": {"$ne": 200}}, {"provider_response.response_code": {"$ne": 200}}]},
                {"_id": 0},
            )
            .sort("created_at", -1)
            .limit(1)
        )

        latest_request_info = await cursor.to_list(length=1)

        if len(latest_request_info) == 0:
            return None

        return Report(**latest_request_info[0])

    def save(self, report: Report) -> None:
        """Saves the given report to the database.

        Args:
            report: The Report object to be saved.
        """
        self.report.insert_one(report.to_dict())
