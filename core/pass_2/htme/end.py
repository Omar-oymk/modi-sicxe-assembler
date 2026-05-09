

def initial_counter(intermediate_table):
    if intermediate_table[0].instruction.upper() == "START":
        return intermediate_table[0].location_counter if intermediate_table[0].location_counter else 0
    return 0

def end_record(intermediate_table, block_table):
    starting_address = initial_counter(intermediate_table)
    return f"E.{starting_address:06X}"