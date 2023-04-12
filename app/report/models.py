from datetime import datetime
from typing import Optional, Any, Dict

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class BaseModel(PydanticBaseModel):
    def to_dict(self) -> dict[str, Any]:
        """Converts the model to a dictionary.

        Returns:
            The Model as a dictionary.
        """
        return self.dict(exclude_none=True)

    class Config:
        orm_mode = True


class GatewayInfo(BaseModel):
    allow_data_source_ids: list[int]
    max_delay_verification: int


class Report(BaseModel):
    pass


class VerifyReport(Report):
    response_code: int
    is_delay: Optional[bool]
    error_type: Optional[str]
    error_msg: Optional[str]
    created_at: datetime = Field(default=datetime.utcnow())


class ProviderResponseReport(Report):
    response_code: int
    error_msg: Optional[str]
    created_at: datetime = Field(default=datetime.utcnow())


class RequestReport(Report):
    user_ip: Optional[str]
    reporter_address: Optional[str]
    validator_address: Optional[str]
    request_id: Optional[int]
    data_source_id: Optional[int]
    external_id: Optional[int]
    created_at: datetime = Field(default=datetime.utcnow())


class Reports(Report):
    latest_request: Optional[Dict[str, Any]]
    latest_response: Optional[Dict[str, Any]]
    latest_verify: Optional[Dict[str, Any]]
