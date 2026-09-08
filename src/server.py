from mcp.server import MCPServer

mcp = MCPServer(name="cats_mcp")

@mcp.tool()
def ping() -> str:
    """Tool de prueba, para verificar que el servidor responde."""
    return "pong"

if __name__ == "__main__":
    mcp.run(transport="stdio")