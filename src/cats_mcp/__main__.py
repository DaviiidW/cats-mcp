"""Entry point: starts the CATS MCP server over stdio."""

import logging
import sys

from cats_mcp.server import mcp


def main() -> None:
    # stdout is the protocol channel, so logs must go to stderr.
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
