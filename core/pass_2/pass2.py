import sys
from pathlib import Path
from core.pass_2.htme.end import end_record
from core.pass_2.htme.modification import modification_record
from core.pass_2.htme.header import total_length, initial_counter, final_counter, header_record
from core.pass_2.htme.text import text_record

from core.pass_2 import parser_pass2 as parse
from core.pass_2.assemble_line import assemble_line


def pass_2(output_dir):

    intermediate_table = []
    symbol_table = {}
    block_table = {}
    pool_table = {}


    current_block = "DEFAULT"
    base_register = None
    lc = 0

    symbol_table = parse.parse_symtab(output_dir)
    block_table = parse.parse_blockTable(output_dir)
    pool_table = parse.parse_poolTable(output_dir)
    intermediate_table = parse.parse_intermediate(output_dir)


    try:
        for i, line in enumerate(intermediate_table):
            if line.instruction.upper() == "USE":
                current_block = line.operand if line.operand else "DEFAULT"
                continue

            elif line.instruction.upper() == "BASE":
                base_symbol = line.operand
                base_register = symbol_table.get(base_symbol)
                if base_register is None:
                    pc_str = f"{line.location_counter:06X}" if line.location_counter is not None else "000000"
                    raise ValueError(
                        f"Error : Unidentified Symbol\n"
                        f"PC    : {pc_str}\n"
                        f"Detail: symbol '{base_symbol}' is referenced but not defined."
                    )
                continue

            elif line.instruction.upper() == "END":
                break

            # handle directives (not complete - just set location counter for now)
            intermediate_table[i].object_code=assemble_line(line, symbol_table, pool_table, base_register, current_block, block_table)

    except ValueError as e:

        with open(output_dir / "error.txt", "w") as f:
            f.write(str(e))

        sys.exit(1)


    with open(output_dir / "out_pass2.txt", "w") as f:
        f.write(f"{'Location counter':<18}{'Symbol':<9}{'Instructions':<14}{'Reference':<12}{'Obj. code':<14}\n")
        f.write(f"{'-'*16}  {'-'*7}  {'-'*12}  {'-'*10}  {'-'*14}\n")
        for line in intermediate_table:
            lc_str = f'{line.location_counter:04X}' if line.location_counter is not None else ''
            label_str = line.label if line.label else ''
            instr_str = line.instruction if line.instruction else ''
            operand_str = line.operand if line.operand else ''
            obj_str = line.object_code if line.object_code else 'No object code'
            f.write(
                f"{lc_str:<18}{label_str:<9}{instr_str:<14}{operand_str:<12}{obj_str}\n"
            )

    with open(output_dir / "HTME.txt", "w") as f:
        f.write(header_record(intermediate_table, block_table) + "\n")
        f.write(text_record(intermediate_table, block_table, parse.parse_poolTable_for_text_rec(output_dir)) + "\n")
        if (modification_record(intermediate_table, block_table)):
            f.write(modification_record(intermediate_table, block_table) + "\n")
        f.write(end_record(intermediate_table, block_table))