import unittest

from rv32i_toolchain.assembler import Assembler
from rv32i_toolchain.errors import SimulationError
from rv32i_toolchain.isa import DATA_BASE
from rv32i_toolchain.simulator import Simulator


def assembled(source: str) -> list[int]:
    return Assembler().assemble(source)[0]


class SimulatorTests(unittest.TestCase):
    def test_arithmetic_branch_and_zero_register(self) -> None:
        words = assembled(
            """\
addi t0,zero,7
addi t1,zero,-2
add t2,t0,t1
sub zero,t0,t1
blt t1,t0,done
addi t2,zero,99
done: beq zero,zero,0
"""
        )
        simulator = Simulator(words)
        binary, _ = simulator.run()
        self.assertEqual(simulator.registers[0], 0)
        self.assertEqual(simulator.registers[7], 5)
        self.assertEqual(simulator.pc, 24)
        self.assertEqual(len(binary.splitlines()), 6 + 32)

    def test_load_store_and_32_bit_wraparound(self) -> None:
        words = assembled(
            """\
lui s0,65536
addi t0,zero,-1
sw t0,0(s0)
lw t1,0(s0)
addi t1,t1,1
beq zero,zero,0
"""
        )
        simulator = Simulator(words)
        simulator.run()
        self.assertEqual(simulator.memory[DATA_BASE], 0xFFFF_FFFF)
        self.assertEqual(simulator.registers[6], 0)

    def test_jal_and_jalr_link_registers(self) -> None:
        words = assembled(
            """\
jal ra,routine
beq zero,zero,0
routine: jalr zero,0(ra)
beq zero,zero,0
"""
        )
        simulator = Simulator(words)
        simulator.run()
        self.assertEqual(simulator.registers[1], 4)
        self.assertEqual(simulator.pc, 4)

    def test_custom_bonus_instructions(self) -> None:
        words = assembled(
            """\
addi t0,zero,6
addi t1,zero,7
mul t2,t0,t1
rvrs a0,t2
rst
halt
"""
        )
        simulator = Simulator(words)
        simulator.run()
        self.assertEqual(simulator.registers, [0] * 32)

    def test_malformed_machine_code_is_rejected(self) -> None:
        with self.assertRaisesRegex(SimulationError, "line 1"):
            Simulator.from_text("10101\n")

    def test_infinite_loop_has_step_guard(self) -> None:
        simulator = Simulator([0x0000006F], max_steps=3)  # jal zero,0
        with self.assertRaisesRegex(SimulationError, "did not halt"):
            simulator.run()


if __name__ == "__main__":
    unittest.main()
