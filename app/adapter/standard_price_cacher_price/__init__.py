from abc import abstractmethod
from dataclasses import dataclass
from app.adapter import Adapter
from typing import TypedDict, List


@dataclass
class Price(TypedDict):
    symbol: str
    price: float
    timestamp: int


@dataclass
class Request(TypedDict):
    source: str
    symbols: str


@dataclass
class Input(TypedDict):
    source: str
    symbols: List[str]


@dataclass
class Output(TypedDict):
    prices: List[Price]


@dataclass
class Response(TypedDict):
    prices: List[Price]


class StandardPriceCacherPrice(Adapter):
    def phrase_input(self, request: Request) -> Input:
        symbols = [symbol.strip() for symbol in request.get("symbols", "").split(",")]
        return Input(source=request.get("source", ""), symbols=symbols)

    def verify_output(self, input: Input, output: Output):
        if len(input["symbols"]) != len(output["prices"]):
            raise Exception(f"length of inputs and outputs are not the same.")

    def phrase_output(self, output: Output) -> Response:
        return Response(output)

    @abstractmethod
    async def call(self, input: Input) -> Output:
        pass
