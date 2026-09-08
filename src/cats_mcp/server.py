from mcp.server import MCPServer

mcp = MCPServer(name="cats_mcp")


@mcp.tool()
def ping() -> str:
    """Tool de prueba, para verificar que el servidor responde."""
    return "pong"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()