import pytest
from fastapi import HTTPException
from httpx import Request, Response
from pytest_httpx import HTTPXMock

from app.utils.helper import (
    add_max_delay_param,
    get_bandchain_params,
    is_data_source_id_allowed,
    verify_request_from_bandchain,
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


def test_is_allow_data_source_id():
    assert is_data_source_id_allowed(1, [1, 2])
    assert not is_data_source_id_allowed(3, [1, 2])


@pytest.mark.asyncio
async def test_verify_request_from_bandchain_success(httpx_mock: HTTPXMock):
    expected = {"is_delay": False, "data_source_id": "226"}

    # mock response
    def custom_response(_: Request):
        return Response(
            status_code=200,
            json={
                "chain_id": "band-laozi-testnet6",
                "validator": "bandvaloper1knxukd35rm4cmthkdgzkfaf8lrhpexv752l7mh",
                "request_id": "2728447",
                "external_id": "2",
                "data_source_id": "226",
                "is_delay": False,
            },
        )

    httpx_mock.add_callback(custom_response)

    verified = await verify_request_from_bandchain(mock_headers, "https://www.mock-url.com", 0)

    assert verified == expected


@pytest.mark.asyncio
async def test_verify_request_from_bandchain_failed(httpx_mock: HTTPXMock):
    # mock response
    def custom_response(_: Request):
        return Response(
            status_code=500,
            content=b"server error",
        )

    httpx_mock.add_callback(custom_response)

    try:
        await verify_request_from_bandchain(mock_headers, "https://www.mock-url.com", 0)
    except HTTPException as e:
        assert e.status_code == 500
