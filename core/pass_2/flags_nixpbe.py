


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

    operand = operand.strip()

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
            result["target"] = symtab[value]

    elif operand.startswith("@"):
        result["n"] = 1
        result["i"] = 0
        symbol = operand[1:]
        if symbol not in symtab:
            print(f"Symbol not found: {symbol}")
            return None
        result["target"] = symtab[symbol]

    elif operand.startswith("&"):
        if operand not in pooltab:
            print(f"Literal not found: {operand}")
            return None
        result["target"] = pooltab[operand]

    else:
        if operand not in symtab:
            print(f"Symbol not found: {operand}")
            return None
        result["target"] = symtab[operand]

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
