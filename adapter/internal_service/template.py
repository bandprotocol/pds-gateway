import os

from adapter.internal_service.base import InternalService, Input, Output


class Template(InternalService):
    api_url: str
    api_key: str

    def __init__(self) -> None:
        self.api_url = os.getenv("API_URL", None)
        self.api_key = os.getenv("API_KEY", None)

    async def call(self, input_: Input) -> Output:
        pass
