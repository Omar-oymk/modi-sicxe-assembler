

def is_instruction(line):
    return line.instruction.upper() not in {"START", "END", "USE", "BASE", "WORD", "RESW", "RESB", "BYTE"}


def switch_current_block(line):
    if line.instruction.upper() == 'USE':
        return line.operand
    return None


def get_lc_instruction(line):
    if is_instruction(line) and line.location_counter is not None:
        return line.location_counter
    return None


def get_starting_address(pass_2_table):
    for line in pass_2_table:
        if get_lc_instruction(line) is not None and line.location_counter is not None:
            return get_lc_instruction(line)
    return None


def text_record_list(pass_2_table, block_table):
    current_block = "DEFAULT"
    t_records = []
    prev_was_data = False 
    t_record = {
        "STARTING ADDRESS": None,
        "LENGTH": 0,
        "INSTRUCTIONS": []
    }

    def flush():
        if t_record["LENGTH"] > 0:
            text = ("T." + f"{t_record['STARTING ADDRESS']:06X}" + "." +
                    f"{t_record['LENGTH']:02X}" + "." +
                    ".".join(t_record['INSTRUCTIONS']))
            t_records.append(text)
            t_record["STARTING ADDRESS"] = None
            t_record["LENGTH"] = 0
            t_record["INSTRUCTIONS"].clear()

    for line in pass_2_table:
        instr = line.instruction.upper() if line.instruction else None
        
        if instr == 'BASE':
            continue

        if instr == 'USE':
            flush()
            prev_was_data = False 
            current_block = line.operand if line.operand else "DEFAULT"
            continue

        if instr in {"RESW", "RESB", "END"}:
            flush()
            prev_was_data = False 
            continue

        if instr in {"START"}:
            prev_was_data = False 
            continue

        base_addr = block_table[current_block]["address"]

        if line.location_counter is None or not line.object_code:
            flush()
            prev_was_data = False
            continue


        if instr in {"BYTE", "WORD"}:
            if not prev_was_data:  # first BYTE/WORD after instructions → flush
                flush()
            
            if t_record["STARTING ADDRESS"] is None:
                t_record["STARTING ADDRESS"] = line.location_counter + base_addr
            
            if instr == "BYTE":
                t_record["LENGTH"] += (len(line.operand) - 3) // 2
            else:
                t_record["LENGTH"] += 3
            
            t_record["INSTRUCTIONS"].append(line.object_code)
            prev_was_data = True
            continue

        
        new_len = len(line.object_code) // 2
        if t_record["LENGTH"] + new_len > 30:
            flush()

        if t_record["STARTING ADDRESS"] is None:
            t_record["STARTING ADDRESS"] = line.location_counter + base_addr
        t_record["LENGTH"] += new_len
        t_record["INSTRUCTIONS"].append(line.object_code)

    flush()
    return t_records


def text_record(text_records, block_table):
    return f"\n".join(text_record_list(text_records, block_table))