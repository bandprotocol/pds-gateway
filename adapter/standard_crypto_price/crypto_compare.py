from adapter.standard_crypto_price import StandardCryptoPrice, Input, Output
from typing import Dict, TypedDict
import httpx
import os


class Config(TypedDict):
    API_URL: str
    API_KEY: str


class CryptoCompare(StandardCryptoPrice):
    config: Config = None
    symbols_map: Dict[str, str] = None
    symbols_map_back: Dict[str, str] = None

    def __init__(self):
        self.config = Config(
            API_URL=os.getenv("CRYPTO_COMPARE_API_URL", None),
            API_KEY=os.getenv("CRYPTO_COMPARE_API_KEY", None),
        )

        self.symbols_map = {
            "CUSD": "CELOUSD",
        }

        self.symbols_map_back = {v: k for k, v in self.symbols_map.items()}

    async def call(self, input: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "GET",
            self.config["API_URL"],
            params={
                "fsyms": ",".join([self.symbols_map.get(symbol, symbol) for symbol in input["symbols"]]),
                "tsyms": "USD",
            },
            headers={"Authorization": f"Apikey " + self.config["API_KEY"]},
        )
        response.raise_for_status()
        response_json = response.json()

        result = {
            self.symbols_map_back.get(symbol, symbol): float(value["USD"]) for symbol, value in response_json.items()
        }
        return Output(
            rates=[result[symbol] for symbol in input["symbols"]],
        )
