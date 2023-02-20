from typing import Any

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

    async def get_latest_request_info(self) -> dict[str, Any]:
        """Gets the latest request information from the database.

        Returns:
            A dictionary in the following format is returned
            For example:
            {
                "reporter_address": "band000000000000000000000000000000000000000",
                "validator_address": "band000000000000000000000000000000000000000",
                "request_id": 1,
                "data_source_id": 1,
                "external_id": 0,
                "cached_data": true,
                "verify": {
                    "response_code": 200,
                    "is_delay": false
                },
                "provider_response": {
                    "response_code": 200
                }
                "created_at": {
                    "$date": "1970-01-01T00:00:00Z"
                }
            }
        """
        # Filter out user IP and storage ID
        cursor = self.report.find(filter={"_id": 0, "user_ip": 0}).sort("created_at", -1).limit(1)
        latest_request_info = await cursor.to_list(length=1)

        if len(latest_request_info) == 0:
            return {}

        return latest_request_info[0]

    async def get_latest_failed_request_info(self) -> dict[str, Any]:
        """Gets the detail of the latest failed request from the database

        Returns:
            A dictionary in the following format is returned
            For example:
            {
                "reporter_address": "band000000000000000000000000000000000000000",
                "validator_address": "band000000000000000000000000000000000000000",
                "request_id": 1,
                "data_source_id": 1,
                "external_id": 0,
                "cached_data": true,
                "verify": {
                    "response_code": 200,
                    "is_delay": false
                },
                "provider_response": {
                    "response_code": 500,
                    "error_msg": "Server error"
                }
                "created_at": {
                    "$date": "1970-01-01T00:00:00Z"
                }
            }
        """
        cursor = (
            self.report.find(
                {"$or": [{"verify.response_code": {"$ne": 200}}, {"provider_response.response_code": {"$ne": 200}}]},
                {"_id": 0, "user_ip": 0},
            )
            .sort("created_at", -1)
            .limit(1)
        )
        latest_request_info = await cursor.to_list(length=1)

        if len(latest_request_info) == 0:
            return {}

        return latest_request_info[0]

    def save(self, report: Report) -> None:
        """Saves the given report to the database.

        Args:
            report: The Report object to be saved.
        """
        self.report.insert_one(report.to_dict())
