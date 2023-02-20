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


class Verify(BaseModel):
    response_code: int = Field(...)
    is_delay: bool = Field(default=False)
    error_type: Optional[str]
    error_msg: Optional[str]


class ProviderResponse(BaseModel):
    response_code: int = Field(...)
    error_msg: Optional[str]


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
