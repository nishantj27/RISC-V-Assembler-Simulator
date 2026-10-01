# Architecture

The project deliberately separates instruction definitions, translation, and execution. This makes encoding bugs distinguishable from simulation bugs and keeps both command-line wrappers compatible with the supplied grader.

```text
assembly source
      |
      v
two-pass parser ----> symbol table (label -> byte address)
      |
      v
instruction encoder ----> 32-bit machine-code file
                                  |
                                  v
                           fetch / decode / execute
                                  |
                    +-------------+-------------+
                    |                           |
               register file              sparse memory
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                         execution trace file
```

## Assembler

The first pass removes blank lines and comments, records labels, and assigns each instruction a byte address in four-byte increments. The second pass validates operands and immediates, resolves PC-relative labels, and packs fields into the R, I, S, B, U, or J format.

The CLI writes the binary output only after the entire program assembles successfully, so a syntax error cannot leave a partially valid machine-code file.

## Simulator

The simulator maintains a 32-entry register file, a byte-addressed sparse memory dictionary, and a byte-addressed program counter. Every write is masked to 32 bits. Signed operations reinterpret a stored unsigned bit pattern only at comparison time.

Execution is a fetch/decode/execute loop. After each instruction—including halt—the simulator records the PC and all 32 registers. It then emits the 32 required data-memory locations from `0x00010000` through `0x0001007C`.

## Course-specific compatibility

- `sp` (`x2`) starts at decimal 380 because that is what the supplied golden traces require.
- The course accepts byte addresses not divisible by four for `lw` and `sw`; sparse memory therefore preserves the exact effective address.
- The virtual halt is the exact instruction `beq zero,zero,0`, which leaves the PC unchanged.
- Some provided files define code after a virtual halt and some reuse labels. For compatibility, at least one halt is required and the first label definition wins.
- U-type source operands are treated as full 32-bit values. For example, `lui s0,65536` writes `0x00010000`, matching the assignment examples.

## Bonus extension encoding

The PDF names bonus operations but does not assign their bit patterns. This implementation documents a deterministic extension:

| Instruction | Encoding choice |
|---|---|
| `mul rd,rs1,rs2` | Standard RISC-V M-extension encoding |
| `rst` | Custom-0 opcode, word `0x0000000B` |
| `halt` | Custom-0 opcode, word `0x0010000B` |
| `rvrs rd,rs1` | Custom-0, `funct3=001`, `rs2=0`; reverses all 32 bits |

These choices do not overlap the required RV32I subset.
