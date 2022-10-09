import functools
from sanic.exceptions import SanicException
from sanic.request import Request

from app.utils.helper import get_bandchain_params
from app.report.db import DB, VerifyErrorType


class CollectVerifyData:
    def __init__(self, db: DB = None):
        self.db = db

    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper_collect_verify_data(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except SanicException as e:
                # save when exception happen
                request = [arg for arg in args if isinstance(arg, Request)][0]

                client_ip = request.ip
                bandchain_params = get_bandchain_params(request.headers)

                if self.db:
                    verify_error_type = VerifyErrorType.ERROR_VERIFICATION.value
                    if e.message[0:19] == "wrong datasource_id":
                        verify_error_type = VerifyErrorType.UNSUPPORTED_DS_ID.value

                    doc = {
                        "user_ip": client_ip,
                        "reporter_address": bandchain_params.get("reporter", None),
                        "validator_address": bandchain_params.get("validator", None),
                        "request_id": bandchain_params.get("request_id", None),
                        "external_id": bandchain_params.get("external_id", None),
                        "from_ds_id": bandchain_params.get("data_source_id", None),
                        "verify_error_type": verify_error_type,
                        "verify_response_code": e.status_code,
                        "verify_error_msg": e.message,
                    }
                    await self.db.client["pds-test"]["report"].insert_one(doc)

                raise e

        return wrapper_collect_verify_data


class CollectRequestData:
    def __init__(self, db: DB = None):
        self.db = db

    def __call__(self, func):
        async def wrapper_collect_request_data(*args, **kwargs):
            try:
                request = [arg for arg in args if isinstance(arg, Request)][0]
                client_ip = request.ip
                bandchain_params = get_bandchain_params(request.headers)

                res = await func(*args, **kwargs)

                if self.db:
                    doc = {
                        "user_ip": client_ip,
                        "reporter_address": bandchain_params.get("reporter", None),
                        "validator_address": bandchain_params.get("validator", None),
                        "request_id": bandchain_params.get("request_id", None),
                        "external_id": bandchain_params.get("external_id", None),
                        "from_ds_id": bandchain_params.get("data_source_id", None),
                        "provider_response_code": res.status,
                    }
                    await self.db.client["pds-test"]["report"].insert_one(doc)

                return res

            except SanicException as e:
                if self.db:
                    doc = {
                        "user_ip": client_ip,
                        "reporter_address": bandchain_params.get("reporter", None),
                        "validator_address": bandchain_params.get("validator", None),
                        "request_id": bandchain_params.get("request_id", None),
                        "external_id": bandchain_params.get("external_id", None),
                        "from_ds_id": bandchain_params.get("data_source_id", None),
                        "provider_response_code": res.status,
                        "provider_error_msg": e.message,
                    }

                raise e

        return wrapper_collect_request_data
