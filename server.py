import logging
from mcp.server.fastmcp import FastMCP


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


mcp = FastMCP("cats_mcp")


if __name__ == "__main__":
    mcp.run()