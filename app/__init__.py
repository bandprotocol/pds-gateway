from sanic import Request, Sanic, response
from sanic.log import logger
from sanic.exceptions import SanicException
from httpx import HTTPStatusError
from pytimeparse.timeparse import timeparse

from app.utils import helper, cache
from app.report import collect_verify_data, collect_request_data


def create_app(name, config):
    app = Sanic(name)
    app.update_config(config)

    # init cache memory
    cache_data = cache.Cache(app.config.CACHE_SIZE, timeparse(app.config.TTL_TIME))

    def init_app(app):
        logger.info(f"GATEWAY_MODE: {app.config.MODE}")

    def init_adapter(app):
        # check adapter configuration
        if app.config.ADAPTER_TYPE is None:
            raise Exception("MISSING 'ADAPTER_TYPE' ENV")
        if app.config.ADAPTER_NAME is None:
            raise Exception("MISSING 'ADAPTER_NAME' ENV")

        logger.info(f"ADAPTER: {app.config.ADAPTER_TYPE}.{app.config.ADAPTER_NAME}")
        app.ctx.adapter = helper.get_adapter(app.config.ADAPTER_TYPE, app.config.ADAPTER_NAME)

    @app.main_process_start
    def init(app):
        init_app(app)
        init_adapter(app)

    @app.on_request
    @collect_verify_data
    async def verify(request: Request):
        try:
            if app.config.MODE == "production":
                # pass verify if already cache
                if cache_data.get_data(helper.get_band_signature_hash(request.headers)):
                    return

                data_source_id = await helper.verify_request(request.headers)
                helper.verify_data_source_id(data_source_id)

            # raise Exception("Sorry can't verify")

        except Exception as e:
            raise SanicException(f"{e}", status_code=401)

    @app.get("/")
    @collect_request_data()
    async def request(request: Request):

        if app.config.MODE == "production":
            # check cache data
            latest_data = cache_data.get_data(helper.get_band_signature_hash(request.headers))
            if latest_data:
                return response.json(latest_data)

        try:
            output = await app.ctx.adapter.unified_call(request)

            if app.config.MODE == "production":
                # cache data
                cache_data.set_data(helper.get_band_signature_hash(request.headers), output)

            raise Exception("fakkkk")

            return response.json(output)

        except HTTPStatusError as e:
            raise SanicException(f"{e}", status_code=e.response.status_code)
        except Exception as e:
            print("WoWWWWWWWW")
            ## todo get res status
            raise SanicException(f"{e}", status_code=500)

    return app
