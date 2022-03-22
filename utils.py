from sanic import Sanic
from config import config
import os
import httpx


def get_bandchain_endpoint() -> str:
    url = config["BANDCHAIN_REST_ENDPOINT"]
    return url


def get_bandchain_params(headers: object) -> object:

    params = {
        k.lower()[5:]: v for k, v in headers.items() if k.lower().startswith("band_")
    }

    return params


def get_endpoint_headers(headers: object) -> object:

    params = {k: v for k, v in headers.items() if k.lower().startswith("band_")}

    if config["HEADER_KEY"]:
        params[config["HEADER_KEY"]] = config["HEADER_VALUE"]

    return params


async def verify_requester(headers):
    url = get_bandchain_endpoint()
    params = get_bandchain_params(headers)

    async with httpx.AsyncClient() as client:
        res = await client.get(url=f"{url}/oracle/v1/verify_request", params=params)

    return res
