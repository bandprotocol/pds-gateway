import pytest
from adapter import init_adapter


@pytest.mark.asyncio
async def test_init_adapter():
    adapter = init_adapter("mock", "mock")

    assert adapter.parse_input({}) == "mock_input"
    adapter.verify_output("", "")
    assert adapter.parse_output({}) == "mock_output"
    assert await adapter.call({}) == "called"
