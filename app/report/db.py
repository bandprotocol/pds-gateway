from datetime import datetime
from enum import Enum
from mimetypes import init
from mongoengine import Document, connect
from mongoengine.fields import StringField, IntField, BooleanField, EnumField, DateTimeField


class VerifyErrorType(Enum):
    ERROR_VERIFICATION = "error_verification"
    UNSUPPORTED_DS_ID = "unsupported_ds_id"
    NODE_DELAYED = "node_delayed"


class DB:
    def __init__(self, mongo_db_url):
        connect(host=mongo_db_url)

    def update_timestamp(sender, document, **kwargs):
        document.updated_at = datetime.utcnow()

    class Report(Document):
        user_ip = StringField(required=True)
        reporter_address = StringField()
        validator_address = StringField()
        request_id = IntField()
        from_ds_id = IntField()
        external_id = IntField()
        cached_data = BooleanField(default=False)
        verify_error_type = EnumField(VerifyErrorType)
        verify_response_code = IntField()
        verify_error_msg = StringField()
        provider_response_code = IntField()
        provider_error_msg = StringField()

        created_at = DateTimeField(required=True, default=datetime.utcnow)
        updated_at = DateTimeField(required=True, default=datetime.utcnow)

        meta = {
            "indexes": [{"fields": ["created_at"], "expireAfterSeconds": 10}],
        }  # ttl index
