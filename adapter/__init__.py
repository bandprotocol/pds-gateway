from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Dict


class Adapter(ABC):
    @abstractmethod
    def phrase_input(self, request: Dict):
        pass

    @abstractmethod
    def verify_output(self, input: Any, output: Any):
        pass

    @abstractmethod
    def phrase_output(self, output: Any):
        pass

    @abstractmethod
    async def call(self, input: Any):
        pass

    async def unified_call(self, request: Dict):
        input = self.phrase_input(request)
        output = await self.call(input)
        self.verify_output(input, output)
        return self.phrase_output(output)


def init_adapter(adapter_type: str, adapter_name: str) -> Adapter:
    # check adapter configuration
    if not adapter_type:
        raise Exception("MISSING 'ADAPTER_TYPE' ENV")
    if not adapter_name:
        raise Exception("MISSING 'ADAPTER_NAME' ENV")

    module = import_module(f"adapter.{adapter_type}.{adapter_name}".lower())
    AdapterClass = getattr(module, "".join([part.capitalize() for part in adapter_name.split("_")]))
    return AdapterClass()
