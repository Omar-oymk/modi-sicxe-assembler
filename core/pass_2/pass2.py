import sys
from pathlib import Path

import parser_pass2 as parse
from assemble_line import assemble_line

def pass_2():

    intermediate_table = []
    symbol_table = {}
    block_table = {}
    pool_table = {}


    current_block = "DEFAULT"
    base_register = None
    lc = 0

    symbol_table = parse.parse_symtab()
    block_table = parse.parse_blockTable()
    pool_table = parse.parse_poolTable()
    intermediate_table = parse.parse_intermediate()

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