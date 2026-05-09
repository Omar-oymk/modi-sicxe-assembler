


def program_name(intermediate_table):
    if intermediate_table[0].instruction.upper() == "START":
        return intermediate_table[0].label if intermediate_table[0].label else "UNKNOWN"
    return "UNKNOWN"

def initial_counter(intermediate_table):
    if intermediate_table[0].instruction.upper() == "START":
        return intermediate_table[0].location_counter if intermediate_table[0].location_counter else 0
    return 0

def final_counter(block_table):
    total_size = 0
    for key in block_table:
        total_size += block_table[key]["size"]
    return total_size

def total_length(intermediate_table, block_table):
    return final_counter(block_table) - initial_counter(intermediate_table)


def header_record(intermediate_table, block_table):
    program_name_str = program_name(intermediate_table)
    initial_counter_value = initial_counter(intermediate_table)
    program_length = total_length(intermediate_table, block_table)
    return f"H.{program_name_str:X<6}.{initial_counter_value:06X}.{program_length:06X}"