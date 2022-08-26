from app.adapter.standard_crypto_price import StandardCryptoPrice, Input, Output
import httpx


class Pricer(StandardCryptoPrice):
    api_url: str = "https://px.bandchain.org"

    async def call(self, input: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "GET",
            self.api_url,
            params={
                "source": input["source"],
                "symbols": ",".join(input["symbols"]),
            },
        )
        response.raise_for_status()
        response_json = response.json()

        prices = [
            {
                "symbol": item["symbol"],
                "price": float(item["price"]),
                "timestamp": item["timestamp"],
            }
            for item in response_json["prices"]
        ]

        return Output(
            prices=prices,
        )
