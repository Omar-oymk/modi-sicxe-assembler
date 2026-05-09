import sys
from pathlib import Path
from core import parser, pass1
from core.pass_2.pass2 import pass_2
from gui.memory_viewer import main


if __name__ == "__main__":
    # --- CLI argument handling ---
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <input_file>\nAdditionally: u can write '--gui' flag to show memory")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    # Output directory is always 'output/' relative to assembler.py
    project_root = Path(__file__).parent
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    # --- Pass 1 ---
    parsed_lines = parser.parse_lines(input_file)
    intermediate_output_lines, location_counters, line_list = parser.preprocess_and_print_lines(parsed_lines, output_dir)
    parser.save_intermediate_output(intermediate_output_lines, output_dir / 'intermediate.txt')

    block_list, pool_list, adjusted_block_list, total_program_length, symb_table = pass1.create_tables(line_list)
    pass1.save_pool_table(pool_list, output_dir / 'PoolTable.txt')
    pass1.save_block_table(adjusted_block_list, total_program_length, output_dir / 'blockTable.txt')
    pass1.save_symbol_table(symb_table, output_dir / 'symbTable.txt')

    # --- Pass 2 ---
    pass_2(output_dir)

    if len(sys.argv) > 2:
        if sys.argv[2].lower() == '--gui':
            main()
        else:
            print("INVALID COMMAND: ")
            print("Usage: python assembler.py <input_file>\nAdditionally: u can write '--gui' flag to show memory")
    else: 
        print("if you want the gui option use the flag '--gui'")