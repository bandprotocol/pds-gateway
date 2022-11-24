import logging
from functools import lru_cache
from fastapi import Depends, FastAPI, Request
from httpx import HTTPStatusError
from pytimeparse.timeparse import timeparse
from fastapi.responses import JSONResponse

from adapter import init_adapter
from app import config
from app.report import init_db
from app.report.middlewares import CollectVerifyData, CollectRequestData, GetStatus
from app.report.models import Verify
from app.utils.types import VerifyErrorType
from app.utils import helper, cache
from app.utils.exception import UnsupportedDsException
from app.utils.log_config import init_loggers

app = FastAPI()


@lru_cache()
def get_settings():
    return config.Settings()


settings = get_settings()

# create logger
init_loggers(log_level=settings.LOG_LEVEL)
log = logging.getLogger("pds_gateway_log")


log.info(f"GATEWAY_MODE: {settings.MODE}")


app.state.cache_data = cache.Cache(settings.CACHE_SIZE, timeparse(settings.TTL_TIME))
app.state.db = init_db(settings.MONGO_DB_URL, settings.COLLECTION_DB_NAME, log)
app.state.adapter = init_adapter(settings.ADAPTER_TYPE, settings.ADAPTER_NAME)


@app.middleware("http")
@CollectVerifyData(db=app.state.db)
async def verify(request: Request, call_next, settings: config.Settings = settings):
    try:
        if settings.MODE == "production" and request.url.path != "/status":
            # pass verify if already cache
            if app.state.cache_data.get_data(helper.get_band_signature_hash(request.headers)):
                return await call_next(request)

            verified = await helper.verify_request(
                request.headers, settings.VERIFY_REQUEST_URL, settings.MAX_DELAY_VERIFICATION
            )
            helper.verify_data_source_id(verified["data_source_id"], settings.ALLOWED_DATA_SOURCE_IDS.split(","))
            request.state.verify = Verify(response_code=200, is_delay=verified["is_delay"])

            return await call_next(request=request)

        else:
            request.state.verify = Verify(response_code=200, is_delay=False)
            return await call_next(request=request)

    except UnsupportedDsException as e:
        return helper.json_verify_error_response(
            401,
            VerifyErrorType.UNSUPPORTED_DS_ID,
            f"wrong data_source_id. expected {e.allowed_data_source_ids}, got {e.data_source_id}.",
        )

    except HTTPStatusError as e:
        return helper.json_verify_error_response(
            e.response.status_code,
            VerifyErrorType.FAILED_VERIFICATION,
            f"{e}",
        )

    except Exception as e:
        return helper.json_verify_error_response(
            500,
            VerifyErrorType.SERVER_ERROR,
            f"{e}",
        )


@app.get("/")
@CollectRequestData(db=app.state.db)
async def request(request: Request, settings: config.Settings = Depends(get_settings)):
    if settings.MODE == "production":
        # get cache data
        latest_data = app.state.cache_data.get_data(helper.get_band_signature_hash(request.headers))
        if latest_data:
            latest_data["cached_data"] = True
            return latest_data

    try:
        output = await app.state.adapter.unified_call(request)
        if settings.MODE == "production":
            # cache data
            app.state.cache_data.set_data(helper.get_band_signature_hash(request.headers), output)

        return output

    except HTTPStatusError as e:
        return JSONResponse(
            status_code=e.response.status_code,
            content={"error_msg": f"{e}"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error_msg": f"{e}"},
        )


@app.get("/status")
@GetStatus(settings, app.state.db)
def get_report_status(request: Request):
    return {}
