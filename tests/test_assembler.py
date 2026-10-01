import unittest

from rv32i_toolchain.assembler import Assembler
from rv32i_toolchain.errors import AssemblyError


class AssemblerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assembler = Assembler()

    def words(self, source: str) -> list[str]:
        words, _ = self.assembler.assemble(source)
        return [f"{word:032b}" for word in words]

    def test_core_instruction_formats(self) -> None:
        source = """\
add s1,s2,s3
addi a0,zero,-5
lw a4,20(s1)
sw ra,32(sp)
blt a4,a5,8
jal ra,-4
beq zero,zero,0
"""
        self.assertEqual(
            self.words(source),
            [
                "00000001001110010000010010110011",
                "11111111101100000000010100010011",
                "00000001010001001010011100000011",
                "00000010000100010010000000100011",
                "00000000111101110100010001100011",
                "11111111110111111111000011101111",
                "00000000000000000000000001100011",
            ],
        )

    def test_forward_and_backward_labels(self) -> None:
        source = """\
start: addi t0,zero,1
beq t0,zero,end
jal zero,start
end: beq zero,zero,0
"""
        words, _ = self.assembler.assemble(source)
        self.assertEqual(words[1], 0x00028463)  # +8
        self.assertEqual(words[2], 0xFF9FF06F)  # -8

    def test_numeric_registers_and_comments(self) -> None:
        source = "addi x5,x0,0x10 # hexadecimal\nbeq x0,x0,0\n"
        words, _ = self.assembler.assemble(source)
        self.assertEqual(words, [0x01000293, 0x00000063])

    def test_missing_halt_is_rejected_with_line_number(self) -> None:
        with self.assertRaisesRegex(AssemblyError, r"line 1: missing virtual halt"):
            self.assembler.assemble("add s1,s2,s3\n")

    def test_bad_register_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssemblyError, r"line 1: unknown register 'r9'"):
            self.assembler.assemble("add r9,s2,s3\nbeq zero,zero,0\n")

    def test_out_of_range_immediate_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssemblyError, "outside"):
            self.assembler.assemble("addi a0,zero,2048\nbeq zero,zero,0\n")


if __name__ == "__main__":
    unittest.main()
