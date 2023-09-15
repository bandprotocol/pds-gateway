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
