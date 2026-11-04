"""Entry point: starts the CATS MCP server over stdio."""

from cats_mcp.server import mcp


def main() -> None:
    # MCPServer configures logging to stderr; stdout is the protocol channel.
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
