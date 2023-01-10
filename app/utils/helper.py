from httpx import AsyncClient, HTTPStatusError
from fastapi import HTTPException
from typing import Dict, List, Union

from app.utils.types import VerifyErrorType


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


def add_params_config(params: Dict[str, str], max_delay_verification: int) -> Dict[str, str]:
    params["max_delay"] = str(max_delay_verification)
    return params


async def verify_request(headers: Dict[str, str], verify_request_url: str, max_delay_verification: int) -> dict:
    try:
        client = AsyncClient()

        res = await client.get(
            url=verify_request_url,
            params=add_params_config(get_bandchain_params(headers), max_delay_verification),
        )

        # check result of request
        res.raise_for_status()

        body = res.json()
        # check node delay
        if body.get("is_delay", False):
            # TODO: add logic to retry or reject request
            pass

        return {"is_delay": body.get("is_delay", False), "data_source_id": body.get("data_source_id", None)}
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"verify_error_type": VerifyErrorType.FAILED_VERIFICATION.value, "error_msg": f"{e}"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"verify_error_type": VerifyErrorType.SERVER_ERROR.value, "error_msg": f"{e}"}
        )


def is_allow_data_source_id(data_source_id: str, allowed_data_source_ids: List[int]) -> bool:
    return data_source_id in allowed_data_source_ids
