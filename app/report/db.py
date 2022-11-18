from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from motor import motor_asyncio


class Verify(BaseModel):
    response_code: int = Field(...)
    is_delay: bool = Field(default=False)
    error_type: Optional[str]
    error_msg: Optional[str]

    def to_dict(self):
        return {k: v for k, v in self.dict().items() if v or type(v) is bool}

        # return {k: v for k, v in asdict(self).items() if v or type(v) is bool}


class ProviderResponse(BaseModel):
    response_code: int = Field(...)
    error_msg: Optional[str]

    def to_dict(self):
        return {k: v for k, v in self.dict().items() if v}


class Report(BaseModel):
    user_ip: str = Field(...)
    reporter_address: Optional[str]
    validator_address: Optional[str]
    request_id: Optional[int]
    data_source_id: Optional[int]
    external_id: Optional[int]
    cached_data: Optional[bool]
    verify: dict = Field(...)
    provider_response: Optional[dict]
    created_at: datetime = Field(default=datetime.utcnow())

    def to_dict(self):
        return {k: v for k, v in self.dict().items() if v or type(v) is bool}


class DB:
    def __init__(self, mongo_db_url: str, db_name: str):
        self.report = motor_asyncio.AsyncIOMotorClient(mongo_db_url)[db_name].get_collection("report")

    async def get_latest_request_info(self):
        cursor = self.report.find({}, {"_id": 0, "user_ip": 0}).sort("created_at", -1).limit(1)
        latest_request_info = await cursor.to_list(length=1)
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
        return latest_request_info[0]

    def save_report(self, report: Report):
        self.report.insert_one(report.to_dict())
