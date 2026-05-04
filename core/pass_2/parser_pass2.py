import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import tables

def is_hex(value):
    try:
        int(value, 16)
        return True
    except ValueError:
        return False

def parse_intermediate():
    intermediate_list = []

    file_path = Path(__file__).parents[2] / "output" / "intermediate.txt"

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

            opcode = tables.OPCODES.get(instr.lstrip("+").upper()) if instr else None

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
                    instruction=instr,  # type: ignore
                    operand=operand,
                    opcode=None,
                    object_code=None,
                    block=None
                )
            )

    return intermediate_list


def parse_symtab():
    symtab = {}

    file_path = Path(__file__).parents[2] / "output" / "symbTable.txt"

    with open(file_path, "r") as f:

        print("SYMTAB path:", file_path, "| exists:", file_path.exists())
        print("Raw contents:", file_path.read_text())

        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = re.split(r'\s+', line)
            if len(parts) < 2:
                continue

            symbol = parts[0]
            try:
                address = int(parts[1], 16)
            except ValueError:
                continue 
            
            symtab[symbol] = address

    return symtab

def parse_blockTable():
    block_table = {}

    file_path = Path(__file__).parents[2] / "output" / "blockTable.txt"

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

    file_path = Path(__file__).parents[2] / "output" / "poolTable.txt"

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