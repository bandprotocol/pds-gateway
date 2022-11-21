from fastapi import FastAPI, Request
from httpx import HTTPStatusError
from pytimeparse.timeparse import timeparse
from fastapi.responses import JSONResponse

from app.report import DB, Verify
from app.utils.types import VerifyErrorType
from app.utils import helper, cache
from app.utils.exception import UnsupportedDsException
from app.adapter import Adapter
from app.report import CollectVerifyData, CollectRequestData, GetStatus


def create_app(config):
    app = FastAPI()

    print(f"GATEWAY_MODE: {config.MODE}")

    def init_db():
        app.state.db = None
        if config.MONGO_DB_URL and config.COLLECTION_DB_NAME:
            app.state.db = DB(config.MONGO_DB_URL, config.COLLECTION_DB_NAME)
            print(f"DB : init report data on mongo db")
        else:
            print(
                f"DB : No DB config -> if you want to save data on db please add [MONGO_DB_URL, COLLECTION_DB_NAME] in env"
            )

    def init_adaptor() -> Adapter:
        # check adapter configuration
        if config.ADAPTER_TYPE is None:
            raise Exception("MISSING 'ADAPTER_TYPE' ENV")
        if config.ADAPTER_NAME is None:
            raise Exception("MISSING 'ADAPTER_NAME' ENV")

        app.state.adapter = helper.get_adapter(config.ADAPTER_TYPE, config.ADAPTER_NAME)

    # init cache memory
    app.state.cache_data = cache.Cache(config.CACHE_SIZE, timeparse(config.TTL_TIME))

    init_db()
    init_adaptor()

    @app.middleware("http")
    @CollectVerifyData(db=app.state.db)
    async def verify(request: Request, call_next):
        try:
            if config.MODE == "production" and request.url.path != "/status":
                # pass verify if already cache
                if app.state.cache_data.get_data(helper.get_band_signature_hash(request.headers)):
                    return await call_next(request)

                verified = await helper.verify_request(
                    request.headers, config.VERIFY_REQUEST_URL, config.MAX_DELAY_VERIFICATION
                )
                helper.verify_data_source_id(verified["data_source_id"], config.ALLOWED_DATA_SOURCE_IDS.split(","))
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
    async def request(request: Request):
        if config.MODE == "production":
            # get cache data
            latest_data = app.state.cache_data.get_data(helper.get_band_signature_hash(request.headers))
            if latest_data:
                latest_data["cached_data"] = True
                return latest_data

        try:
            output = await app.state.adapter.unified_call(request)
            if config.MODE == "production":
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
    @GetStatus(config, app.state.db)
    def get_report_status(request: Request):
        return {}

    return app
