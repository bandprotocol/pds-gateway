from datetime import datetime
from enum import Enum

from motor import motor_asyncio
from dataclasses import dataclass, field, asdict


class VerifyErrorType(Enum):
    ERROR_VERIFICATION = "error_verification"
    UNSUPPORTED_DS_ID = "unsupported_ds_id"
    NODE_DELAYED = "node_delayed"


@dataclass
class Report(object):
    user_ip: str = field(default=None)
    reporter_address: str = field(default=None)
    validator_address: str = field(default=None)
    request_id: int = field(default=None)
    from_ds_id: int = field(default=None)
    external_id: int = field(default=None)
    cached_data: bool = field(default=None)
    verify_error_type: VerifyErrorType = field(default=None)
    verify_response_code: int = field(default=None)
    verify_error_msg: str = field(default=None)
    provider_response_code: int = field(default=None)
    provider_error_msg: str = field(default=None)
    created_at: datetime = field(default=datetime.utcnow())

    def __post_init__(self):
        if self.user_ip == None:
            raise TypeError(f"__init__() missing user_ip field")

    def dict(self):
        return {k: v for k, v in asdict(self).items() if v}


class DB(object):
    def __init__(self, mongo_db_url: str, db_name: str):
        self.client = motor_asyncio.AsyncIOMotorClient(mongo_db_url)
        self.db_name = db_name

    async def save_report(self, report: Report):
        await self.client[self.db_name]["report"].insert_one(report.dict())
