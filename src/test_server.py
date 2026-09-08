import pytest
from mcp import Client
from mcp.types import TextContent

from server import mcp


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with Client(mcp, raise_exceptions=True) as c:
        yield c


@pytest.mark.anyio
async def test_ping(client: Client):
    result = await client.call_tool("ping", {})
    content = result.content[0]

    assert isinstance(content, TextContent)
    assert content.text == "pong"