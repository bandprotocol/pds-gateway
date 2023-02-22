from datetime import datetime
from typing import Optional, Any

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


class Verify(BaseModel):
    response_code: int
    is_delay: Optional[bool]
    error_type: Optional[str]
    error_msg: Optional[str]


class ProviderResponse(BaseModel):
    response_code: int
    error_msg: Optional[str]


class Report(BaseModel):
    user_ip: str
    reporter_address: Optional[str]
    validator_address: Optional[str]
    request_id: Optional[int]
    data_source_id: Optional[int]
    external_id: Optional[int]
    cached_data: Optional[bool]
    verify: Verify
    provider_response: Optional[ProviderResponse]
    created_at: datetime = Field(default=datetime.utcnow())


class GatewayInfo(BaseModel):
    allow_data_source_ids: list[int]
    max_delay_verification: int


class StatusReport(BaseModel):
    gateway_info: GatewayInfo
    latest_request: Optional[Report]
    latest_failed_request: Optional[Report]
