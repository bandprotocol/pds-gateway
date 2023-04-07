import asyncio
from typing import Any

from fastapi import FastAPI, HTTPException, Depends
from httpx import HTTPStatusError
from pytimeparse.timeparse import timeparse
from starlette.requests import Request

from adapter import init_adapter
from app.settings import settings
from app.exceptions import VerificationFailedError
from app.middleware import RequestReportMiddleware, RequestCacheMiddleware, SignatureCacheMiddleware
from app.report import init_db
from app.report.models import StatusReport, GatewayInfo, VerifyReport, ProviderResponseReport, RequestReport
from app.utils.cache import LocalCache, RedisCache
from app.utils.helper import is_data_source_id_allowed, verify_request_from_bandchain
from app.utils.log_config import init_loggers
from app.utils.types import VerifyErrorType

# Setup apps
app = FastAPI()
request_app = FastAPI()
report_app = FastAPI()

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

# Setup report database and middleware
if db := bool(settings.MONGO_DB_URL) and settings.MODE == "production":
    request_db = init_db(settings.MONGO_DB_URL, "request", log, RequestReport)
    provider_response_db = init_db(settings.MONGO_DB_URL, "provider", log, ProviderResponseReport)
    verify_db = init_db(settings.MONGO_DB_URL, "verify", log, VerifyReport)
    request_app.add_middleware(RequestReportMiddleware, db=request_db)

# Setup adapter
adapter = init_adapter(settings.ADAPTER_TYPE, settings.ADAPTER_NAME)

# Setup caching middleware
if cache and settings.MODE == "production":
    request_app.add_middleware(RequestCacheMiddleware, cache=cache)
    request_app.add_middleware(SignatureCacheMiddleware, cache=cache)


async def verify_request(req: Request) -> None:
    """Verifies if the request originated from BandChain"""
    if settings.MODE == "production":
        report = VerifyReport(response_code=200)
        try:
            verify = await verify_request_from_bandchain(
                req.headers, settings.VERIFY_REQUEST_URL, settings.MAX_DELAY_VERIFICATION
            )

            # Checks if the data source requesting is whitelisted
            if not is_data_source_id_allowed(int(verify["data_source_id"]), settings.ALLOWED_DATA_SOURCE_IDS):
                raise VerificationFailedError(
                    status_code=401,
                    error_type=VerifyErrorType.UNSUPPORTED_DS_ID.value,
                )
            report.is_delay = verify.get("is_delay")
        except VerificationFailedError as e:
            report.response_code = e.status_code
            report.error_type = e.error_type
            report.error_msg = str(e)
        except Exception as e:
            report.response_code = 500
            report.error_type = VerifyErrorType.UNKNOWN.value
            report.error_msg = str(e)
        finally:
            # Save report to db if db is enabled
            if db:
                verify_db.save(report)


@request_app.get("/")
async def request_data(request: Request, _: None = Depends(verify_request)) -> Any:
    """Requests data from the premium data source"""
    report = ProviderResponseReport(response_code=200)
    try:
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
        if provider_response_db:
            provider_response_db.save(report)


@report_app.get("/latest")
async def get_status_report() -> StatusReport:
    """Gets a status report that contains the latest reports"""
    gateway_info = GatewayInfo(
        allow_data_source_ids=settings.ALLOWED_DATA_SOURCE_IDS,
        max_delay_verification=settings.MAX_DELAY_VERIFICATION,
    )

    if db:
        try:
            reports = await asyncio.gather(
                request_db.get_latest_report(),
                provider_response_db.get_latest_report(),
                verify_db.get_latest_report(),
            )
            return StatusReport(
                gateway_info=gateway_info,
                latest_request=reports[0].to_dict() if reports[0] else None,
                latest_response=reports[1].to_dict() if reports[1] else None,
                latest_verify=reports[2].to_dict() if reports[2] else None,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")
    else:
        return StatusReport(gateway_info=gateway_info)


@report_app.get("/latest_failed")
async def get_failed_status_report() -> StatusReport:
    """Gets a status report that contains the latest failed reports"""
    gateway_info = GatewayInfo(
        allow_data_source_ids=settings.ALLOWED_DATA_SOURCE_IDS,
        max_delay_verification=settings.MAX_DELAY_VERIFICATION,
    )

    if db:
        try:
            reports = await asyncio.gather(
                provider_response_db.get_latest_failed_report(),
                verify_db.get_latest_failed_report(),
            )

            return StatusReport(
                gateway_info=gateway_info,
                latest_response=reports[0].to_dict() if reports[0] else None,
                latest_verify=reports[1].to_dict() if reports[1] else None,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")
    else:
        return StatusReport(gateway_info=gateway_info)


# Setup Paths
app.mount("/request", request_app)
app.mount("/report", report_app)
