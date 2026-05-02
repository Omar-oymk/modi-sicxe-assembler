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
        if i < 2:
            continue

        line = line.strip()
        if not line:
            continue

        parts = re.split(r'\s+', line)

        if not parts:
            continue


        # CASE 1: normal instruction line (has LC)
        if is_hex(parts[0]):

            lc = int(parts[0], 16)
            tokens = parts[1:]

            # CASE: LC + LABEL + OPCODE + OPERAND
            if len(tokens) == 3:
                label, instr, operand = tokens

            # CASE: LC + OPCODE + OPERAND
            elif len(tokens) == 2:
                label = None
                instr, operand = tokens

            # CASE: LC + OPCODE only
            elif len(tokens) == 1:
                label = None
                instr = tokens[0]
                operand = None

            else:
                continue

            opcode = tables.OPCODES.get(instr.upper())

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
                tables.Line(
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
    file_path = Path(__file__).parents[1] / "output" / "symbTable.txt"
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if line == "":
            continue
    
        # split lines based on spaces
        line = re.split(r'\s+', line)
        if line == "":
            continue

def parse_blockTable():
    file_path = Path(__file__).parents[1] / "output" / "blockTable.txt"
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if line == "":
            continue
    
        # split lines based on spaces
        line = re.split(r'\s+', line)
        if line == "":
            continue


def parse_poolTable():
        file_path = Path(__file__).parents[1] / "output" / "poolTable.txt"
        with open(file_path, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()

            if line == "":
                continue
        
            # split lines based on spaces
            line = re.split(r'\s+', line)
            if line == "":
                continue


def pass_2():
    # print(line_list[4].opcode) # type: ignore
    # intermediate_table = parse_intermediate()

    print(parse_intermediate())

if __name__ == '__main__':
    pass_2()