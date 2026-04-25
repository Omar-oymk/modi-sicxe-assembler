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

for line in parsed_lines:
    line = line.strip()
    if line == "":
        continue
    
    line = re.split(r'\s+', line)
    print(line)
    # remove comments
    if len(line) == 3:
        opcode = tables.OPCODES.get(line[1].strip().upper())
        intermediate_list.append(tables.Line(label=line[0],
                                                opcode=opcode.opcode if opcode else None,
                                                operand=line[2],
                                                object_code=None,
                                                location_counter=None,
                                                block=None))
    elif len(line) == 2:
        opcode = tables.OPCODES.get(line[0].strip().upper())
        intermediate_list.append(tables.Line(label=None,
                                                opcode=opcode.opcode if opcode else None,
                                                operand=line[1],
                                                object_code=None,
                                                location_counter=None,
                                                block=None))
    elif len(line) == 1:
        opcode = tables.OPCODES.get(line[0].strip().upper())
        intermediate_list.append(tables.Line(label=None,
                                                opcode=opcode.opcode if opcode else None,
                                                operand=None,
                                                object_code=None,
                                                location_counter=None,
                                                block=None))
        
print(f"LC\tLABEL\tOPCODE\tOPERAND\tOBJECT_CODE")
print("--" * 20)
for line in intermediate_list:
    # print(line)
    pass