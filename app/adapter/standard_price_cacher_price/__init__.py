from abc import abstractmethod
from app.adapter import Adapter
from typing import TypedDict, List


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


class StandardPriceCacherPrice(Adapter):
    def phrase_input(self, request: Request) -> Input:
        print(request)
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
