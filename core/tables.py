from dataclasses import dataclass

@dataclass
class Line:
    label: str | None
    Instruction: str
    opcode: Opcode | None   # optional if it is actually an opcode, None if it is a directive
    operand: str | None
    object_code: str | None
    location_counter: int | None
    block: str | None

    def __str__(self):
        return f"{self.location_counter}\t{self.label if self.label else ''}\t{self.Instruction}\t{self.operand}\t\t{self.object_code}" # type: ignore

@dataclass
class Opcode:
    mnemonic: str
    format: int
    opcode: int

OPCODES = {
    "ADD": Opcode("ADD", 3, 0x18),
    "ADDF": Opcode("ADDF", 3, 0x58),
    "ADDR": Opcode("ADDR", 2, 0x90),
    "AND": Opcode("AND", 3, 0x40),
    "CLEAR": Opcode("CLEAR", 2, 0xB4),
    "COMP": Opcode("COMP", 3, 0x28),
    "COMPF": Opcode("COMPF", 3, 0x88),
    "COMPR": Opcode("COMPR", 2, 0xA0),
    "DIV": Opcode("DIV", 3, 0x24),
    "DIVF": Opcode("DIVF", 3, 0x64),
    "DIVR": Opcode("DIVR", 2, 0x9C),
    "FIX": Opcode("FIX", 1, 0xC4),
    "FLOAT": Opcode("FLOAT", 1, 0xC0),
    "HIO": Opcode("HIO", 1, 0xF4),
    "J": Opcode("J", 3, 0x3C),
    "JEQ": Opcode("JEQ", 3, 0x30),
    "JGT": Opcode("JGT", 3, 0x34),
    "JLT": Opcode("JLT", 3, 0x38),
    "JSUB": Opcode("JSUB", 3, 0x48),
    "LDA": Opcode("LDA", 3, 0x00),
    "LDB": Opcode("LDB", 3, 0x68),
    "LDCH": Opcode("LDCH", 3, 0x50),
    "LDF": Opcode("LDF", 3, 0x70),
    "LDL": Opcode("LDL", 3, 0x08),
    "LDS": Opcode("LDS", 3, 0x6C),
    "LDT": Opcode("LDT", 3, 0x74),
    "LDX": Opcode("LDX", 3, 0x04),
    "LPS": Opcode("LPS", 3, 0xD0),
    "MUL": Opcode("MUL", 3, 0x20),
    "MULF": Opcode("MULF", 3, 0x60),
    "MULR": Opcode("MULR", 2, 0x98),
    "NORM": Opcode("NORM", 1, 0xC8),
    "OR": Opcode("OR", 3, 0x44),
    "RD": Opcode("RD", 3, 0xD8),
    "RMO": Opcode("RMO", 2, 0xAC),
    "RSUB": Opcode("RSUB", 3, 0x4C),
    "SHIFTL": Opcode("SHIFTL", 2, 0xA4),
    "SHIFTR": Opcode("SHIFTR", 2, 0xA8),
    "SIO": Opcode("SIO", 1, 0xF0),
    "SSK": Opcode("SSK", 3, 0xEC),
    "STA": Opcode("STA", 3, 0x0C),
    "STB": Opcode("STB", 3, 0x78),
    "STCH": Opcode("STCH", 3, 0x54),
    "STF": Opcode("STF", 3, 0x80),
    "STI": Opcode("STI", 3, 0xD4),
    "STL": Opcode("STL", 3, 0x14),
    "STS": Opcode("STS", 3, 0x7C),
    "STSW": Opcode("STSW", 3, 0xE8),
    "STT": Opcode("STT", 3, 0x84),
    "STX": Opcode("STX", 3, 0x10),
    "SUB": Opcode("SUB", 3, 0x1C),
    "SUBF": Opcode("SUBF", 3, 0x5C),
    "SUBR": Opcode("SUBR", 2, 0x94),
    "SVC": Opcode("SVC", 2, 0xB0),
    "TD": Opcode("TD", 3, 0xE0),
    "TIO": Opcode("TIO", 1, 0xF8),
    "TIX": Opcode("TIX", 3, 0x2C),
    "TIXR": Opcode("TIXR", 2, 0xB8),
    "WD": Opcode("WD", 3, 0xDC),
}

DIRECTIVES = {
    "START", "END", "BYTE", "WORD", "RESB", "RESW", "EQU", "USE", "BASE"
}

