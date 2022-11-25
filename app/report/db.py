from motor import motor_asyncio

from app.report.models import Report


class DB:
    def __init__(self, mongo_db_url: str, db_name: str):
        self.report = motor_asyncio.AsyncIOMotorClient(mongo_db_url)[db_name].get_collection("report")

    async def get_latest_request_info(self):
        cursor = self.report.find({}, {"_id": 0, "user_ip": 0}).sort("created_at", -1).limit(1)
        latest_request_info = await cursor.to_list(length=1)

        if len(latest_request_info) == 0:
            return {}

        return latest_request_info[0]

    async def get_latest_verify_failed(self):
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

    def save_report(self, report: Report):
        print(report.to_dict())
        self.report.insert_one(report.to_dict())
