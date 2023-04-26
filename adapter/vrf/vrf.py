import os
import httpx

from typing import TypedDict
from adapter import Adapter


class Request(TypedDict):
    seed: str
    timestamp: int


class Input(TypedDict):
    seed: str
    timestamp: int


class Output(TypedDict):
    proof: str
    hash: str


class Response(TypedDict):
    proof: str
    hash: str


class Vrf(Adapter):
    # URL that allow traffic from gateway only
    api_url: str = None

    def __init__(self):
        self.api_url = os.getenv("API_URL", None)

    def parse_input(self, request: Request) -> Input:
        return Input(**request)

    def verify_output(self, output: Output):
        if len(output["proof"]) != 160:
            raise Exception(f"invalid proof length")
        if len(output["hash"]) != 128:
            raise Exception(f"invalid hash length")

    def parse_output(self, output: Output) -> Response:
        return Response(**output)
    
    async def call(self, input_: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "POST",
            self.api_url,
            json=dict(input_)
        )

        response.raise_for_status()

        return Output(**response.json())
