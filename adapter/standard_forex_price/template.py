import os

from adapter.standard_forex_price.base import StandardForexPrice, Input, Output


class Template(StandardForexPrice):
    api_url: str
    api_key: str

    def __init__(self) -> None:
        self.api_url = os.getenv("API_URL", None)
        self.api_key = os.getenv("API_KEY", None)

    async def call(self, input_: Input) -> Output:
        pass
