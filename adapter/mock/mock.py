from adapter import Adapter


class Mock(Adapter):
    def phrase_input(self, _) -> str:
        return "mock_input"

    def verify_output(self, input: str, output: str):
        return True

    def phrase_output(self, _) -> str:
        return "mock_output"

    async def call(self, _) -> str:
        return "called"
