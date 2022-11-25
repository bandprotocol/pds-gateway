import json
import functools

from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException

from app import config
from app.utils.helper import get_bandchain_params_with_type
from app.report.db import DB
from app.report.models import Report, Verify, ProviderResponse


class CollectVerifyData:
    def __init__(self, db: DB = None):
        self.db = db

    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper_collect_verify_data(*args, **kwargs):

            try:
                res = await func(*args, **kwargs)

            except HTTPException as e:
                if self.db:
                    request = kwargs.get("request")

                    client_ip = request.client.host
                    bandchain_params = get_bandchain_params_with_type(request.headers)

                    self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            data_source_id=bandchain_params.get("data_source_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            verify=Verify(
                                response_code=e.status_code,
                                error_type=e.detail["verify_error_type"],
                                error_msg=e.detail["error_msg"],
                            ).to_dict(),
                        )
                    )

                raise e

            return res

        return wrapper_collect_verify_data


class CollectRequestData:
    def __init__(self, db: DB = None):
        self.db = db

    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper_collect_request_data(*args, **kwargs):
            try:
                res = await func(*args, **kwargs)

                if self.db:
                    request = kwargs.get("request")
                    verify = kwargs.get("verify")
                    client_ip = request.client.host
                    bandchain_params = get_bandchain_params_with_type(request.headers)

                    self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            data_source_id=bandchain_params.get("data_source_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            cached_data=res.get("cached_data", False),
                            verify=verify.to_dict(),
                            provider_response=ProviderResponse(response_code=200).to_dict(),
                        )
                    )

            except HTTPException as e:
                if self.db:
                    request = kwargs.get("request")
                    verify = kwargs.get("verify")
                    client_ip = request.client.host
                    bandchain_params = get_bandchain_params_with_type(request.headers)

                    self.db.save_report(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            data_source_id=bandchain_params.get("data_source_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            cached_data=False,
                            verify=verify.to_dict(),
                            provider_response=ProviderResponse(
                                response_code=e.status_code, error_msg=e.detail["error_msg"]
                            ).to_dict(),
                        )
                    )

                raise e

            return res

        return wrapper_collect_request_data


class GetStatus:
    def __init__(self, settings: config.Settings, db: DB = None):
        self.settings = settings
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
                            "allow_data_source_ids": self.settings.ALLOWED_DATA_SOURCE_IDS,
                            "max_delay_verification": self.settings.MAX_DELAY_VERIFICATION,
                        },
                        "latest_request": latest_request,
                        "latest_failed_request": latest_failed_request,
                    }

                    res = res_dict
                except Exception as e:
                    raise HTTPException(f"{e}", status_code=500)
            return res

        return wrapper_get_status
