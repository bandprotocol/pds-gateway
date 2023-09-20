import json

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Scope, Receive, Send, Message

from app.utils.cache import Cache
from app.utils.helper import get_band_signature_hash


class SignatureCacheMiddleware:
    """A middleware that collects request data from requests and saves a corresponding to a database."""

    def __init__(self, app: ASGIApp, cache: Cache) -> None:
        """Initialize the middleware.

        Args:
            app: ASGI application.
            cache: Cache object.
        """
        self.app = app
        self.cache = cache

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def cache_response(message: Message):
            """Cache the response from the request.

            Args:
                message: Message object.
            """
            if message["type"] == "http.response.body":
                self.cache.set(key, json.loads(message["body"].decode()))
            await send(message)

        if scope["type"] == "http":
            # Get the request object from the scope.
            request = Request(scope)

            # If the key is not in the cache, get the response from the request and cache it.
            key = get_band_signature_hash(request.headers)
            if data := self.cache.get(key):
                # If the key is in the cache, return the cached response.
                await JSONResponse(content=data, status_code=200)(scope, receive, send)
                return

            # If the key is not in the cache, continue.
            await self.app(scope, receive, cache_response)

        # Do nothing if the scope type is not http.
        else:
            await self.app(scope, receive, send)
