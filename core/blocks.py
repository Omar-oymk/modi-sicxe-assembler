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


def adjust_final_blocks(block_list, pool_table, index_of_pool):
    print(index_of_pool)
    total_program_length = 0
    adjusted_block_list = []
    size = 0
    block_size = 0
    address_pool = 0

    pool_block_name = block_list[index_of_pool - 1]['BLOCK NAME']

    # we want to add all the duplicated blocks first the size of them
    for i, block in enumerate(block_list):
        block_size += int(block['SIZE'], 16)
        for item in block_list[i+1:]:
            if block['BLOCK NAME'] == item['BLOCK NAME']:
                block_size = int(item['SIZE'], 16) - int(block['ADDRESS'], 16)
                removed_index = block_list.index(item)
                block_list.remove(item)
                if removed_index < index_of_pool:
                    index_of_pool -= 1
        block_list[i]['SIZE'] = f'{block_size:04X}'
        block_size = 0
    
    print(f'Index of pool after deduplication: {index_of_pool}')

    for item in pool_table:
        size += item['LENGTH']

    pool_inserted = False
    for i, item in enumerate(block_list):

        if i == 0:
            adjusted_block_list.append(item)
        else:
            adjusted_block_list.append({
                "BLOCK NAME": item['BLOCK NAME'],
                "BLOCK NUMBER": len(adjusted_block_list),
                "ADDRESS": f"{int(adjusted_block_list[-1]['ADDRESS'], 16) + int(adjusted_block_list[-1]['SIZE'], 16):04X}",
                "SIZE": item['SIZE']
            })

        if i == index_of_pool - 1 and not pool_inserted:
            address_pool = int(adjusted_block_list[-1]['ADDRESS'], 16) + int(adjusted_block_list[-1]['SIZE'], 16)
            adjusted_block_list.append({
                "BLOCK NAME": "POOL",
                "BLOCK NUMBER": len(adjusted_block_list),
                "ADDRESS": f"{address_pool:04X}",
                "SIZE": f"{size:04X}"
            })
            pool_inserted = True

    if not pool_inserted:
        address_pool = int(adjusted_block_list[-1]['ADDRESS'], 16) + int(adjusted_block_list[-1]['SIZE'], 16)
        adjusted_block_list.append({
            "BLOCK NAME": "POOL",
            "BLOCK NUMBER": len(adjusted_block_list),
            "ADDRESS": f"{address_pool:04X}",
            "SIZE": f"{size:04X}"
        })

    for item in adjusted_block_list:
        total_program_length += int(item['SIZE'], 16)

    for i, item in enumerate(pool_table):
        if i == 0:
            pool_table[i]['ADDRESS'] = f'{address_pool:04X}'
        else:
            pool_table[i]['ADDRESS'] = f'{int(pool_table[i-1]["ADDRESS"], 16) + pool_table[i-1]["LENGTH"]:04X}'

    return adjusted_block_list, f'{total_program_length:04X}', pool_table