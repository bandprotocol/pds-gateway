import functools
import json
from bson import json_util

from sanic import Request, response
from sanic.exceptions import SanicException

from app.utils.helper import get_bandchain_params_with_type
from app.report.db import DB, Report, VerifyErrorType, Verify, ProviderResponse
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
                    verify_error = e.context.get("verify_error")
                    if verify_error is not None:
                        verify_error = VerifyErrorType.ERROR_VERIFICATION

                    self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            data_source_id=bandchain_params.get("data_source_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            verify=Verify(
                                response_code=int(e.status_code),
                                error_type=verify_error.value,
                                error_msg=e.args[0],
                            ).dict(),
                        )
                    )

                raise SanicException(f"{e}", status_code=e.status_code)

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
                    self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            data_source_id=bandchain_params.get("data_source_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            cached_data=res_json.get("cached_data", False),
                            verify=request.ctx.verify.dict(),
                            provider_response=ProviderResponse(response_code=res.status).dict(),
                        )
                    )

                return res

            except SanicException as e:
                if self.db:
                    self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            data_source_id=bandchain_params.get("data_source_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            verify=request.ctx.verify.dict(),
                            provider_response=ProviderResponse(
                                response_code=e.status_code,
                                error_msg=e.args[0],
                            ).dict(),
                        )
                    )

                raise e

        return wrapper_collect_request_data


class GetStatus:
    def __init__(self, config, db: DB = None):
        self.config = config
        self.db = db

    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper_get_status(*args, **kwargs):
            res = func(*args, **kwargs)
            if self.db:
                try:
                    latest_request = await self.db.get_latest_request_info()
                    latest_failed_request = await self.db.get_latest_verify_failed()
                    res_dict = {
                        "gateway_info": {
                            "allow_data_source_ids": self.config.ALLOWED_DATA_SOURCE_IDS,
                            "max_delay_verification": self.config.MAX_DELAY_VERIFICATION,
                        },
                        "latest_request": latest_request,
                        "latest_failed_request": latest_failed_request,
                    }

                    res = response.json(res_dict, default=str)
                except Exception as e:
                    raise SanicException(f"{e}", status_code=500)
            return res

        return wrapper_get_status
