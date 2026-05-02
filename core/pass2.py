import re
from pathlib import Path
from parser import is_a_directive, line_list, valid_instruction
import tables

def is_hex(value):
    try:
        int(value, 16)
        return True
    except ValueError:
        return False

def parse_intermediate():
    intermediate_list = []

    file_path = Path(__file__).parents[1] / "output" / "intermediate.txt"

    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):

        # skip header
        if i < 2:
            continue

        line = line.strip()
        if not line:
            continue

        parts = re.split(r'\s+', line)

        if not parts:
            continue

        # normalize string "None" → real None
        parts = [None if x == "None" else x for x in parts]

        # CASE 1: line starts with LC (hex)
        if parts[0] is not None and is_hex(parts[0]):

            lc = int(parts[0], 16)
            tokens = parts[1:]

            # remove "None" noise
            tokens = [None if x == "None" else x for x in tokens]

            # remove None values
            tokens = [x for x in tokens if x is not None]

            label = None
            instr = None
            operand = None

            if len(tokens) == 3:
                label, instr, operand = tokens

            elif len(tokens) == 2:
                instr, operand = tokens

            elif len(tokens) == 1:
                instr = tokens[0]

            else:
                continue

            opcode = tables.OPCODES.get(instr.upper()) if instr else None

            intermediate_list.append(
                tables.Pass2_Line(
                    location_counter=lc,
                    label=label,
                    instruction=instr,
                    operand=operand,
                    opcode=opcode,
                    object_code=None,
                    block=None
                )
            )

        # CASE 2: directive-only line (USE, BASE, END, etc.)
        else:

            instr = parts[0]
            operand = parts[1] if len(parts) > 1 else None

            intermediate_list.append(
                tables.Pass2_Line(
                    location_counter=None,
                    label=None,
                    instruction=instr,
                    operand=operand,
                    opcode=None,
                    object_code=None,
                    block=None
                )
            )

    return intermediate_list


def parse_symtab():
    symtab = {}

    file_path = Path(__file__).parents[1] / "output" / "symbTable.txt"

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = re.split(r'\s+', line)
            if len(parts) < 2:
                continue

            symbol = parts[0]
            address = int(parts[1], 16)

            symtab[symbol] = address

    return symtab

def parse_blockTable():
    block_table = {}

    file_path = Path(__file__).parents[1] / "output" / "blockTable.txt"

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = re.split(r'\s+', line)

            # skip header/footer
            if parts[0].lower() in ["block", "total"]:
                continue

            if len(parts) < 4:
                continue

            name = parts[0]
            number = int(parts[1])
            address = int(parts[2], 16)
            size = int(parts[3], 16)

            block_table[name] = {
                "number": number,
                "address": address,
                "size": size
            }

    return block_table

# hattzbattt
def parse_poolTable():
    pool_table = {}

    file_path = Path(__file__).parents[1] / "output" / "poolTable.txt"

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = re.split(r'\s+', line)

        # skip header
        if parts[0].lower() == "pool":
            continue

        # must have at least 4 columns
        if len(parts) < 4:
            continue

        name = parts[0]
        address = parts[1]
        length = parts[2]
        object_code = parts[3]

        try:
            address = int(address, 16)
            length = int(length)
        except ValueError:
            continue

        pool_table[name] = address

    return pool_table

#----------------------------------------------------------------------------------

def get_absolute_address(lc, current_block, block_table):
    return block_table[current_block]["address"] + lc

def resolve_operand(operand, symtab, pooltab, current_block, block_table):

    result = {
        "target": None,
        "n": 1,
        "i": 1,
        "x": 0
    }

    if operand is None:
        return result

    if ",X" in operand.upper():
        result["x"] = 1
        operand = operand.replace(",X", "").replace(",x", "")

    if operand.startswith("#"):
        result["n"] = 0
        result["i"] = 1
        value = operand[1:]
        if value.isdigit():
            result["target"] = int(value)
        else:
            if value not in symtab:
                print(f"Symbol not found: {value}")
                return None
            result["target"] = symtab[value]  # already absolute

    elif operand.startswith("@"):
        result["n"] = 1
        result["i"] = 0
        symbol = operand[1:]
        if symbol not in symtab:
            print(f"Symbol not found: {symbol}")
            return None
        result["target"] = symtab[symbol]  # already absolute

    elif operand.startswith("&"):
        if operand not in pooltab:
            print(f"Literal not found: {operand}")
            return None
        result["target"] = pooltab[operand]  # already absolute (stored as address in parse_poolTable)

    else:
        if operand not in symtab:
            print(f"Symbol not found: {operand}")
            return None
        result["target"] = symtab[operand]  # already absolute

    return result


