"""MCP interface: server object, instructions and tools."""

from mcp.server import MCPServer

INSTRUCTIONS = """\
This server runs CATS, a REST API fuzzer driven by OpenAPI contracts, to test the \
robustness and security of a running API.

# Recommended workflow

Follow these steps in order:

1. Gather the inputs: the contract, the service URL and, if the API needs them, \
authentication headers and reference data.
2. Analyze the contract with `cats_analyze_contract` to validate it and list its \
endpoints and methods. If it is invalid, fix it or ask the user before continuing.
3. Estimate the run size with `cats_estimate_tests`, which sends no requests. If the run \
is too large, narrow it with the `endpoints` and `methods` filters.
4. Start the run with `cats_run`. It runs in the background, and only one run can be \
active at a time.
5. Call `cats_status` until the run has finished. Use `cats_cancel` to stop it early.
6. Analyze the reports with your own file tools, using the absolute path that \
`cats_status` returns.

# Finding the inputs

Look in the project before asking the user:

- Contract: OpenAPI or Swagger files.
- Service URL: `servers` in the contract, `.env` files, `docker-compose.yml` and the \
framework configuration.
- Authentication headers and reference data: fixtures, seeds and tests.

Use the local URL by default. Ask the user if you only find remote URLs, or if there is \
ambiguity, such as several contracts or environments. Never use real secrets: if they \
are all you find, stop and ask the user.
"""

mcp = MCPServer("cats", instructions=INSTRUCTIONS)
