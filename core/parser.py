import tables
from pathlib import Path
import re

intermediate_list = []

def parse_lines(file_path = Path(__file__).parents[1] / "input" / "in.txt"):
    with open(file_path, "r") as f:
        lines = f.readlines()
    return lines

parsed_lines = parse_lines()

for line in parsed_lines:
    line = line.strip()
    if line == "":
        continue

print('--' * 20)
# search for the comments and remove them

def preprocess_and_print_lines():
    for line in parsed_lines:
        line = line.strip()
        if line == "":
            continue
        
        # remove comments
        print(line)

    for i, line in enumerate(parsed_lines):
        line = line.strip()

        if line == "":
            continue
    
        # remove comments
        line = re.split(r'\s*;\s*', line)[0]    # split by ; and take the first part

        if line == "":
            continue
        # split lines based on spaces
        line = re.split(r'\s+', line)   # this is not the best as it gives errors for the edge case of BYTE C'HELLO, WORLD' but we will handle that later
        if line == "":
            continue
        print(line)


        # construct the objects and append them to the intermediate list
        if len(line) == 3:

            
            if not valid_instruction(line[1]):
                # break
                # raise an error
                # and generate an error.txt file with the error message
                with open(Path(__file__).parents[1]/ 'output' / "error.txt", "w") as f:
                    f.write(f"ERROR OCCURED IN LINE: {i+1}: {line}\nPROGRAM TERMINATED AT PASS 1.")
                raise ValueError(f"Invalid instruction: {line[1]}")

            opcode = tables.OPCODES.get(line[1].strip("+").upper())

            if opcode and is_format_4(line[1]):
                opcode.format = 4

            intermediate_list.append(tables.Line(label=line[0],
                                                    Instruction=line[1],
                                                    opcode=opcode if opcode else None,  # none if it is actually a directive
                                                    operand=line[2],
                                                    object_code=None,
                                                    location_counter=None,
                                                    block=None))
        elif len(line) == 2:

            if not valid_instruction(line[0]):
                # break
                # raise an error
                # and generate an error.txt file with the error message
                with open(Path(__file__).parents[1]/ 'output' / "error.txt", "w") as f:
                    f.write(f"ERROR OCCURED IN LINE: {i+1}: {line}\nPROGRAM TERMINATED AT PASS 1.")
                raise ValueError(f"Invalid instruction: {line[0]}")

            opcode = tables.OPCODES.get(line[0].strip().upper())
            intermediate_list.append(tables.Line(label=None,
                                                    Instruction=line[0],
                                                    opcode=opcode if opcode else None,
                                                    operand=line[1],
                                                    object_code=None,
                                                    location_counter=None,
                                                    block=None))
        elif len(line) == 1:

            if not valid_instruction(line[0]):
                # break
                # raise an error
                # and generate an error.txt file with the error message
                with open(Path(__file__).parents[1]/ 'output' / "error.txt", "w") as f:
                    f.write(f"ERROR OCCURED IN LINE: {i+1}: {line}\nPROGRAM TERMINATED AT PASS 1.")
                raise ValueError(f"Invalid instruction: {line[0]}")

            opcode = tables.OPCODES.get(line[0].strip().upper())
            intermediate_list.append(tables.Line( label=None,
                                                    Instruction=line[0],
                                                    opcode=opcode if opcode else None,
                                                    operand=None,
                                                    object_code=None,
                                                    location_counter=None,
                                                    block=None))
            
    print(f"LC\tLABEL\tOPCODE\tOPERAND\t  OBJECT_CODE")
    print("--" * 30)
    for line in intermediate_list:
        print(line)

def valid_instruction(instruction: str):
    return instruction.upper() in tables.OPCODES or instruction.upper() in tables.DIRECTIVES or is_format_4(instruction)

def is_format_4(instruction: str):
    return instruction.startswith('+')

preprocess_and_print_lines()