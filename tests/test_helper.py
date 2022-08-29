from genericpath import isdir
from sanic import Sanic
from app.utils import helper
from app import create_app
from os import listdir
from os.path import isfile, join
from pytest_httpx import HTTPXMock
import httpx
import pytest

app = create_app(
    "test",
    {
        "VERIFY_REQUEST_URL": "http://localhost.example",
        "CACHE_SIZE": 5000,
        "TTL_TIME": "1m",
        "MAX_DELAY_VERIFICATION": "0",
    },
)


def test_get_bandchain_params():
    params = helper.get_bandchain_params(
        {
            "BAND_CHAIN_ID": "bandchain",
            "BAND_VALIDATOR": "bandcoolvalidator",
            "BAND_EXTERNAL_ID": "2",
            "BAND_DATA_SOURCE_ID": "1",
            "BAND_REPORTER": "bandcoolreporter",
            "BAND_SIGNATURE": "coolsignature",
            "BAND_REQUEST_ID": "1",
        }
    )

    assert params == {
        "chain_id": "bandchain",
        "validator": "bandcoolvalidator",
        "external_id": "2",
        "data_source_id": "1",
        "reporter": "bandcoolreporter",
        "signature": "coolsignature",
        "request_id": "1",
    }


def test_add_params_config():
    app.update_config({"MAX_DELAY_VERIFICATION": "5"})
    params = helper.add_params_config(
        {
            "chain_id": "bandchain",
            "validator": "bandcoolvalidator",
            "external_id": "2",
            "reporter": "bandcoolreporter",
            "signature": "coolsignature",
            "request_id": "1",
        },
    )

    assert params == {
        "chain_id": "bandchain",
        "validator": "bandcoolvalidator",
        "external_id": "2",
        "reporter": "bandcoolreporter",
        "signature": "coolsignature",
        "request_id": "1",
        "max_delay": "5",
    }


def test_get_adapter():
    path = "./app/adapter"
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
    app = Sanic.get_app()
    app.update_config({"MODE": "development", "ALLOWED_DATA_SOURCE_IDS": ["1", "2"]})
    result = helper.verify_data_source_id("1")
    assert result == True


def test_verify_data_source_id_fail():
    app = Sanic.get_app()
    app.update_config({"MODE": "development", "ALLOWED_DATA_SOURCE_IDS": ["1", "2"]})
    try:
        result = helper.verify_data_source_id("3")
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

    mock_headers = {
        "BAND_CHAIN_ID": "bandchain",
        "BAND_VALIDATOR": "bandcoolvalidator",
        "BAND_REQUEST_ID": "1",
        "BAND_EXTERNAL_ID": "1",
        "BAND_DATA_SOURCE_ID": "1",
        "BAND_REPORTER": "bandcoolreporter",
        "BAND_SIGNATURE": "coolsignature",
    }
    data_source_id = await helper.verify_request(mock_headers)
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

    mock_headers = {
        "BAND_CHAIN_ID": "bandchain",
        "BAND_VALIDATOR": "bandcoolvalidator",
        "BAND_REQUEST_ID": "1",
        "BAND_EXTERNAL_ID": "1",
        "BAND_DATA_SOURCE_ID": "1",
        "BAND_REPORTER": "bandcoolreporter",
        "BAND_SIGNATURE": "coolsignature",
    }

    try:
        await helper.verify_request(mock_headers)
    except Exception as e:
        assert str(e) == "server error"
