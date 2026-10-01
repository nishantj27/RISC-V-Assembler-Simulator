"""Instruction-level simulator for the assignment's RV32I subset."""

from __future__ import annotations

from pathlib import Path

from .errors import SimulationError
from .isa import DATA_BASE, DATA_WORDS, INITIAL_SP, MASK32, VIRTUAL_HALT, sign_extend, signed, u32


class Simulator:
    def __init__(self, words: list[int], *, max_steps: int = 100_000) -> None:
        self.words = words
        self.max_steps = max_steps
        self.pc = 0
        self.registers = [0] * 32
        self.registers[2] = INITIAL_SP
        self.memory: dict[int, int] = {}
        self.trace: list[str] = []
        self.readable_trace: list[str] = []

    @classmethod
    def from_text(cls, machine_code: str, *, max_steps: int = 100_000) -> "Simulator":
        words: list[int] = []
        for line_number, raw in enumerate(machine_code.splitlines(), start=1):
            text = raw.strip()
            if not text:
                continue
            if len(text) != 32 or any(ch not in "01" for ch in text):
                raise SimulationError("expected exactly 32 binary digits", line=line_number)
            words.append(int(text, 2))
        if not words:
            raise SimulationError("the machine-code file is empty")
        return cls(words, max_steps=max_steps)

    def run(self) -> tuple[str, str]:
        halted = False
        for _ in range(self.max_steps):
            word = self._fetch()
            self._execute(word)
            self.registers[0] = 0
            self._record()
            if word in {VIRTUAL_HALT, 0x0010000B}:
                halted = True
                break
        if not halted:
            raise SimulationError(f"program did not halt within {self.max_steps} instructions")

        binary_memory = []
        readable_memory = []
        for index in range(DATA_WORDS):
            address = DATA_BASE + index * 4
            value = self.memory.get(address, 0)
            binary_memory.append(f"0x{address:08X}:0b{value:032b}\n")
            readable_memory.append(f"0x{address:08X}:{value}\n")
        return "".join(self.trace + binary_memory), "".join(self.readable_trace + readable_memory)

    def _fetch(self) -> int:
        if self.pc & 0b11:
            raise SimulationError(f"misaligned program counter 0x{self.pc:08X}")
        index = self.pc // 4
        if index < 0 or index >= len(self.words):
            raise SimulationError(f"program counter 0x{self.pc:08X} is outside instruction memory")
        return self.words[index]

    def _execute(self, word: int) -> None:
        opcode = word & 0x7F
        rd = (word >> 7) & 0x1F
        funct3 = (word >> 12) & 0x7
        rs1 = (word >> 15) & 0x1F
        rs2 = (word >> 20) & 0x1F
        funct7 = (word >> 25) & 0x7F
        next_pc = u32(self.pc + 4)

        if opcode == 0b0110011:
            left, right = self.registers[rs1], self.registers[rs2]
            operation = (funct7, funct3)
            if operation == (0b0000000, 0b000):
                result = left + right
            elif operation == (0b0100000, 0b000):
                result = left - right
            elif operation == (0b0000000, 0b001):
                result = left << (right & 0x1F)
            elif operation == (0b0000000, 0b010):
                result = int(signed(left) < signed(right))
            elif operation == (0b0000000, 0b011):
                result = int(left < right)
            elif operation == (0b0000000, 0b100):
                result = left ^ right
            elif operation == (0b0000000, 0b101):
                result = left >> (right & 0x1F)
            elif operation == (0b0000000, 0b110):
                result = left | right
            elif operation == (0b0000000, 0b111):
                result = left & right
            elif operation == (0b0000001, 0b000):
                result = signed(left) * signed(right)
            else:
                self._illegal(word)
            self._write(rd, result)

        elif opcode == 0b0010011:
            imm = sign_extend(word >> 20, 12)
            if funct3 == 0b000:
                self._write(rd, self.registers[rs1] + imm)
            elif funct3 == 0b011:
                self._write(rd, int(self.registers[rs1] < u32(imm)))
            else:
                self._illegal(word)

        elif opcode == 0b0000011 and funct3 == 0b010:
            imm = sign_extend(word >> 20, 12)
            address = u32(self.registers[rs1] + imm)
            self._write(rd, self.memory.get(address, 0))

        elif opcode == 0b0100011 and funct3 == 0b010:
            imm = (((word >> 25) & 0x7F) << 5) | ((word >> 7) & 0x1F)
            address = u32(self.registers[rs1] + sign_extend(imm, 12))
            self.memory[address] = self.registers[rs2]

        elif opcode == 0b1100011:
            imm = (
                (((word >> 31) & 1) << 12)
                | (((word >> 25) & 0x3F) << 5)
                | (((word >> 8) & 0xF) << 1)
                | (((word >> 7) & 1) << 11)
            )
            left, right = self.registers[rs1], self.registers[rs2]
            conditions = {
                0b000: left == right,
                0b001: left != right,
                0b100: signed(left) < signed(right),
                0b101: signed(left) >= signed(right),
                0b110: left < right,
                0b111: left >= right,
            }
            if funct3 not in conditions:
                self._illegal(word)
            if conditions[funct3]:
                next_pc = u32(self.pc + sign_extend(imm, 13))

        elif opcode == 0b1101111:
            imm = (
                (((word >> 31) & 1) << 20)
                | (((word >> 21) & 0x3FF) << 1)
                | (((word >> 20) & 1) << 11)
                | (((word >> 12) & 0xFF) << 12)
            )
            self._write(rd, self.pc + 4)
            next_pc = u32(self.pc + sign_extend(imm, 21))

        elif opcode == 0b1100111 and funct3 == 0b000:
            imm = sign_extend(word >> 20, 12)
            target = u32(self.registers[rs1] + imm) & ~1
            self._write(rd, self.pc + 4)
            next_pc = target

        elif opcode == 0b0110111:
            self._write(rd, word & 0xFFFFF000)

        elif opcode == 0b0010111:
            self._write(rd, self.pc + (word & 0xFFFFF000))

        elif opcode == 0b0001011:
            if word == 0x0000000B:  # rst
                for index in range(1, 32):
                    self.registers[index] = 0
            elif word == 0x0010000B:  # halt
                pass
            elif funct3 == 0b001 and funct7 == 0 and rs2 == 0:  # rvrs
                self._write(rd, int(f"{self.registers[rs1]:032b}"[::-1], 2))
            else:
                self._illegal(word)
        else:
            self._illegal(word)

        self.pc = next_pc

    def _write(self, register: int, value: int) -> None:
        if register != 0:
            self.registers[register] = u32(value)

    def _illegal(self, word: int) -> None:
        raise SimulationError(f"illegal instruction 0b{word:032b} at PC 0x{self.pc:08X}")

    def _record(self) -> None:
        values = [self.pc, *self.registers]
        self.trace.append(" ".join(f"0b{value:032b}" for value in values) + " \n")
        self.readable_trace.append(" ".join(str(value) for value in values) + " \n")


def simulate_file(input_path: str | Path, output_path: str | Path, readable_path: str | Path | None = None) -> None:
    simulator = Simulator.from_text(Path(input_path).read_text(encoding="utf-8"))
    binary_trace, readable_trace = simulator.run()
    Path(output_path).write_text(binary_trace, encoding="utf-8")
    if readable_path is not None:
        Path(readable_path).write_text(readable_trace, encoding="utf-8")
