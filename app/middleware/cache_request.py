import asyncio
import json
import time

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Scope, Receive, Send, Message

from app.utils.cache import Cache
from app.utils.helper import get_bandchain_params_with_type


class RequestCacheMiddleware:
    def __init__(self, app: ASGIApp, cache: Cache, timeout: int) -> None:
        self.app = app
        self.cache = cache
        self.timeout = timeout

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def cache_response(message: Message) -> None:
            """Cache the response from the request.

            Args:
                message: Message object.
            """
            if message["type"] == "http.response.body":
                self.cache.set(key, {"state": "success", "data": json.loads(message["body"].decode())})
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
            if self.cache.get(key):
                timeout_timestamp = time.time() + self.timeout

                # While the key is in the cache or response timeout has not been exceeded, 
                # check the state of the response and return the cached response.
                while cached := self.cache.get(key) or time.time() < timeout_timestamp:
                    match cached["state"]:
                        case "success":
                            # If the state is success, return the cached response.
                            await JSONResponse(content=cached["data"], status_code=200)(scope, receive, send)
                            return
                        case "failed":
                            # If the state is failed, attempt to request again.
                            break
                        case "pending":
                            # If the state is pending, wait for 0.1 seconds.
                            await asyncio.sleep(0.1)
                            pass
            else:
                # If the key is not in the cache, set the state to pending and cache it.
                self.cache.set(key, {"state": "pending", "data": None})

            try:
                await self.app(scope, receive, cache_response)
                return
            except HTTPException as e:
                self.cache.set(key, {"state": "failed", "data": None})
                raise e

        # Do nothing if the scope is not http.
        await self.app(scope, receive, send)
