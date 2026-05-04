from dataclasses import dataclass

@dataclass
class OpcodeInfo:
    mnemonic: str
    default_format: int     # can be 1, 2 or 3 only 4
    opcode: int

@dataclass
class Line:
    label: str | None
    instruction: str
    opcode: OpcodeInfo | None   # optional if it is actually an opcode, None if it is a directive
    operand: str | None
    object_code: str | None
    location_counter: str | None
    block: str | None

    def __str__(self):
        return f"{self.location_counter}\t{self.label if self.label else ''}\t{self.instruction}\t{self.operand}\t\t{self.object_code}" # type: ignore


def is_char_operand(operand):
    return operand.startswith("C'")

def is_hex_operand(operand):
    return operand.startswith("X'")



def HANDLE_DIRECTIVES(directive: str, location_counter, operand, prev_operand = None):
    if directive == "START":
        location_counter += 0 
    elif directive == "END":
        pass
    elif directive == "BYTE":
        if is_char_operand(operand):
            location_counter += len(operand) - 1
        elif is_hex_operand(operand):
            location_counter += (len(operand) - 1) / 2
    elif directive == "WORD":
        location_counter += 3
    elif directive == "RESB":
        location_counter += int(operand)
    elif directive == "RESW":
        location_counter += int(operand) * 3
    elif directive == "EQU":
        pass
    elif directive == "USE":   
        # needs adjustments and more research on how to handle blocks 
        """
        NEED TO CHECK FOR EXAMPLES CASES LIKE 
        0000
        0002
        0004
        0006
        USE DEFAULTB
        0000
        0003
        0007
        000A
        USE DEFAULT
        
        THE QUESTION IS SHOULD IT BE 
        0008 OR 0000 (aka: continue counting from last location counter on default block or start again)
        """
        if prev_operand == operand:
            pass
        else:
            location_counter = 0
    elif directive == "BASE":
        pass
    return location_counter