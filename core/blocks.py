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
    total_program_length = 0
    adjusted_block_list = []
    size = 0
    block_size = 0


    # we want to add all the duplicated blocks first the size of them
    for i, block in enumerate(block_list):
        block_size += int(block['SIZE'], 16)
        for item in block_list[i+1:]:
            if block['BLOCK NAME'] == item['BLOCK NAME']:
                block_size = int(item['SIZE'], 16) - int(block['ADDRESS'], 16)
                # DELETE THE DUPLICATE BLOCK
                block_list.remove(item)
                index_of_pool -= 1
        block_list[i]['SIZE'] = f'{block_size:04X}'
        block_size = 0
            
    # we want to loop first through the block list and add all the blocks to the adjusted block list
    #  until we find the block at which the pool is in,
    #  then we want to add the pool block to the adjusted block list
    #  and then we want to add the remaining blocks to the adjusted block list
    #  with their new addresses calculated from the pool block size and address

    for i, item in enumerate(block_list):
        
        if i==0:
            adjusted_block_list.append(item)
        else:
            adjusted_block_list.append({
                "BLOCK NAME": item['BLOCK NAME'],
                "BLOCK NUMBER": i,
                "ADDRESS": f"{int(adjusted_block_list[-1]['ADDRESS'], 16) + int(adjusted_block_list[-1]['SIZE'], 16):04X}",
                "SIZE": item['SIZE']
            })

        # if block_list[i]['BLOCK NAME'] == current_block:    # when u find the block at which the pool is in start the loop
        if i == index_of_pool - 1:    # when u find the block at which the pool is in start the loop

            for item in pool_table:     # calculates size from pool table
                size += item['LENGTH']

            adjusted_block_list.append({
                "BLOCK NAME": "POOL",
                "BLOCK NUMBER": index_of_pool,
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
