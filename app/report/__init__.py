from email import message
import functools
from sanic.exceptions import SanicException
from sanic.request import Request
from sanic import Sanic

from app.utils.helper import get_bandchain_params
from app.report.db import DB, VerifyErrorType
from app.report.helper import bytes_to_json


def collect_verify_data(func, db: DB = None):
    @functools.wraps(func)
    async def wrapper_collect_verify_data(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except SanicException as e:
            # save when exception happen
            request = [arg for arg in args if isinstance(arg, Request)][0]

            client_ip = request.ip
            bandchain_params = get_bandchain_params(request.headers)

            if db:
                verify_error_type = VerifyErrorType.ERROR_VERIFICATION
                if e.message[0:19] == "wrong datasource_id":
                    verify_error_type = VerifyErrorType.UNSUPPORTED_DS_ID

                db.Report(
                    user_ip=client_ip,
                    reporter_address=bandchain_params.get("reporter", None),
                    validator_address=bandchain_params.get("validator", None),
                    request_id=bandchain_params.get("request_id", None),
                    external_id=bandchain_params.get("external_id", None),
                    from_ds_id=bandchain_params.get("data_source_id", None),
                    verify_error_type=verify_error_type,
                    verify_response_code=e.status_code,
                    verify_error_msg=e.message,
                ).save()

            raise e

    return wrapper_collect_verify_data


def collect_request_data(func, db: DB = None):
    @functools.wraps(func)
    async def wrapper_collect_request_data(*args, **kwargs):
        try:
            request = [arg for arg in args if isinstance(arg, Request)][0]
            client_ip = request.ip
            bandchain_params = get_bandchain_params(request.headers)

            res = await func(*args, **kwargs)

            if db:
                db.Report(
                    user_ip=client_ip,
                    reporter_address=bandchain_params.get("reporter", None),
                    validator_address=bandchain_params.get("validator", None),
                    request_id=bandchain_params.get("request_id", None),
                    external_id=bandchain_params.get("external_id", None),
                    from_ds_id=bandchain_params.get("data_source_id", None),
                    provider_response_code=res.status_code,
                ).save()

            return res

        except SanicException as e:
            print(f"SanicException 1 {e.status_code}")

            if db:
                db.Report(
                    user_ip=client_ip,
                    reporter_address=bandchain_params.get("reporter", None),
                    validator_address=bandchain_params.get("validator", None),
                    request_id=bandchain_params.get("request_id", None),
                    external_id=bandchain_params.get("external_id", None),
                    from_ds_id=bandchain_params.get("data_source_id", None),
                    provider_response_code=e.status_code,
                    provider_error_msg=e.message,
                ).save()
            raise e

    return wrapper_collect_request_data
