import functools
from sanic.exceptions import SanicException
from sanic.request import Request

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
                            from_ds_id=bandchain_params.get("from_ds_id", None),
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
                            from_ds_id=bandchain_params.get("from_ds_id", None),
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
                            from_ds_id=bandchain_params.get("from_ds_id", None),
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
