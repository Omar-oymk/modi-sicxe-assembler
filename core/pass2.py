import re
from pathlib import Path
from parser import is_a_directive, line_list, valid_instruction
import tables

intermediate_table = []
symbol_table = []
block_table = []
pool_table = []
lc = 0

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


def parse_symbTable():
    symbol_list = []

    file_path = Path(__file__).parents[1] / "output" / "symbTable.txt"

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = re.split(r'\s+', line)

        # skip invalid lines
        if len(parts) < 2:
            continue

        symbol = parts[0]
        address = parts[1]

        # ignore headers if they exist
        if symbol.lower() in ["symbol", "label"]:
            continue

        try:
            address = int(address, 16)
        except ValueError:
            continue

        symbol_list.append({
            "symbol": symbol,
            "address": address
        })

    return symbol_list

def parse_blockTable():
    block_list = []

    file_path = Path(__file__).parents[1] / "output" / "blockTable.txt"

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = re.split(r'\s+', line)

        # skip header
        if parts[0].lower() == "block":
            continue

        # skip footer line
        if parts[0].lower() == "total":
            continue

        if len(parts) < 4:
            continue

        name = parts[0]
        number = parts[1]
        address = parts[2]
        size = parts[3]

        try:
            number = int(number)
            address = int(address, 16)
            size = int(size, 16)
        except ValueError:
            continue

        block_list.append({
            "name": name,
            "number": number,
            "address": address,
            "size": size
        })

    return block_list


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


def pass_2():
    # print(line_list[4].opcode) # type: ignore
    # intermediate_table = parse_intermediate()

    print(parse_intermediate())

if __name__ == '__main__':
    pass_2()