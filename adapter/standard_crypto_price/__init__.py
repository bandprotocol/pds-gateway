from abc import abstractmethod
from adapter import Adapter
from typing import TypedDict, List


class Request(TypedDict):
    symbols: str


class Input(TypedDict):
    symbols: List[str]


class Output(TypedDict):
    rates: List[float]


class Response(TypedDict):
    rates: str


class StandardCryptoPrice(Adapter):
    def phrase_input(self, request: Request) -> Input:
        symbols = [symbol.strip() for symbol in request.get("symbols", "").split(",")]
        return Input(symbols=symbols)

    def verify_output(self, input: Input, output: Output):
        if len(input["symbols"]) != len(output["rates"]):
            raise Exception(f"length of inputs and outputs are not the same.")

    def phrase_output(self, output: Output) -> Response:
        return Response(rates=",".join([str(rate) for rate in output["rates"]]))

    @abstractmethod
    async def call(self, input: Input) -> Output:
        pass
