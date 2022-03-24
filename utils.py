from config import config
import httpx


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


async def verify_request(headers):
    params = get_bandchain_params(headers)

    async with httpx.AsyncClient() as client:
        res = await client.get(url=config["VERIFY_REQUEST_URL"], params=params)

    return res
