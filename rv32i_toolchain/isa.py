"""Constants and bit-level helpers shared by both tools."""

from __future__ import annotations

MASK32 = 0xFFFF_FFFF
DATA_BASE = 0x0001_0000
DATA_WORDS = 32
INITIAL_SP = 380
VIRTUAL_HALT = 0x0000_0063  # beq zero,zero,0

REGISTER_NAMES = {
    "zero": 0,
    "ra": 1,
    "sp": 2,
    "gp": 3,
    "tp": 4,
    "t0": 5,
    "t1": 6,
    "t2": 7,
    "s0": 8,
    "fp": 8,
    "s1": 9,
    "a0": 10,
    "a1": 11,
    "a2": 12,
    "a3": 13,
    "a4": 14,
    "a5": 15,
    "a6": 16,
    "a7": 17,
    "s2": 18,
    "s3": 19,
    "s4": 20,
    "s5": 21,
    "s6": 22,
    "s7": 23,
    "s8": 24,
    "s9": 25,
    "s10": 26,
    "s11": 27,
    "t3": 28,
    "t4": 29,
    "t5": 30,
    "t6": 31,
}
REGISTER_NAMES.update({f"x{i}": i for i in range(32)})


def u32(value: int) -> int:
    return value & MASK32


def signed(value: int, bits: int = 32) -> int:
    value &= (1 << bits) - 1
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


def sign_extend(value: int, bits: int) -> int:
    return signed(value, bits)


def bits(value: int, width: int) -> str:
    return f"{value & ((1 << width) - 1):0{width}b}"


def encode_r(funct7: int, rs2: int, rs1: int, funct3: int, rd: int, opcode: int) -> int:
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def encode_i(imm: int, rs1: int, funct3: int, rd: int, opcode: int) -> int:
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def encode_s(imm: int, rs2: int, rs1: int, funct3: int, opcode: int) -> int:
    value = imm & 0xFFF
    return ((value >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | ((value & 0x1F) << 7) | opcode


def encode_b(imm: int, rs2: int, rs1: int, funct3: int, opcode: int = 0b1100011) -> int:
    value = imm & 0x1FFF
    return (
        (((value >> 12) & 1) << 31)
        | (((value >> 5) & 0x3F) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (((value >> 1) & 0xF) << 8)
        | (((value >> 11) & 1) << 7)
        | opcode
    )


def encode_u(imm: int, rd: int, opcode: int) -> int:
    return (imm & 0xFFFFF000) | (rd << 7) | opcode


def encode_j(imm: int, rd: int, opcode: int = 0b1101111) -> int:
    value = imm & 0x1FFFFF
    return (
        (((value >> 20) & 1) << 31)
        | (((value >> 1) & 0x3FF) << 21)
        | (((value >> 11) & 1) << 20)
        | (((value >> 12) & 0xFF) << 12)
        | (rd << 7)
        | opcode
    )
