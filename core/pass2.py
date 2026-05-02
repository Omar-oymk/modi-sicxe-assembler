import re
from pathlib import Path
from parser import line_list

intermediate_list = []
symbol_table = []
block_table = []
pool_table = []
lc = 0

def parse_intermediate():
    file_path = Path(__file__).parents[1] / "output" / "intermediate.txt"
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if line == "":
            continue
        
        # split lines based on spaces
        line = re.split(r'\s+', line)
        if line == "":
            continue

def parse_symbTable():
    file_path = Path(__file__).parents[1] / "output" / "symbTable.txt"
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if line == "":
            continue
    
        # split lines based on spaces
        line = re.split(r'\s+', line)
        if line == "":
            continue

def parse_blockTable():
    file_path = Path(__file__).parents[1] / "output" / "blockTable.txt"
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if line == "":
            continue
    
        # split lines based on spaces
        line = re.split(r'\s+', line)
        if line == "":
            continue


def parse_poolTable():
        file_path = Path(__file__).parents[1] / "output" / "poolTable.txt"
        with open(file_path, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()

            if line == "":
                continue
        
            # split lines based on spaces
            line = re.split(r'\s+', line)
            if line == "":
                continue


def pass_2():
    print(line_list[4].opcode) # type: ignore

if __name__ == '__main__':
    pass_2()