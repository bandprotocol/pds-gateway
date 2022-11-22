from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Verify(BaseModel):
    response_code: int = Field(...)
    is_delay: bool = Field(default=False)
    error_type: Optional[str]
    error_msg: Optional[str]

    def to_dict(self):
        return {k: v for k, v in self.dict().items() if v or type(v) is bool}


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
