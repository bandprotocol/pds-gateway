from venv import create
from sanic import Request, Sanic, response
from sanic.log import logger
from sanic.exceptions import SanicException
from config import config
import app.utils.helper as helper


def create_app(name, config):
    app = Sanic(name)
    app.update_config(config)

    def init_app(app):
        logger.info(f"GATEWAY_MODE: {app.config['MODE']}")

    def init_adapter(app):
        # check adapter configuration
        if app.config["ADAPTER_TYPE"] is None:
            raise Exception("MISSING 'ADAPTER_TYPE' env")
        if app.config["ADAPTER_NAME"] is None:
            raise Exception("MISSING 'ADAPTER_NAME' env")

        logger.info(f"ADAPTER: {app.config['ADAPTER_TYPE']}.{app.config['ADAPTER_NAME']}")
        app.ctx.adapter = helper.get_adapter(app.config["ADAPTER_TYPE"], app.config["ADAPTER_NAME"])

    @app.main_process_start
    def init(app):
        init_app(app)
        init_adapter(app)

    @app.on_request
    async def verify(request: Request):
        try:
            if app.config["MODE"] == "production":
                data_source_id = await helper.verify_request(request.headers)
                helper.verify_data_source_id(data_source_id)
        except Exception as e:
            raise SanicException(f"{e}", status_code=401)

    @app.get("/<path:path>")
    async def request(request: Request, path: str):
        try:
            output = await app.ctx.adapter.unified_call(request)
            return response.json(output)

        except Exception as e:
            raise SanicException(f"{e}", status_code=500)

    return app