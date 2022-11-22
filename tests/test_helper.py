from genericpath import isdir
from os import listdir
from os.path import isfile, join
from pytest_httpx import HTTPXMock
import httpx
import pytest

from app.utils import helper


class MockConfig:
    VERIFY_REQUEST_URL = "http://localhost.example"
    ALLOWED_DATA_SOURCE_IDS = ["1"]
    CACHE_SIZE = 1000
    TTL_TIME = "10m"
    MAX_DELAY_VERIFICATION = "5"


mock_headers = {
    "BAND_CHAIN_ID": "bandchain",
    "BAND_VALIDATOR": "bandcoolvalidator",
    "BAND_REQUEST_ID": "1",
    "BAND_EXTERNAL_ID": "1",
    "BAND_DATA_SOURCE_ID": "1",
    "BAND_REPORTER": "bandcoolreporter",
    "BAND_SIGNATURE": "coolsignature",
}


def test_get_bandchain_params():
    params = helper.get_bandchain_params(mock_headers)

    assert params == {
        "chain_id": "bandchain",
        "validator": "bandcoolvalidator",
        "request_id": "1",
        "external_id": "1",
        "data_source_id": "1",
        "reporter": "bandcoolreporter",
        "signature": "coolsignature",
    }


def test_add_params_config():
    params = helper.add_params_config(
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


def test_get_adapter():
    path = "./adapter"
    standards = [f for f in listdir(path) if isdir(join(path, f)) and not f.startswith("__")]
    for standard in standards:
        adapters = [
            f.replace(".py", "")
            for f in listdir(join(path, standard))
            if isfile(join(path, standard, f)) and not f.startswith("__")
        ]

        for adapter in adapters:
            helper.get_adapter(standard, adapter + "")


def test_verify_data_source_id_success():
    result = helper.verify_data_source_id("1", ["1", "2"])
    assert result == True


def test_verify_data_source_id_fail():
    try:
        result = helper.verify_data_source_id("3", ["1", "2"])
        assert result == False
    except:
        pass


@pytest.mark.asyncio
async def test_verify_request_success(httpx_mock: HTTPXMock):
    # mock response
    def custom_response(_: httpx.Request):
        return httpx.Response(
            status_code=200,
            json={
                "chain_id": "band-laozi-testnet5",
                "validator": "bandvaloper1knxukd35rm4cmthkdgzkfaf8lrhpexv752l7mh",
                "request_id": "2728447",
                "external_id": "2",
                "data_source_id": "226",
            },
        )

    httpx_mock.add_callback(custom_response)

    data_source_id = await helper.verify_request(mock_headers, "MOCK_URL", "0")
    assert data_source_id == "226"


@pytest.mark.asyncio
async def test_verify_request_failed(httpx_mock: HTTPXMock):
    # mock response
    def custom_response(_: httpx.Request):
        return httpx.Response(
            status_code=500,
            content=b"server error",
        )

    httpx_mock.add_callback(custom_response)

    try:
        await helper.verify_request(mock_headers, "MOCK_URL", "0")
    except Exception as e:
        assert str(e) == "server error"
