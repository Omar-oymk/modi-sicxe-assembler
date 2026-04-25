import tables
from pathlib import Path
import re

intermediate_list = []

def parse_lines(file_path = Path("input") / "in.txt"):
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

    for line in parsed_lines:
        line = line.strip()

        if line == "":
            continue
    
        # remove comments
        line = re.split(r'\s*;\s*', line)[0]    # split by ; and take the first part
        # split lines based on spaces
        line = re.split(r'\s+', line)
        print(line)
    
        # construct the objects and append them to the intermediate list
        if len(line) == 3:
            opcode = tables.OPCODES.get(line[1].strip().upper())
            intermediate_list.append(tables.Line(label=line[0],
                                                    Instruction=line[1],
                                                    opcode=opcode if opcode else None,  # none if it is actually a directive
                                                    operand=line[2],
                                                    object_code=None,
                                                    location_counter=None,
                                                    block=None))
        elif len(line) == 2:
            opcode = tables.OPCODES.get(line[0].strip().upper())
            intermediate_list.append(tables.Line(label=None,
                                                    Instruction=line[0],
                                                    opcode=opcode if opcode else None,
                                                    operand=line[1],
                                                    object_code=None,
                                                    location_counter=None,
                                                    block=None))
        elif len(line) == 1:
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


preprocess_and_print_lines()