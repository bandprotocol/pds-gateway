from sanic import Sanic
from typing import Dict
from importlib import import_module
import httpx


def get_app():
    return Sanic.get_app()


def get_bandchain_params(headers: Dict[str, str]) -> Dict[str, str]:
    params = {k.lower()[5:]: v for k, v in headers.items() if k.lower().startswith("band_")}
    return params


def add_params_config(params: Dict[str, str]) -> Dict[str, str]:
    params["max_delay"] = get_app().config["MAX_DELAY_VERIFICATION"]
    return params


def get_adapter(type: str, name: str):
    module = import_module(f"app.adapter.{type}.{name}".lower())
    AdapterClass = getattr(module, "".join([part.capitalize() for part in name.split("_")]))
    return AdapterClass()


async def verify_request(headers: Dict[str, str]) -> str:
    client = httpx.AsyncClient()
    res = await client.get(
        url=get_app().config["VERIFY_REQUEST_URL"],
        params=add_params_config(get_bandchain_params(headers)),
    )
    body = res.json()

    # check result of request
    if res.status_code != 200:
        raise Exception(body)

    # check node delay
    if body.get("data_source_id", False) == True:
        # TODO: add logic
        pass

    return body.get("data_source_id", None)


def verify_data_source_id(data_source_id: str) -> bool:
    if data_source_id not in get_app().config["ALLOWED_DATA_SOURCE_IDS"]:
        raise Exception(
            f"wrong datasource_id. expected {get_app().config['ALLOWED_DATA_SOURCE_IDS']}, got {data_source_id}."
        )
    return True
