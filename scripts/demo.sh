#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
output_dir=${1:-/tmp/rv32i-demo}
mkdir -p "$output_dir"

python3 "$project_dir/SimpleAssembler/Assembler.py" \
  "$project_dir/examples/fibonacci.asm" \
  "$output_dir/fibonacci.bin" \
  "$output_dir/fibonacci.instructions.txt"

python3 "$project_dir/SimpleSimulator/Simulator.py" \
  "$output_dir/fibonacci.bin" \
  "$output_dir/fibonacci.trace" \
  "$output_dir/fibonacci.readable.txt"

echo "Demo outputs written to $output_dir"
