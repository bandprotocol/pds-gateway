from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, Dict


class Adapter(ABC):
    @abstractmethod
    def parse_input(self, request: Dict[str, Any]) -> Any:
        """This function parses the data retrieved from the request.

        Args:
            request: The request response as a dictionary.

        Returns:
            A parsed set of data.
        """
        pass

    @abstractmethod
    def verify_output(self, input_: Any, output: Any) -> None:
        """This function verifies the adapter's output to assure a proper response can be given.

        If the output fails verification, this function should raise an exception.

        Args:
            input_: The request input data from BandChain.
            output: The output to be returned to the data source requestor.
        """
        pass

    @abstractmethod
    def parse_output(self, output: Any) -> Any:
        """This function parses the output retrieved from the adapter's set endpoint.

        Args:
            output: Output from the adapter's endpoint.

        Returns:
            The parsed output to be sent back to the data source.
        """
        pass

    @abstractmethod
    async def call(self, input_: Any) -> Any:
        """This function calls the adapter's set endpoint to retrieve the requested data.

        Args:
            input_: The input from request from the data source.

        Returns:
            The raw data from the adapter's endpoint.
        """
        pass

    async def unified_call(self, request: Dict[str, Any]) -> Any:
        input_ = self.parse_input(request)
        output = await self.call(input_)
        self.verify_output(input_, output)
        return self.parse_output(output)


def init_adapter(adapter_type: str, adapter_name: str) -> Adapter:
    # check adapter configuration
    if not adapter_type:
        raise Exception("MISSING 'ADAPTER_TYPE' ENV")
    if not adapter_name:
        raise Exception("MISSING 'ADAPTER_NAME' ENV")

    module = import_module(f"adapter.{adapter_type}.{adapter_name}".lower())
    AdapterClass = getattr(module, "".join([part.capitalize() for part in adapter_name.split("_")]))
    return AdapterClass()
