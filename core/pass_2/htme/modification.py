

def is_format4_instruction(line):
    return line.instruction and line.instruction.startswith('+')

def get_instruction_address(line, current_block, block_table):
    if line.instruction is None:
        return None

    if is_format4_instruction(line):
        return line.location_counter + block_table[current_block]["address"] + 1


def modification_record_line(line, current_block, block_table):
    if is_format4_instruction(line) and line.location_counter is not None:
        address = get_instruction_address(line, current_block, block_table)
        return f"M.{address:06X}.05"
    return None

def modification_record_list(intermediate_table,current_block, block_table):
    current_block = "DEFAULT"
    m_records = []
    for line in intermediate_table:
        if line.instruction and line.instruction.upper() == 'USE':
            current_block = line.operand if line.operand else "DEFAULT"
            continue

        m_record = modification_record_line(line, current_block, block_table)
        if m_record:
            m_records.append(m_record)

    return m_records


def modification_record(intermediate_table, block_table):
    return "\n".join(modification_record_list(intermediate_table, "DEFAULT", block_table))
