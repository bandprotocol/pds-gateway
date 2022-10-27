from enum import Enum


class VerifyErrorType(Enum):
    ERROR_VERIFICATION = "error_verification"
    UNSUPPORTED_DS_ID = "unsupported_ds_id"
    NODE_DELAYED = "node_delayed"
