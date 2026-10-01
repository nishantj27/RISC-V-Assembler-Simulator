# RISC-V32I Assembler and Simulator

A dependency-free Python implementation of the Computer Organization project. It translates a practical RV32I subset from assembly into 32-bit machine code, executes that code, and emits the exact register/memory trace format expected by the supplied course frameworks.

## What is included

- A two-pass assembler with forward/backward label resolution
- R, I, S, B, U, and J instruction encoders
- An instruction-level simulator with 32 registers, 32-bit wraparound, control flow, and sparse memory
- Clear line-numbered diagnostics for malformed source and machine code
- Grader-compatible two-argument and three-argument CLIs
- Bonus `mul`, `rst`, `halt`, and `rvrs` instructions
- Unit tests, a Fibonacci example, architecture notes, and validation documentation.

## Supported instructions

| Format | Instructions |
|---|---|
| R | `add`, `sub`, `sll`, `slt`, `sltu`, `xor`, `srl`, `or`, `and`, `mul` |
| I | `addi`, `sltiu`, `lw`, `jalr` |
| S | `sw` |
| B | `beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu` |
| U | `lui`, `auipc` |
| J | `jal` |
| Custom bonus | `rst`, `halt`, `rvrs` |

Both ABI register names (`zero`, `ra`, `sp`, `a0`, `s0`, and so on) and numeric names (`x0`–`x31`) are accepted.

## Quick start

Requires Python 3.10 or newer; no third-party packages are needed.

```bash
python3 SimpleAssembler/Assembler.py examples/fibonacci.asm /tmp/fibonacci.bin
python3 SimpleSimulator/Simulator.py /tmp/fibonacci.bin /tmp/fibonacci.trace
```

Add a third path to either command to produce a human-readable companion file:

```bash
python3 SimpleAssembler/Assembler.py examples/fibonacci.asm /tmp/fibonacci.bin /tmp/instructions.txt
python3 SimpleSimulator/Simulator.py /tmp/fibonacci.bin /tmp/fibonacci.trace /tmp/trace.txt
```

Or run the complete demo:

```bash
bash scripts/demo.sh
```

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

The implementation was also checked against all machine-code goldens in the supplied mid-semester and March final frameworks, and against all March final simulator traces.


## Project stages

- **Mid-semester deliverable:** assembler, label resolution, validation, and binary output.
- **Final deliverable:** simulator, register and memory traces, complete control flow, broader tested instruction subset, and bonus operations.

See [the architecture notes](docs/ARCHITECTURE.md) for design decisions and course-specific behavior, [the validation report](docs/VALIDATION.md) for the exact test results.

## Scope

This is an educational functional simulator, not a cycle-accurate CPU model. It does not model a pipeline, cache hierarchy, interrupts, privilege levels, or the complete RISC-V specification.
