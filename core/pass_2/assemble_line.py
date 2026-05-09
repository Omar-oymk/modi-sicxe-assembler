import re
from core.pass_2.flags_nixpbe import calculate_base_relative, calculate_pc_relative, generate_format3_object_code, generate_format4_object_code, resolve_operand
from core import tables

def assemble_format3(line, symtab, pooltab, base_register, current_block, block_table):

    operand_info = resolve_operand(line.operand, symtab, pooltab, current_block, block_table)

    if operand_info is None or operand_info["target"] is None:  # add this guard
        return None

    target = operand_info["target"]
    n = operand_info["n"]
    i = operand_info["i"]
    x = operand_info["x"]

    if n == 0 and i == 1 and line.operand.lstrip("#").strip().isdigit():
        return generate_format3_object_code(
            opcode=line.opcode.opcode,
            n=n, i=i, x=x, b=0, p=0, e=0,
            disp=target
        )

    block_base = block_table[current_block]["address"]
    pc = (line.location_counter + block_base) + 3

    # try PC-relative first
    pc_result = calculate_pc_relative(target, pc)

    if pc_result["valid"]:
        return generate_format3_object_code(
            opcode=line.opcode.opcode,
            n=n,
            i=i,
            x=x,
            b=pc_result["b"],
            p=pc_result["p"],
            e=0,
            disp=pc_result["disp"]
        )

    # if PC-relative not possible, try base-relative
    elif base_register is not None:
        base_result = calculate_base_relative(target, base_register)

        if base_result["valid"]:
            return generate_format3_object_code(
                opcode=line.opcode.opcode,
                n=n,
                i=i,
                x=x,
                b=base_result["b"],
                p=base_result["p"],
                e=0,
                disp=base_result["disp"]
            )

    # if neither works, we have an error (needs to be handled and written to and error file)
    if line.operand and line.operand.strip().startswith("&"):
        raise ValueError(
            f"POOLVAR error at PC={line.location_counter:04X}"
        )

    raise ValueError(
        f"Address out of range for format 3 at LC={line.location_counter:04X}, target={target:04X}"
    )


def assemble_format4(line, symtab, pooltab, current_block, block_table):

    operand_info = resolve_operand(line.operand, symtab, pooltab, current_block, block_table)

    if operand_info is None or operand_info["target"] is None:  # match format3 guard
        return None

    target = operand_info["target"]
    n = operand_info["n"]
    i = operand_info["i"]
    x = operand_info["x"]

    return generate_format4_object_code(
        opcode=line.opcode.opcode,
        n=n,
        i=i,
        x=x,
        b=0,
        p=0,
        e=1,
        address=target
    )

def assemble_format2(line):

    opcode = line.opcode.opcode

    r1 = 0
    r2 = 0

    if line.operand:

        parts = line.operand.split(",")

        r1 = tables.REGISTER_MAP.get(parts[0].strip(), 0)

        if len(parts) == 2:
            r2 = tables.REGISTER_MAP.get(parts[1].strip(), 0)

    object_code = (opcode << 8) | (r1 << 4) | r2

    return f"{object_code:04X}"


def assemble_format1(line):
    opcode = line.opcode.opcode
    return f"{opcode:02X}"


def assemble_byte(operand, line=None):
    operand = operand.strip()

    # Character constant: C'EOF'
    if operand.startswith("C'") and operand.endswith("'"):
        chars = operand[2:-1]

        if chars == "":
            raise ValueError(f"Empty BYTE C constant at line: {line}")

        return ''.join(f"{ord(c):02X}" for c in chars)

    # Hex constant: X'F1'
    elif operand.startswith("X'") and operand.endswith("'"):
        hex_part = operand[2:-1]

        if any(c not in "0123456789ABCDEFabcdef" for c in hex_part):
            raise ValueError(f"Invalid HEX in BYTE at line {line}: {operand}")

        return hex_part.upper()

    else:
        raise ValueError(f"""
        BYTE FORMAT ERROR at line {line}
        Invalid operand: {operand}""")
    
def assemble_word(operand, symtab=None):
    operand = operand.strip()

    # If it's a symbol
    if symtab and operand in symtab:
        value = symtab[operand]
    else:
        # supports decimal, hex, and numeric strings
        try:
            value = int(operand, 0)
        except ValueError:
            raise ValueError(f"Invalid WORD operand: {operand}")

    # 3-byte signed range check (SIC/XE WORD = 24-bit)
    if not (-2**23 <= value <= 2**24 - 1):
        raise ValueError(f"WORD out of range: {value}")

    # convert to 24-bit hex in case of negative values, we want the 2's complement hex representation to cap the negative value in 3 bytes
    return f"{value & 0xFFFFFF:06X}"


def handle_directive(line, symtab):

    instr = line.instruction.upper()

    if instr == "BYTE":
        return assemble_byte(line.operand, line.location_counter)

    elif instr == "WORD":
        return assemble_word(line.operand, symtab)

    elif instr in ["RESB", "RESW", "START", "END", "BASE", "USE"]:
        return None

    return None


def assemble_line(line, symtab, pooltab, base_register, current_block, block_table):
    
    if line.instruction.startswith("+"):
        return assemble_format4(line, symtab, pooltab, current_block, block_table)
    
    if line.instruction.upper() in ["RSUB"]:
        return f"{0x4F0000:06X}"

    if line.opcode is None:
        return handle_directive(line, symtab)
    
    elif line.opcode.format == 1:
        return assemble_format1(line)

    elif line.opcode.format == 2:
        return assemble_format2(line)

    elif line.opcode.format == 3:
        return assemble_format3(line, symtab, pooltab, base_register, current_block, block_table)
    
    raise ValueError(f"Unknown instruction format: {line}")