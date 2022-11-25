import imp
import logging
from functools import lru_cache
from fastapi import Depends, FastAPI, Request
from httpx import HTTPStatusError
from pytimeparse.timeparse import timeparse
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from adapter import init_adapter
from app import config
from app.report import init_db
from app.report.middlewares import CollectVerifyData, CollectRequestData
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


@CollectVerifyData(db=app.state.db)
async def verify(request: Request, settings: config.Settings = settings):
    try:
        if settings.MODE == "production":
            # pass verify if already cache
            if app.state.cache_data.get_data(helper.get_band_signature_hash(request.headers)):
                return Verify(response_code=200, is_delay=False)

            verified = await helper.verify_request(
                request.headers, settings.VERIFY_REQUEST_URL, settings.MAX_DELAY_VERIFICATION
            )
            helper.verify_data_source_id(verified["data_source_id"], settings.ALLOWED_DATA_SOURCE_IDS.split(","))

            return Verify(response_code=200, is_delay=verified["is_delay"])

        return Verify(response_code=200, is_delay=False)

    except UnsupportedDsException as e:
        raise HTTPException(
            status_code=401,
            detail={
                "verify_error_type": VerifyErrorType.UNSUPPORTED_DS_ID.value,
                "error_msg": f"wrong data_source_id. expected {e.allowed_data_source_ids}, got {e.data_source_id}.",
            },
        )

    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"verify_error_type": VerifyErrorType.FAILED_VERIFICATION.value, "error_msg": f"{e}"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"verify_error_type": VerifyErrorType.SERVER_ERROR.value, "error_msg": f"{e}"}
        )


@app.get("/")
@CollectRequestData(db=app.state.db)
async def request(
    request: Request, settings: config.Settings = Depends(get_settings), verify: Verify = Depends(verify)
):
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
async def get_report_status(settings: config.Settings = Depends(get_settings)):
    res = {
        "gateway_info": {
            "allow_data_source_ids": settings.ALLOWED_DATA_SOURCE_IDS,
            "max_delay_verification": settings.MAX_DELAY_VERIFICATION,
        }
    }

    if app.state.db:
        try:
            res["latest_request"] = await app.state.db.get_latest_request_info()
            res["latest_failed_request"] = await app.state.db.get_latest_verify_failed()

            return res
        except Exception as e:
            raise HTTPException(f"{e}", status_code=500)

    return res
