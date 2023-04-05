import json

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Scope, Receive, Send, Message

from app.utils.cache import Cache
from app.utils.helper import get_bandchain_params_with_type


class RequestCacheMiddleware:
    def __init__(self, app: ASGIApp, cache: Cache) -> None:
        self.app = app
        self.cache = cache

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def cache_response(message: Message) -> None:
            """Cache the response from the request.

            Args:
                message: Message object.
            """
            if message["type"] == "http.response.body":
                self.cache.set(key, json.loads(message["body"].decode()))
            await send(message)

        if scope["type"] == "http":
            # Get request_id and external_id from the request header.
            request = Request(scope)
            bandchain_params = get_bandchain_params_with_type(request.headers)
            rid = bandchain_params.get("request_id", None)
            eid = bandchain_params.get("external_id", None)

            # If request_id or external_id is None, return the response from the request.
            if rid is None or eid is None:
                await self.app(scope, receive, send)
                return

            # If the key is not in the cache, get the response from the request and cache it.
            key = hash((rid, eid))
            if data := self.cache.get(key):
                # If the key is in the cache, return the cached response.
                await JSONResponse(content=data, status_code=200)(scope, receive, send)
                return

            # If the key is not in the cache, get the response from the request and cache it.
            try:
                await self.app(scope, receive, cache_response)
                return
            except HTTPException as e:
                raise e
