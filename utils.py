from sanic import response
from sanic import Sanic
from config import config
import os
import httpx


def get_bandchain_rest_endpoint() -> str:
    base_url = config["BANDCHAIN_REST_ENDPOINT"]

    if base_url is None:
        return response.text("no bandchain endpoint")

    return base_url + "/oracle/v1/verify_request"


def get_bandchain_headers(headers) -> object:

    params = {
        k.lower()[5:]: v for k, v in headers.items() if k.lower().startswith("band_")
    }

    return params


def get_cache_key(headers):
    return ":".join([v for k, v in headers.items() if k.lower().startswith("band_")])


async def verify_requester(headers):
    url = get_bandchain_rest_endpoint()
    params = get_bandchain_headers(headers)

    async with httpx.AsyncClient() as client:
        res = await client.get(url=url, params=params)

    return res
