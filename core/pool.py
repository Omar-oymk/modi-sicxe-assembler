import parser
import tables 


def handle_pool(lines, block_table):
    prev_block_sizes = [int(block_table[0]['SIZE'], 16)]
    pool_table = []

    pool_name = ""
    address = ""
    length = 0
    object_code = ""

    current_block = ""
    next_block = ""
    
    block_found = False
    search_for_next = False

    starting_lc = ""

    current_block_line = lines[0]
    found_symbol = False

    for line in lines:
        if line.operand:
            if search_for_next and (line.instruction == 'USE' or line.instruction == 'END'):
                next_block = line.operand
                next_block_line = line
                search_for_next = False
            
            if line.instruction == 'USE' and not block_found:
                current_block = line.operand
                current_block_line = line

            if line.instruction == 'USE' and not found_symbol:
                for item in block_table:
                    if item['BLOCK NAME'] == line.operand:
                        prev_block_sizes.append(int(item['SIZE'], 16))

            if line.operand.startswith('&'):
                pool_name = line.operand
                address = line.location_counter
                block_found = True
                search_for_next = True
                found_symbol = True

                if tables.is_char_operand(line.operand[1:]):
                    length = len(line.operand[3:-1])
                    object_code = ''.join(format(ord(c), '02X') for c in line.operand[3:-1])
                elif tables.is_hex_operand(line.operand[1:]):
                    length = int(len(line.operand[3:-1])//2)
                    object_code = line.operand[3:-1]

                pool_table.append({
                    'POOL NAME': pool_name,
                    'ADDRESS': address,
                    'LENGTH': length,
                    'OBJECT CODE': object_code
                })

    for i, item in enumerate(pool_table):
        if i == 0:  # for first item address will be = to the sum of the previous blocks' sizes
            starting_lc = f"{sum(prev_block_sizes):04X}"
            item['ADDRESS'] = starting_lc
        else:
            item['ADDRESS'] = f"{int(pool_table[i-1]['ADDRESS'], 16) + pool_table[i-1]['LENGTH']:04X}"


            
    return pool_table, current_block, next_block