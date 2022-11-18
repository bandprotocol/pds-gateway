from abc import ABC, abstractmethod
from fastapi import Request


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
