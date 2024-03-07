import asyncio
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from httpx import HTTPStatusError
from pytimeparse.timeparse import timeparse
from starlette.requests import Request

from adapter import init_adapter
from app.middleware import (
    RequestReportMiddleware,
    RequestCacheMiddleware,
    SignatureCacheMiddleware,
    VerifyRequestMiddleware,
)
from app.report import init_db
from app.report.models import Reports, GatewayInfo, VerifyReport, ProviderResponseReport, RequestReport
from app.settings import settings
from app.utils.cache import LocalCache, RedisCache
from app.utils.log_config import init_loggers

# Setup apps
app = FastAPI()
request_app = FastAPI()
info_app = FastAPI()
reports_app = FastAPI()

# Setup logger
log = init_loggers(log_level=settings.LOG_LEVEL)
log.info(f"GATEWAY_MODE: {settings.MODE}")

# Setup cache
if settings.CACHE_TYPE == "redis":
    cache = RedisCache(settings.REDIS_URL, settings.REDIS_PORT, settings.REDIS_DB, timeparse(settings.TTL))
elif settings.CACHE_TYPE == "local":
    cache = LocalCache(settings.CACHE_SIZE, timeparse(settings.TTL))
else:
    cache = None

# Setup report database
if db_enabled := bool(settings.MONGO_DB_URL) and settings.MODE == "production":
    request_db = init_db(
        settings.MONGO_DB_URL,
        f"{settings.COLLECTION_DB_NAME}-request",
        log,
        RequestReport,
        expiration_time=settings.MONGO_DB_EXPIRATION_TIME,
    )
    provider_response_db = init_db(
        settings.MONGO_DB_URL,
        f"{settings.COLLECTION_DB_NAME}-provider",
        log,
        ProviderResponseReport,
        expiration_time=settings.MONGO_DB_EXPIRATION_TIME,
    )
    verify_db = init_db(
        settings.MONGO_DB_URL,
        f"{settings.COLLECTION_DB_NAME}-verify",
        log,
        VerifyReport,
        expiration_time=settings.MONGO_DB_EXPIRATION_TIME,
    )
else:
    request_db = None
    provider_response_db = None
    verify_db = None

# Setup adapter
adapter = init_adapter(settings.ADAPTER_TYPE, settings.ADAPTER_NAME)

# Setup middleware
if settings.MODE == "production":
    # Add middleware to store all requests
    if db_enabled:
        request_app.add_middleware(RequestReportMiddleware, db=request_db)

    # Add middleware to cache requests by signature
    if cache:
        request_app.add_middleware(RequestCacheMiddleware, cache=cache, timeout=timeparse(settings.PENDING_TIMEOUT))

    # Add middleware to verify requests
    request_app.add_middleware(
        VerifyRequestMiddleware,
        verify_url=settings.VERIFY_REQUEST_URL,
        max_verification_delay=settings.MAX_DELAY_VERIFICATION,
        allowed_data_source_ids=settings.ALLOWED_DATA_SOURCE_IDS,
        report_db=verify_db,
    )

    # Add middleware to cache responses by signature
    if cache:
        request_app.add_middleware(SignatureCacheMiddleware, cache=cache)


@request_app.get("/")
@request_app.post("/")
async def request_data(request: Request) -> Any:
    """Requests data from the premium data source"""
    report = ProviderResponseReport(
        response_code=200,
        created_at=datetime.utcnow(),
    )
    try:
        if request.method == "POST":
            return await adapter.unified_call(await request.json())
        else:
            return await adapter.unified_call(dict(request.query_params))
    except HTTPStatusError as e:
        report.response_code = e.response.status_code
        report.error_msg = str(e)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=str(e),
        )
    except Exception as e:
        report.response_code = 500
        report.error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    finally:
        if db_enabled:
            provider_response_db.save(report)


@info_app.get("/")
async def get_info() -> GatewayInfo:
    """Gets the gateway info"""
    return GatewayInfo(
        allow_data_source_ids=settings.ALLOWED_DATA_SOURCE_IDS,
        max_delay_verification=settings.MAX_DELAY_VERIFICATION,
    )


@reports_app.get("/latest")
async def get_status_report() -> Reports:
    """Gets the latest reports"""
    if db_enabled:
        try:
            reports = await asyncio.gather(
                request_db.get_latest_report(),
                provider_response_db.get_latest_report(),
                verify_db.get_latest_report(),
            )
            return Reports(
                latest_request=reports[0].to_dict() if reports[0] else None,
                latest_response=reports[1].to_dict() if reports[1] else None,
                latest_verify=reports[2].to_dict() if reports[2] else None,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")
    else:
        raise HTTPException(status_code=501, detail="Reports are not enabled")


@reports_app.get("/latest_failed")
async def get_failed_status_report() -> Reports:
    """Gets the latest failed reports"""
    if db_enabled:
        try:
            reports = await asyncio.gather(
                provider_response_db.get_latest_failed_report(),
                verify_db.get_latest_failed_report(),
            )

            return Reports(
                latest_response=reports[0].to_dict() if reports[0] else None,
                latest_verify=reports[1].to_dict() if reports[1] else None,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")
    else:
        raise HTTPException(status_code=501, detail="Reports are not enabled")


# Setup Paths
app.mount("/request", request_app)
app.mount("/info", info_app)
app.mount("/reports", reports_app)
