#!/usr/bin/env python3
"""Grading-framework-compatible assembler entry point."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rv32i_toolchain.assembler import assemble_file  # noqa: E402
from rv32i_toolchain.errors import ToolchainError  # noqa: E402


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print("Usage: python3 Assembler.py INPUT_ASM OUTPUT_BIN [READABLE_OUTPUT]")
        return 2
    try:
        assemble_file(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
    except (OSError, ToolchainError) as error:
        print(f"Assembler error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
