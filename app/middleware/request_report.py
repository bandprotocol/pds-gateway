from datetime import datetime
from starlette.requests import Request
from starlette.types import ASGIApp, Scope, Receive, Send

from app.report import DB
from app.report.models import RequestReport
from app.utils.helper import get_bandchain_params_with_type


class RequestReportMiddleware:
    """A middleware that collects request data from requests and saves a corresponding to a database.

    Attributes:
        app: ASGI application.
        db: Report database class.
    """

    def __init__(self, app: ASGIApp, db: DB) -> None:
        """Initialize the middleware.

        Args:
            app: ASGI application.
            db: Report database class.
        """
        self.app = app
        self.db = db

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request = Request(scope)
            bandchain_params = get_bandchain_params_with_type(request.headers)

            report = RequestReport(
                user_ip=request.client.host,
                reporter_address=bandchain_params.get("reporter", None),
                validator_address=bandchain_params.get("validator", None),
                request_id=bandchain_params.get("request_id", None),
                data_source_id=bandchain_params.get("data_source_id", None),
                external_id=bandchain_params.get("external_id", None),
                created_at=datetime.utcnow(),
            )

            await self.app(scope, receive, send)
            self.db.save(report)
        else:
            # Do nothing if the scope type is not http.
            await self.app(scope, receive, send)
