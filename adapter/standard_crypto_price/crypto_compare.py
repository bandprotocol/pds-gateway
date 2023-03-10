import os
from datetime import datetime
from typing import Dict

import httpx

from adapter.standard_crypto_price.base import StandardCryptoPrice, Input, Output


class CryptoCompare(StandardCryptoPrice):
    api_url: str = "https://min-api.cryptocompare.com/data/pricemulti"
    api_key: str = None
    symbols_map: Dict[str, str] = None
    symbols_map_back: Dict[str, str] = None

    def __init__(self) -> None:
        self.api_key = os.getenv("CRYPTO_COMPARE_API_KEY", None)
        self.symbols_map = {
            "CUSD": "CELOUSD",
        }
        self.symbols_map_back = {v: k for k, v in self.symbols_map.items()}

    async def call(self, input_: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "GET",
            self.api_url,
            params={
                "fsyms": ",".join([self.symbols_map.get(symbol, symbol) for symbol in input_["symbols"]]),
                "tsyms": "USD",
            },
            headers={"Authorization": f"Apikey " + self.api_key},
        )
        response.raise_for_status()
        response_json = response.json()

        timestamp = int(datetime.now().timestamp())
        prices = [
            {
                "symbol": self.symbols_map_back.get(symbol, symbol),
                "price": float(value["USD"]),
                "timestamp": timestamp,
            }
            for symbol, value in response_json.items()
        ]

        return Output(prices=prices)
