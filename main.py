from sanic import Sanic, response
from sanic.log import logger
from config import config
import utils
import httpx

app = Sanic(__name__)


@app.middleware("request")
async def verify(request):

    # CALL BAND_ENDPOINT TO VALIDATE REQUESTOR
    res = await utils.verify_request(request.headers)
    body = res.json()

    # CHECK RESULT OF REQUEST
    if res.status_code != 200:
        return response.json(body, status=res.status_code)

    # CHECK DATA_SOURCE_ID
    if body.get("data_source_id", None) not in config["ALLOW_DATA_SOURCE_IDS"]:
        return response.json(
            {
                "error": f"wrong datasource_id, expected {config['ALLOW_DATA_SOURCE_IDS']}.",
            },
            status=400,
        )


@app.route("/<path:path>", methods=["GET", "POST"])
async def request(request, path):

    try:
        async with httpx.AsyncClient() as client:
            res = await client.request(
                request.method,
                f"{config['ENDPOINT_URL']}/{path}" if path else config["ENDPOINT_URL"],
                params=request.args,
                headers=utils.get_endpoint_headers(request.headers),
                content=request.body,
            )

        return response.json(res.json(), status=res.status_code)

    except Exception as e:
        logger.warning(str(e))
        return response.json(
            {
                "error": f"endpoint error.",
            },
            status=400,
        )
