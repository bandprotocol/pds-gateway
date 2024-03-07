import os
import httpx

from typing import TypedDict
from adapter import Adapter


class Request(TypedDict):
    model: str
    messages: str
    temperature: float
    top_p: float
    max_tokens: int
    stream: bool
    safe_prompt: bool
    random_seed: int


class Input(TypedDict):
    model: str
    messages: str
    temperature: float
    top_p: float
    max_tokens: int
    stream: bool
    safe_prompt: bool
    random_seed: int


class Output(TypedDict):
    answer: str


class Response(TypedDict):
    answer: str


class Mistral(Adapter):
    api_url: str = "https://api.mistral.ai/v1/chat/completions"
    api_key: str
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY", None)

    def parse_input(self, request: Request) -> Input:
        return Input(**request)

    def verify_output(self, input_: Input, output: Output):
        pass

    def parse_output(self, output: Output) -> Response:
        return Response(**output)
    
    async def call(self, input_: Input) -> Output:        
        client = httpx.AsyncClient()
        response = await client.request(
            "POST",
            self.api_url,
            headers={
                "Authorization": "Bearer {}".format(self.api_key),
            },
            json=input_
        )

        response.raise_for_status()

        return Output(answer=response.json()["choices"][0]["message"]["content"])
