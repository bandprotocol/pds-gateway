from typing import Dict, List, Union
from importlib import import_module
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import httpx

from app.utils.exception import UnsupportedDsException
from app.utils.types import VerifyErrorType, ErrorResponse


def get_bandchain_params(headers: Dict[str, str]) -> Dict[str, str]:
    params = {k.lower()[5:]: v for k, v in headers.items() if k.lower().startswith("band_")}
    return params


def get_bandchain_params_with_type(headers: Dict[str, str]) -> Dict[str, str]:
    params = {}
    params_type_int = ["request_id", "data_source_id", "external_id"]
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


def add_params_config(params: Dict[str, str], max_delay_verification: Union[int, str]) -> Dict[str, str]:
    params["max_delay"] = str(max_delay_verification)
    return params


def get_adapter(type: str, name: str):
    module = import_module(f"adapter.{type}.{name}".lower())
    AdapterClass = getattr(module, "".join([part.capitalize() for part in name.split("_")]))
    return AdapterClass()


async def verify_request(
    headers: Dict[str, str], verify_request_url: str, max_delay_verification: Union[int, str]
) -> dict:
    client = httpx.AsyncClient()

    res = await client.get(
        url=verify_request_url,
        params=add_params_config(get_bandchain_params(headers), str(max_delay_verification)),
    )

    # check result of request
    res.raise_for_status()

    body = res.json()
    # check node delay
    if body.get("is_delay", False):
        # TODO: add logic
        pass

    return {"is_delay": body.get("is_delay", False), "data_source_id": body.get("data_source_id", None)}


def verify_data_source_id(data_source_id: str, allowed_data_source_ids: List[str]) -> bool:
    if data_source_id not in allowed_data_source_ids:
        raise UnsupportedDsException(allowed_data_source_ids=allowed_data_source_ids, data_source_id=data_source_id)

    return True


def json_verify_error_response(status_code: int, verify_error_type: VerifyErrorType, msg: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "error_response": jsonable_encoder(
                ErrorResponse(
                    verify_error_type=verify_error_type.value,
                    msg=msg,
                )
            )
        },
    )