def calculate_pc_relative(target, pc):

    disp = target - pc

    if -2048 <= disp <= 2047:

        # convert negative displacement
        if disp < 0:
            disp &= 0xFFF

        return {
            "valid": True,
            "disp": disp,
            "p": 1,
            "b": 0
        }

    return {
        "valid": False
    }


def calculate_base_relative(target, base):

    disp = target - base

    if 0 <= disp <= 4095:
        return {
            "valid": True,
            "disp": disp,
            "p": 0,
            "b": 1
        }

    return {
        "valid": False
    }

#------------------------------------------------------------------------------------

def generate_format3_object_code(
        opcode,
        n,
        i,
        x,
        b,
        p,
        e,
        disp
):

    # remove last 2 bits
    opcode = opcode & 0xFC

    # add n/i bits
    opcode |= (n << 1) | i

    # build xbpe
    xbpe = (x << 3) | (b << 2) | (p << 1) | e

    # build final 24-bit instruction
    object_code = (
        (opcode << 16) |
        (xbpe << 12) |
        disp
    )

    return f"{object_code:06X}"


def generate_format4_object_code(
        opcode,
        n,
        i,
        x,
        b,
        p,
        e,
        address
):

    # clear last 2 bits
    opcode = opcode & 0xFC

    # add n/i bits
    opcode |= (n << 1) | i

    # build xbpe
    xbpe = (x << 3) | (b << 2) | (p << 1) | e

    # build final 32-bit instruction
    object_code = (
        (opcode << 24) |
        (xbpe << 20) |
        address
    )

    return f"{object_code:08X}"

#------------------------------------------------------------------------------------

def assemble_format3(line, symtab, pooltab, base_register, current_block, block_table):

    operand_info = resolve_operand(line.operand, symtab, pooltab, current_block, block_table)

    if operand_info is None or operand_info["target"] is None:  # add this guard
        return None

    target = operand_info["target"]
    n = operand_info["n"]
    i = operand_info["i"]
    x = operand_info["x"]

    pc = line.location_counter + 3  # PC points to next instruction

    # try PC-relative first
    pc_result = calculate_pc_relative(target, pc)

    if pc_result["valid"]:
        return generate_format3_object_code(
            opcode=line.opcode.opcode,
            n=n,
            i=i,
            x=x,
            b=pc_result["b"],
            p=pc_result["p"],
            e=0,
            disp=pc_result["disp"]
        )

    # if PC-relative not possible, try base-relative
    elif base_register is not None:
        base_result = calculate_base_relative(target, base_register)

        if base_result["valid"]:
            return generate_format3_object_code(
                opcode=line.opcode.opcode,
                n=n,
                i=i,
                x=x,
                b=base_result["b"],
                p=base_result["p"],
                e=0,
                disp=base_result["disp"]
            )

    # if neither works, we have an error (needs to be handled and written to and error file)
    raise ValueError(
        f"Address out of range for format 3 at LC={line.location_counter:04X}, target={target:04X}"
    )


def assemble_format4(line, symtab, pooltab, current_block, block_table):

    operand_info = resolve_operand(line.operand, symtab, pooltab, current_block, block_table)

    if operand_info is None:
        return None

    target = operand_info["target"]
    n = operand_info["n"]
    i = operand_info["i"]
    x = operand_info["x"]

    return generate_format4_object_code(
        opcode=line.opcode.opcode,
        n=n,
        i=i,
        x=x,
        b=0,
        p=0,
        e=1,
        address=target
    )

def assemble_format2(line):

    opcode = line.opcode.opcode

    r1 = 0
    r2 = 0

    if line.operand:

        parts = line.operand.split(",")

        r1 = tables.REGISTER_MAP.get(parts[0].strip(), 0)

        if len(parts) == 2:
            r2 = tables.REGISTER_MAP.get(parts[1].strip(), 0)

    object_code = (opcode << 8) | (r1 << 4) | r2

    return f"{object_code:04X}"


