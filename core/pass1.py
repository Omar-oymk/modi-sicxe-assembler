from parser import line_list, intermediate_output_lines, location_counters
import blocks
import pool
from pathlib import Path


def handle_symboltable(lines, block_table):
    current_block = "DEFAULT"
    current_block_address = ""

    symb_table = []
    
    for item in block_table:
        if item['BLOCK NAME'] == 'DEFAULT':
            current_block_address = item['ADDRESS']
            break
    
    # main loop
    for line in lines:
        if line.instruction == 'USE':
            for item in block_table:
                if item['BLOCK NAME'] == line.operand:
                    current_block = line.operand
                    current_block_address = item['ADDRESS']
        
        if line.label and line.instruction != 'START':
            symb_table.append({
                'SYMBOL': line.label,
                'ADDRESS': f'{int(current_block_address, 16) + int(line.location_counter, 16):04X}'
            })
            
    
    return symb_table
    



block_list = blocks.handle_blocks(line_list)
pool_list, current_block, next_block = pool.handle_pool(line_list, block_list)
adjusted_block_list, total_program_length = blocks.adjust_final_blocks(block_list, pool_list, current_block)
symb_table = handle_symboltable(line_list, adjusted_block_list)
# print(block_list)

# print(pool_list, " ", current_block, " ", next_block)

# print(adjusted_block_list, " ", total_program_length)

# print(symb_table)

def save_pool_table(pool_list, file_path = Path(__file__).parents[1] / 'output' / 'PoolTable.txt'):
    with open(file_path, 'w') as f:
        f.write(f"{'POOL NAME':<12}{'ADDRESS':<10}{'LENGTH':<8}{'OBJECT CODE':<12}\n")
        
        for item in pool_list:
            values = list(item.values())
            f.write(f'{values[0]:<12}{values[1]:<10}{values[2]:<8}{values[3]:<12}\n')
        
def save_block_table(block_list, total_program_length, file_path = Path(__file__).parents[1] / 'output' / 'blockTable.txt'):
    with open(file_path, 'w') as f:
        f.write(f'{'BLOCK NAME':<12}{'BLOCK NUMBER':<14}{'ADDRESS':<10}{'SIZE':<8}\n')

        for item in block_list:
            values = list(item.values())
            f.write(f'{values[0]:<12}{values[1]:<14}{values[2]:<10}{values[3]:<8}\n')
        
        f.write(f'\nTotal program length: {total_program_length}')

def save_symbol_table(symbol_list, file_path = Path(__file__).parents[1] / 'output' / 'symbTable.txt'):
    with open(file_path, 'w') as f:
        f.write(f'{'SYMBOL NAME':<13}{'ADDRESS':<8}\n')
        for item in symbol_list:
            values = list(item.values())
            f.write(f'{values[0]:<13}{values[1]:<8}\n')


save_pool_table(pool_list)
save_block_table(adjusted_block_list, total_program_length)
save_symbol_table(symb_table)