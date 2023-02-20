import functools
from typing import Optional, Any, Callable

from fastapi import HTTPException

from app.report.db import DB
from app.report.models import Report, Verify, ProviderResponse
from app.utils.helper import get_bandchain_params_with_type


class CollectVerifyData:
    """A decorator that collects verify data from requests, and saves a corresponding reports to a database."""

    def __init__(self, db: Optional[DB] = None) -> None:
        """Initializes a CollectVerifyData object with an optional database.

        Args:
            db : An optional database for saving reports.
        """
        self.db = db

    def __call__(self, func: Callable):
        @functools.wraps(func)
        async def wrapper_collect_verify_data(*args, **kwargs):
            try:
                res = await func(*args, **kwargs)
            except HTTPException as e:
                if self.db:
                    request = kwargs.get("request")

                    client_ip = request.client.host
                    bandchain_params = get_bandchain_params_with_type(request.headers)

                    error_details: Any = e.detail
                    self.db.save(
                        Report(
                            user_ip=client_ip,
                            reporter_address=bandchain_params.get("reporter", None),
                            validator_address=bandchain_params.get("validator", None),
                            request_id=bandchain_params.get("request_id", None),
                            data_source_id=bandchain_params.get("data_source_id", None),
                            external_id=bandchain_params.get("external_id", None),
                            verify=Verify(
                                response_code=e.status_code,
                                error_type=error_details["verify_error_type"],
                                error_msg=error_details["error_msg"],
                            ).to_dict(),
                        )
                    )
                raise e

            return res

        return wrapper_collect_verify_data


class CollectRequestData:
    """A decorator that collects request data from requests and saves a corresponding to a database."""

    def __init__(self, db: Optional[DB] = None):
        """Inits CollectVerifyData with an optional db.

        Args:
            db: Report database class.
        """
        self.db = db

    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper_collect_request_data(*args, **kwargs):
            cached_data: bool = False
            provider_response: Optional[dict] = None
            try:
                res = await func(*args, **kwargs)

                cached_data = res.get("cached_data", False)
                provider_response = ProviderResponse(response_code=200).to_dict()
            except HTTPException as e:
                error_detail: Any = e.detail

                provider_response = ProviderResponse(
                    response_code=e.status_code, error_msg=error_detail["error_msg"]
                ).to_dict()

                raise e
            finally:
                if self.db:
                    request = kwargs.get("request")
                    verify = kwargs.get("verify")
                    client_ip = request.client.host

                    bandchain_params = get_bandchain_params_with_type(request.headers)

                    report = Report(
                        user_ip=client_ip,
                        reporter_address=bandchain_params.get("reporter", None),
                        validator_address=bandchain_params.get("validator", None),
                        request_id=bandchain_params.get("request_id", None),
                        data_source_id=bandchain_params.get("data_source_id", None),
                        external_id=bandchain_params.get("external_id", None),
                        cached_data=cached_data,
                        verify=verify.to_dict(),
                        provider_response=provider_response,
                    )
                    self.db.save(report)

            return res

        return wrapper_collect_request_data
