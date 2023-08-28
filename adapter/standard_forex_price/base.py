from abc import abstractmethod
from typing import TypedDict, List, Dict

from adapter import Adapter


class Price(TypedDict):
    symbol: str
    price: float
    timestamp: int


class Request(TypedDict):
    symbols: str


class Input(TypedDict):
    symbols: List[str]


class Output(TypedDict):
    prices: List[Price]


class Response(TypedDict):
    prices: List[Price]


class StandardForexPrice(Adapter):
    def parse_input(self, request: Dict) -> Input:
        symbols = [symbol.strip() for symbol in request.get("symbols", "").split(",")]
        return Input(symbols=symbols)

    def verify_output(self, input_: Input, output: Output):
        if len(input_["symbols"]) != len(output["prices"]):
            raise Exception(f"length of inputs and outputs are not the same.")

    def parse_output(self, output: Output) -> Response:
        return Response(prices=output["prices"])

    @abstractmethod
    async def call(self, input_: Input) -> Output:
        pass
