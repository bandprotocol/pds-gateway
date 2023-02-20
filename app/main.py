import logging
from typing import Any

from fastapi import Depends, FastAPI, Request, HTTPException
from httpx import HTTPStatusError
from pytimeparse.timeparse import timeparse

from adapter import init_adapter
from app.config import Settings
from app.report import init_db
from app.report.middlewares import CollectVerifyData, CollectRequestData
from app.report.models import Verify
from app.utils.cache import Cache
from app.utils.helper import is_data_source_id_allowed, verify_request, get_band_signature_hash
from app.utils.log_config import init_loggers
from app.utils.types import VerifyErrorType

app = FastAPI()


@app.on_event("startup")
async def set_startup():
    """Runs events on server startup"""
    # Get setting
    settings = Settings()

    # Setup logger
    init_loggers(log_level=settings.LOG_LEVEL)
    log = logging.getLogger("pds_gateway_log")
    log.info(f"GATEWAY_MODE: {settings.MODE}")

    # Setup app state
    app.state.cache_data = Cache(settings.CACHE_SIZE, timeparse(settings.TTL))
    app.state.db = init_db(settings.MONGO_DB_URL, settings.COLLECTION_DB_NAME, log)
    app.state.adapter = init_adapter(settings.ADAPTER_TYPE, settings.ADAPTER_NAME)


@CollectVerifyData(db=app.state.db)
async def verify(req: Request, settings: Settings = Depends(Settings)) -> Verify:
    """Verifies if the request originated from BandChain"""
    # Skip verification if request has already been cached
    if settings.MODE == "production" and app.state.cache_data.get_data(get_band_signature_hash(req.headers)):
        # Verify the request is from BandChain
        verified = await verify_request(req.headers, settings.VERIFY_REQUEST_URL, settings.MAX_DELAY_VERIFICATION)

        # Checks if the data source requesting is whitelisted
        if not is_data_source_id_allowed(int(verified["data_source_id"]), settings.ALLOWED_DATA_SOURCE_IDS):
            raise HTTPException(
                status_code=401,
                detail={
                    "verify_error_type": VerifyErrorType.UNSUPPORTED_DS_ID.value,
                    "error_msg": "wrong data_source_id. expected {allowed}, got {actual}.".format(
                        allowed=settings.ALLOWED_DATA_SOURCE_IDS, actual=verified["data_source_id"]
                    ),
                },
            )

        return Verify(response_code=200, is_delay=verified["is_delay"])
    else:
        return Verify(response_code=200, is_delay=False)


@app.get("/", dependencies=[Depends(verify)])
@CollectRequestData(db=app.state.db)
async def request(req: Request, settings: Settings = Depends(Settings)) -> str:
    """Requests data from the premium data source"""
    if settings.MODE == "production":
        # Get cached data
        latest_data = app.state.cache_data.get_data(get_band_signature_hash(req.headers))
        if latest_data:
            latest_data["cached_data"] = True
            return latest_data

    try:
        output = await app.state.adapter.unified_call(dict(req.query_params))
        if settings.MODE == "production":
            # Cache data
            app.state.cache_data.set_data(get_band_signature_hash(req.headers), output)

        return output
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error_msg": f"{e}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_msg": f"{e}"},
        )


@app.get("/status")
async def get_report_status(settings: Settings = Depends(Settings)) -> dict[str, Any]:
    """Gets a status report: gateway info, latest request and latest failed request"""
    res = {
        "gateway_info": {
            "allow_data_source_ids": settings.ALLOWED_DATA_SOURCE_IDS,
            "max_delay_verification": settings.MAX_DELAY_VERIFICATION,
        }
    }

    if app.state.db:
        try:
            res["latest_request"] = await app.state.db.get_latest_request_info()
            res["latest_failed_request"] = await app.state.db.get_latest_failed_request_info()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")

    return res
