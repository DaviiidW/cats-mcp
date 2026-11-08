"""CATS adapter: commands, subprocess, output and exit codes."""

from collections.abc import Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
from subprocess import DEVNULL, PIPE

import anyio
from anyio.abc import ByteReceiveStream, Process
from anyio.streams.text import TextReceiveStream


BINARY_NAME = "cats.exe" if os.name == "nt" else "cats"

EXIT_CODE_MEANINGS = {
    0: "Success: CATS finished and reported no errors.",
    1: (
        "CATS finished and reported errors. In a run this normally means it found "
        "problems in the API, which is an expected result and not a failure of the "
        "tool. CATS also uses this code for an invalid contract, an unreachable "
        "service and filters that match nothing, so check the output."
    ),
    2: (
        "Invalid arguments: CATS rejected the command. Check the output for the "
        "offending option, correct it and try again."
    ),
}

PROFILES = ("quick", "security", "compliance", "ci", "full")


class CatsError(Exception):
    """A problem the agent can fix; the message says how."""

class CatsNotFoundError(CatsError):
    """The CATS binary could not be located."""


@dataclass(frozen=True)
class CatsResult:
    exit_code: int
    meaning: str
    stdout: str
    stderr: str
    command: list[str]


def find_cats() -> Path:
    configured = os.environ.get("CATS_PATH")
    if configured:
        path = _absolute_path(configured)
        if not path.is_file():
            raise CatsNotFoundError(
                f"CATS_PATH points to '{path}', which is not an existing "
                "file. Set CATS_PATH to the full path of the CATS binary, "
                f"or unset it to look for '{BINARY_NAME}' on the PATH."
            )
        return path

    found = shutil.which(BINARY_NAME)
    if found is None:
        raise CatsNotFoundError(
            f"CATS was not found: '{BINARY_NAME}' is not on the PATH. Install CATS "
            "(https://endava.github.io/cats/) and add it to the PATH, or set "
            "CATS_PATH to the full path of the binary."
        )
    return _absolute_path(found)

def describe_exit_code(exit_code: int) -> str:
    return EXIT_CODE_MEANINGS.get(
        exit_code,
        f"Unexpected exit code {exit_code}: CATS crashed or was stopped before it "
        "finished. Check the output.",
    )

async def run_cats(args: Sequence[str]) -> CatsResult:
    command = [str(find_cats()), *args]
    try:
        process = await anyio.open_process(
            command, stdin=DEVNULL, stdout=PIPE, stderr=PIPE
        )
    except OSError as error:
        raise CatsError(
            f"Could not start CATS at '{command[0]}': {error}. Check that it is the "
            "native CATS binary and that it is executable, or set "
            "CATS_PATH to a valid one."
        ) from error

    stdout: list[str] = []
    stderr: list[str] = []
    async with process:
        try:
            async with anyio.create_task_group() as readers:
                readers.start_soon(_read_stream, process.stdout, stdout)
                readers.start_soon(_read_stream, process.stderr, stderr)
            exit_code = await process.wait()
        except BaseException:
            await _stop_process(process)
            raise

    return CatsResult(
        exit_code=exit_code,
        meaning=describe_exit_code(exit_code),
        stdout="".join(stdout),
        stderr="".join(stderr),
        command=command,
    )

def validate_args(contract: str) -> list[str]:
    return ["validate", _contract_option(contract), "--detailed", "--json"]

def list_paths_args(contract: str) -> list[str]:
    return ["list", "--paths", _contract_option(contract), "--json"]

def path_details_args(contract: str, path: str) -> list[str]:
    return ["list", "--paths", f"--path={path}", _contract_option(contract), "--json"]

def estimate_args(
    contract: str,
    url: str,
    profile: str,
    endpoints: Sequence[str] | None = None,
    methods: Sequence[str] | None = None,
) -> list[str]:
    return [*_fuzzing_args(contract, url, profile, endpoints, methods), "--dryRun"]

def run_args(
    contract: str,
    url: str,
    profile: str,
    endpoints: Sequence[str] | None = None,
    methods: Sequence[str] | None = None,
    headers: Mapping[str, str] | None = None,
    ref_data: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> list[str]:
    args = _fuzzing_args(contract, url, profile, endpoints, methods)
    headers = headers or {}
    for name, value in headers.items():
        args += ["-H", f"{name}={value}"]
    masked = dict.fromkeys(["Authorization", *headers])
    args.append(f"--maskHeaders={','.join(masked)}")
    if ref_data is not None:
        args.append(f"--refData={_absolute_path(ref_data)}")
    if output_dir is not None:
        args += ["-o", str(_absolute_path(output_dir))]
    return args

def _fuzzing_args(
    contract: str,
    url: str,
    profile: str,
    endpoints: Sequence[str] | None,
    methods: Sequence[str] | None,
) -> list[str]:
    if profile not in PROFILES:
        raise CatsError(
            f"Invalid profile: '{profile}'. Allowed values: {', '.join(PROFILES)}. "
        )
    args = [
        _contract_option(contract),
        f"--server={url}",
        f"--profile={profile}",
        "--no-color",
        "--no-checkUpdate",
    ]
    if endpoints:
        args.append(f"--paths={','.join(endpoints)}")
    if methods:
        args.append(f"--httpMethods={','.join(methods)}")
    return args

def _contract_option(contract: str) -> str:
    location = contract if "://" in contract else _absolute_path(contract)
    return f"--contract={location}"

def _absolute_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()

async def _read_stream(stream: ByteReceiveStream, chunks: list[str]) -> None:
    async for chunk in TextReceiveStream(stream, errors="replace"):
        chunks.append(chunk)

async def _stop_process(process: Process) -> None:
    with anyio.CancelScope(shield=True):
        with suppress(ProcessLookupError):
            process.terminate()
        with anyio.move_on_after(5):
            await process.wait()
        with suppress(ProcessLookupError):
            process.kill()
        await process.wait()