def assemble_format1(line):
    opcode = line.opcode.opcode
    return f"{opcode:02X}"


def assemble_byte(operand, line=None):
    operand = operand.strip()

    # Character constant: C'EOF'
    if operand.startswith("C'") and operand.endswith("'"):
        chars = operand[2:-1]

        if chars == "":
            raise ValueError(f"Empty BYTE C constant at line: {line}")

        return ''.join(f"{ord(c):02X}" for c in chars)

    # Hex constant: X'F1'
    elif operand.startswith("X'") and operand.endswith("'"):
        hex_part = operand[2:-1]

        if any(c not in "0123456789ABCDEFabcdef" for c in hex_part):
            raise ValueError(f"Invalid HEX in BYTE at line {line}: {operand}")

        return hex_part.upper()

    else:
        raise ValueError(f"""
        BYTE FORMAT ERROR at line {line}
        Invalid operand: {operand}""")
    
def assemble_word(operand, symtab=None):
    operand = operand.strip()

    # If it's a symbol
    if symtab and operand in symtab:
        value = symtab[operand]
    else:
        # supports decimal, hex, and numeric strings
        try:
            value = int(operand, 0)
        except ValueError:
            raise ValueError(f"Invalid WORD operand: {operand}")

    # 3-byte signed range check (SIC/XE WORD = 24-bit)
    if not (-2**23 <= value <= 2**24 - 1):
        raise ValueError(f"WORD out of range: {value}")

    # convert to 24-bit hex in case of negative values, we want the 2's complement hex representation to cap the negative value in 3 bytes
    return f"{value & 0xFFFFFF:06X}"


def handle_directive(line, symtab):

    instr = line.instruction.upper()

    if instr == "BYTE":
        return assemble_byte(line.operand, line.location_counter)

    elif instr == "WORD":
        return assemble_word(line.operand, symtab)

    elif instr in ["RESB", "RESW", "START", "END", "BASE", "USE"]:
        return None

    return None


def assemble_line(line, symtab, pooltab, base_register, current_block, block_table):
    
    if line.opcode is None:
        return handle_directive(line, symtab)
    
    if line.instruction.startswith("+"):
        return assemble_format4(line, symtab, pooltab, current_block, block_table)
    
    elif line.opcode.format == 1:
        return assemble_format1(line)

    elif line.opcode.format == 2:
        return assemble_format2(line)

    elif line.opcode.format == 3:
        return assemble_format3(line, symtab, pooltab, base_register, current_block, block_table)
    
    raise ValueError(f"Unknown instruction format: {line}")


#------------------------------------------------------------------------------------



def pass_2():

    intermediate_table = []
    symbol_table = {}
    block_table = {}
    pool_table = {}


    current_block = "DEFAULT"
    base_register = None
    lc = 0

    symbol_table = parse_symtab()
    block_table = parse_blockTable()
    pool_table = parse_poolTable()
    intermediate_table = parse_intermediate()

    # DEBUG — remove after fixing
    print("=== SYMTAB ===")
    for k, v in symbol_table.items():
        print(f"  {k!r}: {v:04X}")

    print("=== POOLTAB ===")
    for k, v in pool_table.items():
        print(f"  {k!r}: {v:04X}")

    print("=== BLOCK TABLE ===")
    for k, v in block_table.items():
        print(f"  {k!r}: {v}")

    for i, line in enumerate(intermediate_table):
        if line.instruction.upper() == "USE":
            current_block = line.operand if line.operand else "DEFAULT"
            continue

        elif line.instruction.upper() == "BASE":
            base_symbol = line.operand
            base_register = symbol_table.get(base_symbol)
            if base_register is None:
                print(f"Warning: BASE symbol '{base_symbol}' not found in symtab")
            continue

        elif line.instruction.upper() == "END":
            break

        # handle directives (not complete - just set location counter for now)
        intermediate_table[i].object_code=assemble_line(line, symbol_table, pool_table, base_register, current_block, block_table)

        print(line.location_counter, line.instruction, line.object_code)


def test():
    pass_2()

if __name__ == '__main__':
    test()