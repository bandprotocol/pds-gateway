from app.adapter.standard_crypto_price import StandardCryptoPrice, Input, Output
import os


class Template(StandardCryptoPrice):
    api_url: str
    api_key: str

    def __init__(self):
        self.api_url = os.getenv("API_URL", None)
        self.api_key = os.getenv("API_KEY", None)

    async def call(self, input: Input) -> Output:
        return Output()
