def handle_blocks(lines):
    block_list = []
    i = 0 
    
    for line in lines:
        if line.instruction == 'USE' or i == 0:

            block_list.append({
                "BLOCK NAME" : "DEFAULT" if i == 0 else line.operand,
                "BLOCK NUMBER": i,
                "ADDRESS": '0000' if i == 0 else line.location_counter,
                "SIZE": ""
            })

            if i != 0:
                block_list[i-1]['SIZE'] = block_list[i]['ADDRESS']

            i+=1
        
        if line.instruction == 'END':
            block_list[i-1]['SIZE'] = line.location_counter
    
    return block_list

def adjust_final_blocks(block_list, pool_table, current_block):
    total_program_length = 0

    adjusted_block_list = []
    size = 0
    for i, item in enumerate(block_list):
        adjusted_block_list.append(item)
        if block_list[i]['BLOCK NAME'] == current_block:

            for item in pool_table:
                size += item['LENGTH']

            adjusted_block_list.append({
                "BLOCK NAME": "POOL",
                "BLOCK NUMBER": i + 1,
                "ADDRESS": pool_table[0]['ADDRESS'],
                'SIZE': f'{size:04X}'
            })
            for item in block_list[i+1:]:
                last_block = adjusted_block_list[-1]

                new_address = int(last_block['ADDRESS'], 16) + int(last_block['SIZE'], 16)

                adjusted_block_list.append({
                    "BLOCK NAME": item['BLOCK NAME'],
                    "BLOCK NUMBER": last_block['BLOCK NUMBER'] + 1,
                    "ADDRESS": f"{new_address:04X}",
                    "SIZE": item['SIZE']
                })
            
            break

    for item in adjusted_block_list:
        total_program_length += int(item['SIZE'], 16)
    return adjusted_block_list, f'{total_program_length:04X}'
