import functools
from sanic.exceptions import SanicException
from sanic.request import Request

from app.utils.helper import get_bandchain_params_with_type
from app.report.db import DB, VerifyErrorType, Report
from app.report.helper import bytes_to_json


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
                bandchain_params = get_bandchain_params_with_type(request.headers)

                if self.db:
                    verify_error_type = VerifyErrorType.ERROR_VERIFICATION
                    if e.message[0:19] == "wrong datasource_id":
                        verify_error_type = VerifyErrorType.UNSUPPORTED_DS_ID

                    await self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            from_ds_id=bandchain_params.get("from_ds_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            verify_error_type=verify_error_type,
                            verify_response_code=int(e.status_code),
                            verify_error_msg=e.message,
                        )
                    )

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
                bandchain_params = get_bandchain_params_with_type(request.headers)

                res = await func(*args, **kwargs)

                if self.db:
                    res_json = bytes_to_json(res.body)
                    await self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            from_ds_id=bandchain_params.get("from_ds_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            cached_data=res_json.get("cached_data", False),
                            provider_response_code=res.status,
                        )
                    )

                return res

            except SanicException as e:
                if self.db:
                    await self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            from_ds_id=bandchain_params.get("from_ds_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            provider_response_code=res.status,
                            provider_error_msg=e.message,
                        )
                    )

                raise e

        return wrapper_collect_request_data
