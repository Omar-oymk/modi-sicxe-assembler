from parser import line_list, intermediate_output_lines, location_counters
import blocks
import pool

block_list = blocks.handle_blocks(line_list)
pool_list, current_block, next_block = pool.handle_pool(line_list, block_list)
adjusted_block_list, total_program_length = blocks.adjust_final_blocks(block_list, pool_list, current_block)
print(block_list)

print(pool_list, " ", current_block, " ", next_block)

print(adjusted_block_list, " ", total_program_length)