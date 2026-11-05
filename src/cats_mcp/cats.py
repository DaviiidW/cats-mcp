"""CATS adapter: commands, subprocess, output and exit codes."""

from dataclasses import dataclass


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

@dataclass(frozen=True)
class CatsResult:
    exit_code: int
    meaning: str
    stdout: str
    stderr: str
    command: list[str]

