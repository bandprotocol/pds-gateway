import pytest
from fastapi import HTTPException
from httpx import Request, Response
from pytest_httpx import HTTPXMock

from app.exceptions import VerificationFailedError
from app.utils.helper import (
    add_max_delay_param,
    get_bandchain_params,
)


class MockConfig:
    VERIFY_REQUEST_URL = "http://localhost.example"
    ALLOWED_DATA_SOURCE_IDS = [1]
    CACHE_SIZE = 1000
    TTL_TIME = "10m"
    MAX_DELAY_VERIFICATION = 5


mock_headers = {
    "NOT_BAND": "0",
    "BAND_CHAIN_ID": "bandchain",
    "BAND_VALIDATOR": "bandcoolvalidator",
    "BAND_REQUEST_ID": "1",
    "BAND_EXTERNAL_ID": "1",
    "BAND_DATA_SOURCE_ID": "1",
    "BAND_REPORTER": "bandcoolreporter",
    "BAND_SIGNATURE": "coolsignature",
}


def test_get_bandchain_params():
    params = get_bandchain_params(mock_headers)

    assert params == {
        "chain_id": "bandchain",
        "validator": "bandcoolvalidator",
        "request_id": "1",
        "external_id": "1",
        "data_source_id": "1",
        "reporter": "bandcoolreporter",
        "signature": "coolsignature",
    }


def test_add_max_delay_param():
    params = add_max_delay_param(
        {
            "chain_id": "bandchain",
            "validator": "bandcoolvalidator",
            "request_id": "1",
            "external_id": "1",
            "reporter": "bandcoolreporter",
            "signature": "coolsignature",
        },
        10,
    )

    assert params == {
        "chain_id": "bandchain",
        "validator": "bandcoolvalidator",
        "external_id": "1",
        "request_id": "1",
        "reporter": "bandcoolreporter",
        "signature": "coolsignature",
        "max_delay": "10",
    }
