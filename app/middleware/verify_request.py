import asyncio
from datetime import datetime
from typing import Any

from httpx import AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Scope, Receive, Send

from app.exceptions import VerificationFailedError
from app.report.db import DB
from app.report.models import VerifyReport
from app.utils.helper import (
    add_max_delay_param,
    get_bandchain_params,
)


class VerifyRequestMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        verify_urls: list[str],
        max_verification_delay: int,
        allowed_data_source_ids: list[int],
        report_db: DB = None,
    ) -> None:
        self.app = app
        self.verify_urls = verify_urls
        self.max_verification_delay = max_verification_delay
        self.report_db = report_db
        self.client = AsyncClient()
        self.allowed_ds_ids = allowed_data_source_ids

    def report(self, report: VerifyReport):
        if self.report_db:
            self.report_db.save(report)

    @staticmethod
    def parse_verify_response(body: dict[str, Any]) -> (bool, int):
        try:
            is_delay = bool(body["is_delay"])
            data_source_id = int(body["data_source_id"])
            return is_delay, data_source_id
        except (KeyError, ValueError):
            raise VerificationFailedError(
                status_code=500,
                error="Failed to parse successful response from verify endpoint",
                details=f"Verify endpoint returned a successful response but failed to parse the content: {body}",
            )

    def check_request_validity(self, ds_id: int) -> None:
        if ds_id not in self.allowed_ds_ids:
            raise VerificationFailedError(
                status_code=401,
                error="Data source is not allowed",
                details=f"Data source id {ds_id} is not in allowed set: {self.allowed_ds_ids}",
            )

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] == "http":
            # Setup report
            report = VerifyReport(
                response_code=200,
                created_at=datetime.utcnow(),
            )
            try:
                # Get the request from scope
                request = Request(scope)
                params = add_max_delay_param(
                    get_bandchain_params(request.headers), self.max_verification_delay
                )

                # Verify against all URLs concurrently
                results = await asyncio.gather(
                    *[self._verify_url(url, params) for url in self.verify_urls],
                    return_exceptions=True,
                )

                # Process results: separate successful responses from errors
                valid_results: list[tuple[dict[str, Any], int]] = []
                errors: list[str] = []

                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        url = result.request.url
                        # Reconstruct URL without query parameters to avoid leaking signatures
                        port = f":{url.port}" if url.port is not None else ""
                        sanitized_url = f"{url.scheme}://{url.host}{port}{url.path}"
                        status_code = (
                            result.response.status_code
                            if result.response is not None
                            else "unknown"
                        )
                        errors.append(
                            f"{self.verify_urls[i]}: HTTPStatusError: "
                            f"status_code={status_code}, url={sanitized_url}"
                        )
                    else:
                        valid_results.append((result, i))

                if not valid_results:
                    raise VerificationFailedError(
                        status_code=500,
                        error="All verification requests failed",
                        details=(
                            "; ".join(errors)
                            if errors
                            else "Failed to verify request against all verify nodes"
                        ),
                    )

                is_delay: bool | None = None
                ds_id: int | None = None
                errors = []

                # Find result: prefer any with is_delay=false, otherwise use first one
                for result, _ in valid_results:
                    try:
                        is_delay, ds_id = self.parse_verify_response(result)
                    except VerificationFailedError as e:
                        # If parsing fails, log the error but continue processing other results
                        errors.append(
                            f"Failed to parse response from verify endpoint: {result}, error: {e.details}"
                        )
                        continue
                    # If any response indicates no delay, we can break early and use that result
                    if not is_delay:
                        break

                # If we couldn't parse any successful response, treat it as a failure
                if is_delay is None or ds_id is None:
                    raise VerificationFailedError(
                        status_code=500,
                        error="Failed to parse any successful response from verify endpoints",
                        details=(
                            "; ".join(errors)
                            if errors
                            else "All verification responses were malformed or invalid"
                        ),
                    )

                # Check if request is in allowed data source ids, if not, raise error and save report
                self.check_request_validity(ds_id)

                # TODO: handle case for is_delay
                report.is_delay = is_delay
                # If request is not delayed, return response from request
                await self.app(scope, receive, send)
                return
            except VerificationFailedError as e:
                report.response_code = e.status_code
                report.error_type = e.error
                report.error_msg = e.details
            except Exception as e:
                report.response_code = 500
                report.error_type = "Internal Server Error"
                report.error_msg = f"{e.__class__.__name__}: {(str(e))}"
            finally:
                # If response code is not 200, return error response
                if report.response_code != 200:
                    await JSONResponse(
                        content={"error": report.error_type},
                        status_code=report.response_code,
                    )(scope, receive, send)

                # Save the report if report_db is provided
                if self.report_db:
                    self.report(report)
        else:
            # Do nothing if the scope is not http.
            await self.app(scope, receive, send)

    async def _verify_url(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Verify against a single URL and return the response body."""
        res = await self.client.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json()
