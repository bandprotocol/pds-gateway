import os

import httpx

from adapter.standard_crypto_price.base import StandardCryptoPrice, Input, Output


class InternalService(StandardCryptoPrice):
    # URL that allow traffic from gateway only
    api_url: str = None

    def __init__(self):
        self.api_url = os.getenv("API_URL", None)

    async def call(self, input_: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "GET",
            self.api_url,
            params={"symbols": ",".join(input_["symbols"])},
        )

        response.raise_for_status()
        response_json = response.json()

        prices = [
            {
                "symbol": item["symbol"],
                "price": float(item["price"]),
                "timestamp": int(item["timestamp"]),
            }
            for item in response_json["prices"]
        ]

        return Output(prices=prices)
