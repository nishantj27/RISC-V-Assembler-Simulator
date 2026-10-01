#!/usr/bin/env python3
"""Grading-framework-compatible simulator entry point."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rv32i_toolchain.errors import ToolchainError  # noqa: E402
from rv32i_toolchain.simulator import simulate_file  # noqa: E402


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print("Usage: python3 Simulator.py INPUT_BIN OUTPUT_TRACE [READABLE_OUTPUT]")
        return 2
    try:
        simulate_file(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
    except (OSError, ToolchainError) as error:
        print(f"Simulator error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
