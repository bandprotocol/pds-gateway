from datetime import datetime

from motor import motor_asyncio
from dataclasses import dataclass, field, asdict

from app.utils.types import VerifyErrorType


@dataclass
class Verify:
    response_code: int = field(default=None)
    is_delay: bool = field(default=False)
    error_type: VerifyErrorType = field(default=None)
    error_msg: str = field(default=None)

    def dict(self):
        return {k: v for k, v in asdict(self).items() if v or type(v) is bool}


@dataclass
class ProviderResponse:
    response_code: int = field(default=None)
    error_msg: str = field(default=None)

    def dict(self):
        return {k: v for k, v in asdict(self).items() if v or type(v) is bool}


@dataclass
class Report:
    user_ip: str = field(default=None)
    reporter_address: str = field(default=None)
    validator_address: str = field(default=None)
    request_id: int = field(default=None)
    from_ds_id: int = field(default=None)
    external_id: int = field(default=None)
    cached_data: bool = field(default=False)
    verify: dict = field(default=None)
    provider_response: dict = field(default=None)
    created_at: datetime = field(default=datetime.utcnow())

    def dict(self):
        return {k: v for k, v in asdict(self).items() if v or type(v) is bool}


class DB:
    def __init__(self, mongo_db_url: str, db_name: str):
        self.db = motor_asyncio.AsyncIOMotorClient(mongo_db_url)[db_name]

    def save_report(self, report: Report):
        self.db["report"].insert_one(report.dict())
