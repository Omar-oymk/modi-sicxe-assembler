import sys
from pathlib import Path
from htme.header import total_length, initial_counter, final_counter, header_record

import parser_pass2 as parse
from assemble_line import assemble_line

sys.path.append(str(Path(__file__).resolve().parents[1]))
from parser import line_list, location_counters, intermediate_output_lines

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
    # print("=== SYMTAB ===")
    # for k, v in symbol_table.items():
    #     print(f"  {k!r}: {v:04X}")

    # print("=== POOLTAB ===")
    # for k, v in pool_table.items():
    #     print(f"  {k!r}: {v:04X}")

    # print("=== BLOCK TABLE ===")
    # for k, v in block_table.items():
    #     print(f"  {k!r}: {v}")

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
        # print(line.location_counter, line.instruction, line.object_code)

    # print(initial_counter(intermediate_table))
    # print(final_counter(intermediate_table))
    # print(total_length(intermediate_table))

    print(header_record(intermediate_table, block_table))

    with open(Path(__file__).parents[2] / 'output' / "out_pass2.txt", "w") as f:
        f.write(f"Location counter  Symbol  Instructions  Reference  Obj. code\n")
        f.write(f"-------------------------------------------------------------\n")
        for line in intermediate_table:
            f.write(f"{line.location_counter:04X}              {line.label if line.label else 'None':<10}  {line.instruction if line.instruction else 'None':<10}  {line.operand if line.operand else 'None':<10}  {line.object_code if line.object_code else 'None':<10}\n")


        # line.object_code = assemble_line(line, symbol_table, pool_table, base_register, current_block, block_table)



def test():
    pass_2()

if __name__ == '__main__':
    test()