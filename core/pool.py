import parser
import tables 


def handle_pool(lines, block_table):
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

    for line in lines:
        if line.operand:
            if search_for_next and (line.instruction == 'USE' or line.instruction == 'END'):
                next_block = line.operand
                next_block_line = line
                search_for_next = False
            
            if line.instruction == 'USE' and not block_found:
                current_block = line.operand
                current_block_line = line

            if line.operand.startswith('&'):
                pool_name = line.operand
                address = line.location_counter
                block_found = True
                search_for_next = True

                if tables.is_char_operand(line.operand[1:]):
                    length = len(line.operand[3:-1])
                    object_code = ''.join(format(ord(c), '02X') for c in line.operand[3:-1])
                elif tables.is_hex_operand(line.operand[1:]):
                    length = int(len(line.operand[3:-1])/2)
                    object_code = line.operand[3:-1]

                pool_table.append({
                    'POOL NAME': pool_name,
                    'ADDRESS': address,
                    'LENGTH': length,
                    'OBJECT CODE': object_code
                })

    for i, item in enumerate(pool_table):
        if i == 0:  # for first item just make it = locc of prev block + locc of next block
            starting_lc = f"{(int(current_block_line.location_counter, 16) + int(next_block_line.location_counter, 16)):04X}"
            item['ADDRESS'] = starting_lc
        else:
            item['ADDRESS'] = f"{int(pool_table[i-1]['ADDRESS'], 16) + pool_table[i-1]['LENGTH']:04X}"


            
    return pool_table, current_block, next_block