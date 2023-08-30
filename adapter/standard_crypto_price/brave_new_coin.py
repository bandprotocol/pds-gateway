import concurrent.futures
import os
import requests

from datetime import datetime
from typing import Dict

from adapter.standard_crypto_price.base import StandardCryptoPrice, Input, Output


class BraveNewCoin(StandardCryptoPrice):
    api_url: str = "https://api.bravenewcoin.com/v3/index-ticker"
    client_id: str
    client_secret: str
    symbols_map: Dict[str, str] = None
    symbols_map_back: Dict[str, str] = None

    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID", None)
        self.client_secret = os.getenv("CLIENT_SECRET", None)
        self.symbols_map = {
            "BAND": "daf9f645-b832-4859-bdf4-2a833571ab90",
            "BTC": "f1ff77b6-3ab4-4719-9ded-2fc7e71cff1f",
            "ETH": "e991ba77-d384-48ff-b0a4-40e95ef6b7d6",
            "USDT": "eefcc863-188e-4fbb-9a78-6e2cf12027a0",
        }
        self.symbols_map_back = {v: k for k, v in self.symbols_map.items()}

    def get_access_token(client_id, client_secret: str) -> str:
        url = "https://api.bravenewcoin.com/v3/oauth/token"
        res = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
            },
            json={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": "https://api.bravenewcoin.com",
            },
        )

        if res.status_code != 200:
            raise Exception(res.json())

        return res.json()["access_token"]

    def get_price(url, id, token: str) -> requests.Response:
        return requests.get(
            url,
            params={"indexId": id},
            headers={
                "Authorization": "Bearer " + token,
            },
        )

    async def call(self, input_: Input) -> Output:
        token = self.get_access_token(self.client_id, self.client_secret)
        ids = [self.symbols_map.get(symbol, symbol) for symbol in input_["symbols"]]
        prices = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_symbol = {
                executor.submit(self.get_price, self.api_url, id, token): self.symbols_map_back.get(id) for id in ids
            }
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    res = future.result()
                    if res.status_code != 200:
                        return res.content, res.status_code
                    result = res.json()["content"][0]
                    prices.append(
                        {
                            "symbol": symbol,
                            "price": result["price"],
                            "timestamp": int(datetime.now().timestamp()),
                        }
                    )
                except Exception as exc:
                    print("%r generated an exception: %s" % (self.api_url, exc))

        return Output(prices=prices)
