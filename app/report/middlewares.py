import sys
from functools import wraps
from typing import Optional, Any, Callable

from fastapi import HTTPException, Request

from app.config import Settings
from app.report.db import DB
from app.report.models import Report, Verify, ProviderResponse
from app.utils.helper import get_bandchain_params_with_type


class CollectRequestData:
    """A decorator that collects request data from requests and saves a corresponding to a database."""

    def __init__(self, db: Optional[DB] = None):
        """Inits CollectVerifyData with an optional db.

        Args:
            db: Report database class.
        """
        self.db = db

    def __call__(self, func: Callable[[Request, Verify, Settings], Any]):
        @wraps(func)
        async def wrapper_collect_request_data(request: Request, verify: Verify, settings: Settings):
            res = None

            try:
                if verify.response_code == 200:
                    res = await func(request, verify, settings)
            except HTTPException as e:
                raise e
            except Exception as e:
                raise e
            finally:
                if self.db:
                    _, exc_value, _ = sys.exc_info()

                    match exc_value:
                        case None:
                            provider_response = ProviderResponse(response_code=200)
                        case HTTPException() as e:
                            provider_response = ProviderResponse(response_code=e.status_code, error_msg=e.detail)
                        case _:
                            provider_response = None


                    client_ip = request.client.host
                    bandchain_params = get_bandchain_params_with_type(request.headers)

                    report = Report(
                        user_ip=client_ip,
                        reporter_address=bandchain_params.get("reporter", None),
                        validator_address=bandchain_params.get("validator", None),
                        request_id=bandchain_params.get("request_id", None),
                        data_source_id=bandchain_params.get("data_source_id", None),
                        external_id=bandchain_params.get("external_id", None),
                        cached_data=res.get("cached_data", False) if res is not None else None,
                        verify=verify,
                        provider_response=provider_response,
                    )
                    self.db.save(report)

            return res

        return wrapper_collect_request_data
