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
    seed: int


class Input(TypedDict):
    model: str
    messages: str
    max_tokens: int
    stream: bool
    temperature: float
    top_p: float
    seed: int


class Output(TypedDict):
    answer: str


class Response(TypedDict):
    answer: str


class OpenAI(Adapter):
    api_url: str = "https://api.openai.com/v1/chat/completions"
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
            json={
                "model": input_["model"],
                "messages": [{
                    "role": "user",
                    "content": input_["messages"],
                }],
                "temperature": float(input_["temperature"]),
                "top_p": float(input_["top_p"]),
                "max_tokens": int(input_["max_tokens"]),
                "stream": True if input_["stream"] == "true" else False,
                "seed": int(input_["seed"]),
            }
        )

        response.raise_for_status()

        return Output(answer=response.json()["choices"][0]["message"]["content"])
