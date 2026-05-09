import tables
from pathlib import Path
import re
import copy

intermediate_output_lines = []
location_counters = []
line_list = []
current_lc : int = 0x0000

def parse_lines(file_path = Path(__file__).parents[1] / "input" / "in.txt"):
    with open(file_path, "r") as f:
        lines = f.readlines()
        
    return lines



def valid_instruction(instruction: str):
    clean = instruction.upper().lstrip('+')
    return clean in tables.OPCODES or clean in tables.DIRECTIVES 

def is_format_4(instruction: str):
    return instruction.startswith('+')

def is_a_directive(instruction: str):
    return instruction.upper() in tables.DIRECTIVES


def is_valid_block(operand: str):
    return operand.upper() in tables.BLOCKS


def preprocess_and_print_lines():
    global current_lc 
    
    for i, line in enumerate(parsed_lines):
        line = line.strip()

        if line == "":
            continue
    
        # remove comments
        line = re.split(r'\s*;\s*', line)[0]   # split by ; and take the first part
        
        if line == "":
            continue
        # split lines based on spaces
        line = re.split(r'\s+', line)   # this is not the best as it gives errors for the edge case of BYTE C'HELLO, WORLD' but we will handle that later
        if line == "":
            continue
        # print(line)       # USED FOR DEBUGGING


        # construct the objects and append them to the intermediate list
        if len(line) == 3:
            
            if not valid_instruction(line[1]):
                # break
                # raise an error
                # and generate an error.txt file with the error message
                with open(Path(__file__).parents[1]/ 'output' / "error.txt", "w") as f:
                    f.write(f"ERROR OCCURED IN LINE: {i+1}: {line}\nPROGRAM TERMINATED AT PASS 1.")
                raise ValueError(f"Invalid instruction: {line[1]}")

            if is_a_directive(line[1]) and line[1].upper() == 'START':
                current_lc = tables.HANDLE_DIRECTIVES(line[1].upper(), location_counter = current_lc, operand=line[2])
                location_counters.append(format(current_lc, '04X'))


            opcode = copy.deepcopy(tables.OPCODES.get(line[1].lstrip(" +").upper()))    # to copy also the opcode dataobject

            if opcode and is_format_4(line[1]):
                opcode.format = 4

            line_list.append(
                            tables.Line(      
                                            label=line[0],
                                            instruction=line[1],
                                            opcode=opcode if opcode else None,  # none if it is actually a directive
                                            operand=line[2],
                                            object_code=None,
                                            location_counter=f'{current_lc:04X}',
                                            block=None
                                        )
                            )
            
            if is_a_directive(line[1]) and line[1].upper() != 'START':
                if line[1] == 'USE':
                    if not is_valid_block(line[2].upper()):
                        with open(Path(__file__).parents[1] / 'output' / 'error.txt', 'w') as f:
                            f.write('Error : Unidentified Block Name\n')
                            f.write(f'PC    : {current_lc:06X}\n')
                            f.write(f'Line  : line {i+1}\n')
                            f.write(f"Detail: unknown block name '{line[2]}'; valid blocks are CBLKS, CDATA, DEFAULT, DEFAULTB\n")   
                        raise ValueError('Invalid block pass1 terminated')

                current_lc = tables.HANDLE_DIRECTIVES(line[1], location_counter= current_lc, operand = line[2])
            else:
                current_lc += opcode.format if opcode else 0x0000

        elif len(line) == 2:

            if not valid_instruction(line[0]):
                if not valid_instruction(line[1]):
                    # break
                    # raise an error
                    # and generate an error.txt file with the error message
                    with open(Path(__file__).parents[1]/ 'output' / "error.txt", "w") as f:
                        f.write(f"ERROR OCCURED IN LINE: {i+1}: {line}\nPROGRAM TERMINATED AT PASS 1.")
                    raise ValueError(f"Invalid instruction: {line[0]}")

            if is_a_directive(line[0]) and line[0].upper() == 'START':
                current_lc = tables.HANDLE_DIRECTIVES(line[0].upper(), location_counter=current_lc, operand=line[1])

            opcode = copy.deepcopy(tables.OPCODES.get(line[0].lstrip(" +").upper()))

            if opcode and is_format_4(line[0]):
                opcode.format = 4

            line_list.append(
                                tables.Line(           
                                                label=None,
                                                instruction=line[0],
                                                opcode=opcode if opcode else None,
                                                operand=line[1],
                                                object_code=None,
                                                location_counter=f'{current_lc:04X}',
                                                block=None
                                            )
                            )
            

            if is_a_directive(line[0]) and line[0].upper() != 'START':
                if line[0] == 'USE':
                    if not is_valid_block(line[1].upper()):
                        with open(Path(__file__).parents[1] / 'output' / 'error.txt', 'w') as f:
                            f.write('Error : Unidentified Block Name\n')
                            f.write(f'PC    : {current_lc:06X}\n')
                            f.write(f'Line  : line {i+1}\n')
                            f.write(f"Detail: unknown block name '{line[1]}'; valid blocks are CBLKS, CDATA, DEFAULT, DEFAULTB\n")   
                        raise ValueError('Invalid block pass1 terminated')
                current_lc = tables.HANDLE_DIRECTIVES(line[0], location_counter= current_lc, operand = line[1])
            else:
                current_lc += opcode.format if opcode else 0

        elif len(line) == 1:

            if not valid_instruction(line[0]):
                # break
                # raise an error
                # and generate an error.txt file with the error message
                with open(Path(__file__).parents[1]/ 'output' / "error.txt", "w") as f:
                    f.write(f"ERROR OCCURED IN LINE: {i+1}: {line}\nPROGRAM TERMINATED AT PASS 1.")
                raise ValueError(f"Invalid instruction: {line[0]}")

            opcode = copy.deepcopy(tables.OPCODES.get(line[0].lstrip(" +").upper()))    # to copy also the opcode dataobject


            if opcode and is_format_4(line[0]):
                opcode.format = 4

            line_list.append(
                               tables.Line(   
                                            label=None,
                                            instruction=line[0],
                                            opcode=opcode if opcode else None,
                                            operand=None,
                                            object_code=None,
                                            location_counter=f'{current_lc:04X}',
                                            block=None
                                        )
                            )
            

            if is_a_directive(line[0]):
                current_lc = tables.HANDLE_DIRECTIVES(line[0], location_counter= current_lc, operand = None)
            else:
                current_lc += opcode.format if opcode else 0
            
        
        location_counters.append(f'{current_lc:04X}')
        # print(location_counters)


    for i, line in enumerate(line_list):
        intermediate_output_lines.append(f'{location_counters[i]} {line.label} {line.instruction} {line.operand} {line.object_code}\n')

    return intermediate_output_lines

def save_intermediate_output(path_to_output: Path = Path(__file__).parents[1] / 'output' / 'intermediate.txt'):
    # opens intermediate file in write mode
    with open(path_to_output, 'w') as f:
        f.write(f"{'Location counter':<18}{'Symbol':<9}{'Instructions':<14}{'Reference':<10}\n")
        f.write(f"{'-'*18}{'-'*9}{'-'*14}{'-'*10}\n")

        
        for item in intermediate_output_lines:
            line = item.split()

            symbol = line[1] if line[1] != 'None' else ""
            instr = line[2] if line[2] != 'None' else ""
            loc = line[0] if line[0] != 'None' and instr != 'USE' else ""
            ref = line[3] if line[3] != 'None' else ""

            f.write(f"{loc:<18}{symbol:<9}{instr:<14}{ref:<10}\n")

        

parsed_lines = parse_lines()
preprocess_and_print_lines()

print(intermediate_output_lines)
save_intermediate_output()
