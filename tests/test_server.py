from mcp import Client

from cats_mcp.server import mcp


async def test_client_connects_to_server() -> None:
    async with Client(mcp) as client:
        assert client.server_info.name == "cats"
