from sanic import Request, Sanic, response
from sanic.log import logger
from sanic.exceptions import SanicException
from config import Config
from importlib import import_module
import utils.header as header
import httpx

app = Sanic(__name__)
app.update_config(Config)


@app.main_process_start
def init_app(app):
    logger.info(f"GATEWAY_MODE: {app.config['MODE']}")


@app.main_process_start
async def init_adapter(app):
    # check adapter configuration
    if app.config["ADAPTER_TYPE"] is None:
        raise Exception("MISSING 'ADAPTER_TYPE' env")
    if app.config["ADAPTER_NAME"] is None:
        raise Exception("MISSING 'ADAPTER_NAME' env")

    logger.info(f"ADAPTER: {app.config['ADAPTER_TYPE']}.{app.config['ADAPTER_NAME']}")

    # initial adapter
    module = import_module(f"adapter.{app.config['ADAPTER_TYPE']}.{app.config['ADAPTER_NAME']}".lower())
    AdapterClass = getattr(module, "".join([part.capitalize() for part in app.config["ADAPTER_NAME"].split("_")]))
    app.ctx.adapter = AdapterClass()


@app.on_request
async def verify(request: Request):
    if app.config["MODE"] == "production":
        # call Band's endpoint to verify requestor
        client = httpx.AsyncClient()
        res = await client.get(
            url=app.config["VERIFY_REQUEST_URL"],
            params=header.get_bandchain_params(request.headers),
        )
        body = res.json()

        # check result of request
        if res.status_code != 200:
            raise SanicException(body, status_code=res.status_code)

        # check data_source_id
        if body.get("data_source_id", None) not in app.config["ALLOWED_DATA_SOURCE_IDS"]:
            raise SanicException(
                f"wrong datasource_id, expected {app.config['ALLOWED_DATA_SOURCE_IDS']}.", status_code=401
            )


@app.get("/<path:path>")
async def request(request: Request, path: str):
    try:
        output = await app.ctx.adapter.unified_call(request)
        return response.json(output)

    except Exception as e:
        raise SanicException(f"{e}", status_code=500)
