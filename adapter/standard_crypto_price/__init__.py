from abc import abstractmethod
from adapter import Adapter
from typing import TypedDict, List


class Input(TypedDict):
    symbols: List[str]


class Output(TypedDict):
    result: List[float]


class StandardCryptoPrice(Adapter):
    def phrase_input(self, request) -> Input:
        symbols = [symbol.strip() for symbol in request.args.get("symbols", {}).split(",")]
        return {"symbols": symbols}

    def phrase_output(self, output: Output):
        return output

    def verify_output(self, input: Input, output: Output):
        if len(input["symbols"]) != len(output["result"]):
            raise Exception(f"length of inputs and outputs are not the same.")

    @abstractmethod
    async def call(self, input: Input) -> Output:
        pass
