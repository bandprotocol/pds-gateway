from abc import ABC, abstractmethod
from fastapi import Request
from app.utils import helper


class Adapter(ABC):
    @abstractmethod
    def phrase_input(self, request: Request):
        return request.args

    @abstractmethod
    def phrase_output(self, output):
        return output

    @abstractmethod
    def verify_output(self, input, output):
        pass

    @abstractmethod
    async def call(self, input):
        pass

    async def unified_call(self, request: Request):
        input = self.phrase_input(dict(request.query_params))
        output = await self.call(input)
        self.verify_output(input, output)
        return self.phrase_output(output)


def init_adapter(adapter_type: str, adapter_name: str) -> Adapter:
    # check adapter configuration
    if not adapter_type:
        raise Exception("MISSING 'ADAPTER_TYPE' ENV")
    if not adapter_name:
        raise Exception("MISSING 'ADAPTER_NAME' ENV")

    return helper.get_adapter(adapter_type, adapter_name)
