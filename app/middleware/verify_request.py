from datetime import datetime

from fastapi import HTTPException
from httpx import AsyncClient
from starlette.requests import Request
from starlette.types import ASGIApp, Scope, Receive, Send

from app.report.db import DB
from app.report.models import VerifyReport
from app.utils.helper import (
    add_max_delay_param,
    get_bandchain_params,
)
from app.utils.types import VerifyErrorType


class VerifyRequestMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        verify_url: str,
        max_verification_delay: int,
        allowed_data_source_ids: list[int],
        report_db: DB = None,
    ) -> None:
        self.app = app
        self.verify_url = verify_url
        self.max_verification_delay = max_verification_delay
        self.report_db = report_db
        self.client = AsyncClient()
        self.allowed_ds_ids = allowed_data_source_ids

    def report(self, report: VerifyReport):
        if self.report_db:
            self.report_db.save(report)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            # Setup report
            report = VerifyReport(
                response_code=200,
                created_at=datetime.utcnow(),
            )
            try:
                # Get the request from scope
                request = Request(scope)

                # Check if request is valid from verify endpoint
                res = await self.client.get(
                    self.verify_url,
                    headers=add_max_delay_param(get_bandchain_params(request.headers), self.max_verification_delay),
                )
                res.raise_for_status()
                body = res.json()

                # Attempt to parse response from verify endpoint, if not possible, raise error and save report
                try:
                    is_delay = bool(body["is_delay"])
                    data_source_id = int(body["data_source_id"])
                except (KeyError, ValueError) as e:
                    report.response_code = res.status_code
                    report.error_type = "Invalid response from verify endpoint"
                    report.error_msg = str(e)
                    raise HTTPException(status_code=500, detail="Invalid response from verify server")
                finally:
                    self.report(report)

                # Check if request is in allowed data source ids, if not, raise error and save report
                if data_source_id not in self.allowed_ds_ids:
                    report.response_code = 401
                    report.error_type = VerifyErrorType.UNSUPPORTED_DS_ID.value
                    report.error_msg = f"Data source id {data_source_id} is not in allowed set: {self.allowed_ds_ids}"
                    self.report(report)
                    raise HTTPException(status_code=401, detail="Data source is not allowed")

                report.is_delay = is_delay
                # If request is not delayed, return response from request
                await self.app(scope, receive, send)
                return
            except Exception as e:
                report.response_code = 500
                report.error_type = "Internal server error"
                report.error_msg = f"{e.__class__.__name__}: {(str(e))}"
                self.report(report)
                raise HTTPException(status_code=500, detail="Internal server error")

        # Do nothing if the scope is not http.
        await self.app(scope, receive, send)
