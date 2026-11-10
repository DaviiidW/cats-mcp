"""MCP interface: server object, instructions and tools."""

from typing import Annotated, Any

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from cats_mcp import cats

INSTRUCTIONS = """\
This server runs CATS, a REST API fuzzer driven by OpenAPI contracts, to test the \
robustness and security of a running API.

# Recommended workflow

Each tool can be used on its own. When the user asks for one specific action, such as \
only validating the contract or only estimating the run size, call just the tools it \
needs. When the user asks to test their API without saying how, follow these steps in \
order:

1. Gather the inputs: the contract, the service URL and, if the API needs them, \
authentication headers and reference data.
2. Validate the contract with `cats_analyze_contract`. If it is invalid, fix it or ask \
the user before continuing.
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

CONTRACT_DESCRIPTION = (
    "Absolute path of the OpenAPI or Swagger contract of the API, in YAML or JSON. "
    "Look for files such as openapi.yaml, swagger.json or api-docs, often in the "
    "project root, docs/, api/ or src/main/resources/. If there is none, the "
    "framework may serve it from the running API (/openapi.json in FastAPI, "
    "/v3/api-docs in springdoc): pass that URL or save it to a file. Write a "
    "contract from the routes only as a last resort, and tell the user. If you find "
    "several contracts, ask the user which one to use. A relative path is resolved "
    "against the server's working directory."
)

Contract = Annotated[str, Field(description=CONTRACT_DESCRIPTION)]


@mcp.tool(annotations=ToolAnnotations(read_only_hint=True, idempotent_hint=True))
async def cats_analyze_contract(contract: Contract) -> dict[str, Any]:
    """Validate an OpenAPI contract with CATS (`cats validate`).

    Use it on its own when the user only wants to check a contract, or as the first
    step of the workflow (analyze, estimate, run) when the user asks to test their
    API. It sends no requests to the API, so you can call it without asking the user.

    Returns what CATS produced: `exit_code`, `stdout` and `stderr`. Exit code 0 means
    the contract is valid; if you are testing the API, continue with
    `cats_estimate_tests`. Exit code 1 means it is invalid or could not be read,
    which is a normal answer and not a failure of the tool: `stdout` holds a JSON
    document whose `reasons` list the problems (CATS may print a Java stack trace
    before it). If a reason says the file does not exist or is a directory, look
    for OpenAPI or Swagger files in the project or ask the user. Otherwise, fix the
    problems in the contract if it belongs to the project, or show them to the user
    and ask how to continue. If you are testing the API, do not estimate or run
    tests against an invalid contract. Any other exit code means CATS itself
    failed: check `stderr`.
    """
    try:
        result = await cats.run_cats(cats.validate_args(contract))
    except cats.CatsError as error:
        raise ToolError(str(error)) from error
    return {
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
