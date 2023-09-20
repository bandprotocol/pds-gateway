import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Request, Response
from pytest_httpx import HTTPXMock

from app.middleware import VerifyRequestMiddleware


@pytest.fixture
def mock_headers() -> dict[str, str]:
    return {
        "NOT_BAND": "0",
        "BAND_CHAIN_ID": "bandchain",
        "BAND_VALIDATOR": "bandcoolvalidator",
        "BAND_REQUEST_ID": "1",
        "BAND_EXTERNAL_ID": "1",
        "BAND_DATA_SOURCE_ID": "1",
        "BAND_REPORTER": "bandcoolreporter",
        "BAND_SIGNATURE": "coolsignature",
    }


@pytest.fixture
def mock_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(
        VerifyRequestMiddleware,
        verify_url="https://www.mock-verify.com",
        max_verification_delay=0,
        allowed_data_source_ids=[1, 2],
        report_db=None,
    )

    @app.get("/request")
    def test_request():
        return {"Hello": "World"}

    return TestClient(app, "http://test_pds")


@pytest.fixture
def non_mocked_hosts() -> list[str]:
    return ["test_pds"]


@pytest.mark.asyncio
async def test_verify_request_from_bandchain_success(
    mock_client: TestClient, mock_headers: dict[str, str], httpx_mock: HTTPXMock
):
    httpx_mock.add_response(
        method="GET",
        url="https://www.mock-verify.com",
        status_code=200,
        json={
            "chain_id": "band-laozi-testnet6",
            "validator": "bandvaloper1knxukd35rm4cmthkdgzkfaf8lrhpexv752l7mh",
            "request_id": "2728447",
            "external_id": "2",
            "data_source_id": "1",
            "is_delay": False,
        },
    )

    res = mock_client.get("/request", headers=mock_headers)
    assert res.json() == {"Hello": "World"}
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_verify_request_from_bandchain_with_prohibited_ds_id(
    mock_client: TestClient, mock_headers: dict[str, str], httpx_mock: HTTPXMock
):
    httpx_mock.add_response(
        method="GET",
        url="https://www.mock-verify.com",
        status_code=200,
        json={
            "chain_id": "band-laozi-testnet6",
            "validator": "bandvaloper1knxukd35rm4cmthkdgzkfaf8lrhpexv752l7mh",
            "request_id": "2728447",
            "external_id": "2",
            "data_source_id": "100",
            "is_delay": False,
        },
    )

    res = mock_client.get("/request", headers=mock_headers)
    assert res.json() == {"error": "Data source is not allowed"}
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_verify_request_from_bandchain_with_verify_fail(
    mock_client: TestClient, mock_headers: dict[str, str], httpx_mock: HTTPXMock
):
    httpx_mock.add_response(
        method="GET",
        url="https://www.mock-verify.com",
        status_code=500,
        content=b"server error",
    )

    res = mock_client.get("/request", headers=mock_headers)
    assert res.json() == {"error": "Internal Server Error"}
    assert res.status_code == 500


@pytest.mark.asyncio
async def test_verify_request_from_bandchain_with_invalid_verify_response(
    mock_client: TestClient, mock_headers: dict[str, str], httpx_mock: HTTPXMock
):
    httpx_mock.add_response(method="GET", url="https://www.mock-verify.com", status_code=200, json={"not": "valid"})

    res = mock_client.get("/request", headers=mock_headers)
    assert res.json() == {"error": "Failed to parse successful response from verify endpoint"}
    assert res.status_code == 500
