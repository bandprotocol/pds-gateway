import re
from typing import List, Mapping, Any, TypedDict, Optional

from httpx import AsyncClient, HTTPStatusError

from app.exceptions import VerificationFailedError
from app.utils.types import VerifyErrorType


def get_bandchain_params(headers: Mapping[str, Any]) -> dict[str, Any]:
    """Gets BandChain parameters from the header.

    Args:
        headers: Header to extract BandChain parameters from.

    Returns:
        A dictionary containing BandChain's parameters
    """

    return {r.group(1): v for k, v in headers.items() if (r := re.search("^band_(.+)", k.lower()))}


def get_bandchain_params_with_type(headers: Mapping[str, Any]) -> dict[str, Any]:
    """Gets BandChain parameters with type from the header.

    Args:
        headers: Header to extract BandChain parameters from.

    Returns:
        A dictionary containing BandChain's parameters
    """
    params = get_bandchain_params(headers)
    for k, v in params.items():
        if k in ["request_id", "data_source_id", "external_id"]:
            params[k] = int(v)
    return params


def get_band_signature_hash(headers: Mapping[str, Any]) -> int:
    """Gets the hash of the band signature from a header

    Args:
        headers: Header containing band signature

    Returns:
        Hash of band signature
    """
    return hash(headers["BAND_SIGNATURE"])


def add_max_delay_param(params: dict[str, Any], max_delay_verification: int) -> dict[str, Any]:
    """Add a 'max_delay' parameter to the input dictionary of parameters and return the updated dictionary.

    Args:
        params: A dictionary of parameters as key-value pairs.
        max_delay_verification: Maximum node delay in request ID.

    Returns:
        A new dictionary with the original parameters and the 'max_delay' parameter added.
    """
    params["max_delay"] = str(max_delay_verification)
    return params


async def verify_request_from_bandchain(
    headers: Mapping[str, str],
    verify_request_url: str,
    max_delay_verification: int,
) -> TypedDict("Verify", {"is_delay": bool, "data_source_id": Optional[int]}):
    """Verifies if the request came from BandChain

    Args:
        headers: Request header
        verify_request_url: URL to verify request from
        max_delay_verification: Maximum node delay in request ID

    Returns:
        A dictionary containing the data source id and is delay status.
        An example can be seen here:
        {
            "is_delay": false,
            "data_source_id": 1
        }

    Raises:
        HttpException: When an error occurs
    """
    try:
        async with AsyncClient() as client:
            params = add_max_delay_param(get_bandchain_params(headers), max_delay_verification)
            res = await client.get(url=verify_request_url, params=params)

            # Raises for non-2xx codes
            res.raise_for_status()

            # Gets body
            body = res.json()

            return {"is_delay": body.get("is_delay", False), "data_source_id": body.get("data_source_id", None)}
    except HTTPStatusError as e:
        status_code = e.response.status_code
        verify_error_type = VerifyErrorType.UNKNOWN.value
        if re.match(r"4[\d]{2}", str(status_code)):
            verify_error_type = VerifyErrorType.FAILED_VERIFICATION.value
        raise VerificationFailedError(
            status_code=status_code,
            error_type=verify_error_type,
        )


def is_data_source_id_allowed(data_source_id: int, allowed_data_source_ids: List[int]) -> bool:
    """Checks whether the given data source ID is allowed to send a request.

    Args:
        data_source_id: The ID of the data source sending the request.
        allowed_data_source_ids: A list of allowed data source IDs.

    Returns:
        bool: Returns True if the data source ID is in the allowed data source IDs list, and False otherwise.
    """
    return data_source_id in allowed_data_source_ids
