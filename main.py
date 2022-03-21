from wsgiref import headers
from sanic import Sanic, response
from sanic_redis import SanicRedis
from sanic.log import logger
from config import config
import utils
import httpx

app = Sanic(__name__)
# app.config.update(
#     {
#         "REDIS": config["REDIS"],
#     }
# )

# redis = SanicRedis(config_name="REDIS")
# redis.init_app(app)


@app.middleware("request")
async def verify(request):

    # CHECK DATA FROM CACHE
    # async with request.app.ctx.redis as r:
    #     body = await r.get(get_cache_key(request.headers))
    #     if body:
    #         return response.json(json.loads(body.decode("UTF-8")))

    # CALL VALIDATE REQUEST
    res = await utils.verify_requester(request.headers)
    body = res.json()

    # CHECK RESULT OF REQUEST
    if res.status_code != 200:
        logger.warning(f"{res.text}")
        return response.json(body, status=res.status_code)

    # CHECK DATA_SOURCE_ID
    if body.get("data_source_id", None) not in config["ALLOW_DATA_SOURCE_IDS"]:
        return response.json(
            {
                "error": f"wrong datasource_id, expected {config['ALLOW_DATA_SOURCE_IDS']}.",
            },
            status=400,
        )

    request.headers["BAND_PROXY_API_KEY"] = config["API_KEY"]


# @app.middleware("response")
# async def cache(request, response):
#     if response.status == 200:
#         async with request.app.ctx.redis as r:
#             await r.set(
#                 get_cache_key(request.headers),
#                 response.body,
#             )


@app.route("/<path:path>", methods=["GET", "POST"])
async def request(request, path):

    # print(request.method)
    # print(f"{config['ENDPOINT_URL']}/{path}" if path else config["ENDPOINT_URL"])
    # print(request.args)
    # print(request.body)
    # print(request.headers)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.request(
                request.method,
                f"{config['ENDPOINT_URL']}/{path}" if path else config["ENDPOINT_URL"],
                params=request.args,
                headers=utils.get_bandchain_headers(request.headers),
                content=request.body,
            )

        print(res.json())
        return response.json(res.json(), status=res.status_code)

    except Exception as e:
        return response.json(
            {
                "error": f"endpoint error.",
            },
            status=400,
        )


if __name__ == "__main__":
    app.run(host=config["HOST"], port=config["PORT"], debug=config["DEBUG"])
