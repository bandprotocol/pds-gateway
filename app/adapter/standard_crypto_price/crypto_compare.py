from app.adapter.standard_crypto_price import StandardCryptoPrice, Input, Output
from typing import Dict
import httpx
import os


class CryptoCompare(StandardCryptoPrice):
    api_url: str = "https://min-api.cryptocompare.com/data/pricemulti"
    api_key: str = None
    symbols_map: Dict[str, str] = None
    symbols_map_back: Dict[str, str] = None

    def __init__(self):
        self.api_key = os.getenv("CRYPTO_COMPARE_API_KEY", None)
        self.symbols_map = {
            "CUSD": "CELOUSD",
        }
        self.symbols_map_back = {v: k for k, v in self.symbols_map.items()}

    async def call(self, input: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "GET",
            self.api_url,
            params={
                "fsyms": ",".join([self.symbols_map.get(symbol, symbol) for symbol in input["symbols"]]),
                "tsyms": "USD",
            },
            headers={"Authorization": f"Apikey " + self.api_key},
        )
        response.raise_for_status()
        response_json = response.json()

        result = {
            self.symbols_map_back.get(symbol, symbol): float(value["USD"]) for symbol, value in response_json.items()
        }
        return Output(
            rates=[result[symbol] for symbol in input["symbols"]],
        )