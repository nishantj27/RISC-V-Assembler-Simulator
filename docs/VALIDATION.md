# Validation report

Validation was performed against the supplied course material without modifying the golden files.

| Suite | Assembler | Simulator | Result |
|---|---:|---:|---|
| Automated unit tests | 6 tests | 6 tests | 12/12 passed |
| March 3 mid-evaluation framework | 10 fixtures | 5 legacy traces | All assembler encodings match; the legacy traces use an obsolete halt-PC convention |
| March 30 final framework | 10 fixtures | 10 traces | 20/20 passed through the official grader |
| April 4 shared framework | 4 fixtures | 13 traces | 4/4 assembler and 12/13 simulator passed |
| Standalone final test cases | 10 fixtures | — | 10/10 assembler encodings match |

The single April simulator mismatch is `hard_4.txt`. Its golden trace contains only 25 lines, stops before the program's halt, and has no required 32-line data-memory dump. The generated trace runs the program to its virtual halt and includes memory, so the project intentionally does not imitate that truncated fixture.

The older mid-evaluation trace files advance the PC from a virtual halt. The assignment defines virtual halt as `beq zero,zero,0`, and the final framework correctly keeps the PC unchanged. The implementation follows the instruction semantics and final framework.

## Reproduce the portable checks

```bash
python3 -m unittest discover -s tests -v
bash scripts/demo.sh /tmp/rv32i-demo
```

The original grading bundles are excluded from Git because they are course-provided material. Place them next to the project locally to repeat the official framework runs.
