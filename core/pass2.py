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


def parse_poolTable():
    pool_list = []

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

        pool_list.append({
            "name": name,
            "address": address,
            "length": length,
            "object_code": object_code
        })

    return pool_list

#----------------------------------------------------------------------------------

def get_absolute_address(lc):
    return blocktab[current_block] + lc

def resolve_operand(operand, symtab, pooltab):

    result = {
        "target": None,
        "n": 1,
        "i": 1,
        "x": 0
    }

    # instructions without operands (e.g. RSUB)
    if operand is None:
        return result

    # indexed
    if ",X" in operand.upper():
        result["x"] = 1
        operand = operand.replace(",X", "")

    # immediate
    if operand.startswith("#"):

        result["n"] = 0
        result["i"] = 1

        value = operand[1:]

        # constant
        if value.isdigit():
            result["target"] = int(value)

        # symbol
        else:
            try:
                result["target"] = symtab[value]
            except KeyError:
                print(f"Symbol not found: {value}")
                return None

    # indirect
    elif operand.startswith("@"):

        result["n"] = 1
        result["i"] = 0

        symbol = operand[1:]
        try:
            result["target"] = symtab[symbol]
        except KeyError:
            print(f"Symbol not found: {symbol}")
            return None

    # literal pool
    elif operand.startswith("&"):

        try:
            result["target"] = pooltab[operand]
        except KeyError:
            print(f"Literal not found: {operand}")
            return None

    # simple
    else:

        try:
            result["target"] = symtab[operand]
        except KeyError:
            print(f"Symbol not found: {operand}")
            return None

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
intermediate_table = []
symbol_table = {}
block_table = {}
pool_table = {}

symtab = parse_symtab()
blocktab = parse_blockTable()

current_block = "DEFAULT"
base_register = None
lc = 0


def pass_2():

    for line in parse_intermediate():
        if line.instruction.upper() == "USE":
            current_block = line.operand if line.operand else "DEFAULT"
            continue

        elif line.instruction.upper() == "BASE":
            base_register = line.operand
            continue

        elif line.instruction.upper() == "END":
            break

        # handle directives (not complete - just set location counter for now)
        elif tables.is_a_directive(line.instruction):
            line.location_counter = get_absolute_address(lc)
            continue

        # handle instructions (not complete - just set location counter for now)
        elif line.opcode:
            line.location_counter = get_absolute_address(lc)
            continue


def test():
    print(generate_format3_object_code(
    opcode=0x00,   # LDA
    n=1,
    i=1,
    x=0,
    b=0,
    p=1,
    e=0,
    disp=0x01E
    ))

if __name__ == '__main__':
    test()