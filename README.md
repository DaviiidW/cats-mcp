# cats-mcp

MCP server that lets an AI agent use [CATS](https://endava.github.io/cats/), a REST API fuzzer driven by OpenAPI contracts, to test the robustness and security of a running API.

## Prerequisites

- [uv](https://docs.astral.sh/uv/), which provides `uvx`. Python 3.10 or later.
- [CATS](https://endava.github.io/cats/) installed and available as `cats` on your `PATH`. This server does not install it; follow the [CATS installation guide](https://endava.github.io/cats/docs/getting-started/installation/). Check it with:

  ```sh
  cats --version
  ```

## Usage

No separate installation step is needed. Add this server to the MCP client you work with, following that client's documentation, and register it as a local stdio server with this command:

```sh
uvx --from git+https://github.com/DaviiidW/cats-mcp cats-mcp
```

To run it from a local clone instead:

```sh
uvx --from /path/to/cats-mcp cats-mcp
```

The client starts the server whenever it needs it, and `uvx` builds it from the repository the first time.

## Development

```sh
uv sync
uv run pytest
```
