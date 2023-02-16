from typing import Any

from motor import motor_asyncio

from app.report.models import Report


class DB:
    """MongoDB wrapper class for storing Reports."""

    def __init__(self, mongo_db_url: str, db_name: str) -> None:
        """Inits DB with the db URL and name.

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
                "user_ip": "0.0.0.0"
                "reporter_address": "band1tlhlzds3226zcqfjl3npj0pjzzxu5f2um4f3m8"
                "validator_address": "bandvaloper1r00x80djyu6wkxpceegmvn5w9nx65prgqhxkzq"
                "request_id": 1
                "data_source_id": 1
                "external_id": 0
                "cached_data": True
                "verify": {}
                "provider_response": {}
                "created_at": ""
            }
        """
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
                "user_ip": "0.0.0.0"
                "reporter_address": "band1tlhlzds3226zcqfjl3npj0pjzzxu5f2um4f3m8"
                "validator_address": "bandvaloper1r00x80djyu6wkxpceegmvn5w9nx65prgqhxkzq"
                "request_id": 1
                "data_source_id": 1
                "external_id": 0
                "cached_data": True
                "verify": {}
                "provider_response": {}
                "created_at": ""
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
        """Saves the report to the database

        Args:
            report: Report to save
        """
        self.report.insert_one(report.to_dict())


