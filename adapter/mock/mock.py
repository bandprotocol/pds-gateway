from typing import Any

from adapter import Adapter


class Mock(Adapter):
    def parse_input(self, _) -> Any:
        return "mock_input"

    def verify_output(self, input_: str, output: str) -> None:
        pass

    def parse_output(self, _) -> Any:
        return "mock_output"

    async def call(self, _) -> Any:
        return "called"
