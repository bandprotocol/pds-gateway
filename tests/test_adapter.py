import pytest
from adapter import init_adapter


@pytest.mark.asyncio
async def test_init_adapter():
    adapter = init_adapter("mock", "mock")

    assert adapter.phrase_input({}) == "mock_input"
    assert adapter.verify_output("", "")
    assert adapter.phrase_output({}) == "mock_output"
    assert await adapter.call({}) == "called"
