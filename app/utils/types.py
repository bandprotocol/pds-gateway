from pydantic import BaseModel
from enum import Enum


class VerifyErrorType(Enum):
    FAILED_VERIFICATION = "failed_verification"
    UNSUPPORTED_DS_ID = "unsupported_ds_id"
    SERVER_ERROR = "server_error"


class ErrorResponse(BaseModel):
    verify_error_type: str
    msg: str
