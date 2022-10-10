from sanic import Sanic
from typing import Dict
from importlib import import_module
import httpx


def get_app():
    return Sanic.get_app()


def get_bandchain_params(headers: Dict[str, str]) -> Dict[str, str]:
    params = {k.lower()[5:]: v for k, v in headers.items() if k.lower().startswith("band_")}
    return params


def get_bandchain_params_with_type(headers: Dict[str, str]) -> Dict[str, str]:
    params = {}
    params_type_int = ["request_id", "from_ds_id", "external_id"]
    for k, v in headers.items():
        if k.lower().startswith("band_"):
            band_arg = k.lower()[5:]
            if band_arg in params_type_int:
                params[band_arg] = int(v)
            else:
                params[band_arg] = v

    return params


def get_band_signature_hash(headers: Dict[str, str]) -> str:
    return hash(headers["BAND_SIGNATURE"])


def add_params_config(params: Dict[str, str]) -> Dict[str, str]:
    params["max_delay"] = get_app().config.MAX_DELAY_VERIFICATION
    return params


def get_adapter(type: str, name: str):
    module = import_module(f"app.adapter.{type}.{name}".lower())
    AdapterClass = getattr(module, "".join([part.capitalize() for part in name.split("_")]))
    return AdapterClass()


async def verify_request(headers: Dict[str, str]) -> str:
    client = httpx.AsyncClient()

    res = await client.get(
        url=get_app().config.VERIFY_REQUEST_URL,
        params=add_params_config(get_bandchain_params(headers)),
    )

    # check result of request
    if res.status_code != 200:
        raise Exception(res.text)

    body = res.json()
    # check node delay
    if body.get("is_delay", False):
        # TODO: add logic
        pass

    return body.get("data_source_id", None)


def verify_data_source_id(data_source_id: str) -> bool:
    if data_source_id not in get_app().config.ALLOWED_DATA_SOURCE_IDS:
        raise Exception(
            f"wrong datasource_id. expected {get_app().config.ALLOWED_DATA_SOURCE_IDS}, got {data_source_id}."
        )
    return True
