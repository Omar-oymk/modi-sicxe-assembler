# Modified SIC/XE Assembler - Project Report

## 1. Introduction
This report details the design and implementation of a two-pass assembler for the Modified SIC/XE (Simplified Instructional Computer Extra Equipment) architecture. The objective of this project was to build a robust systems software component capable of translating assembly language into relocatable machine code, strictly adhering to SIC/XE format specifications. The assembler provides advanced memory management features, including program block separation and automatic literal pool generation.

## 2. Project Objectives
The primary objectives of this implementation were:
- **Two-Pass Architecture:** Implement a clean separation of concerns where Pass 1 calculates memory addresses and Pass 2 generates object code.
- **Instruction Support:** Support SIC/XE Formats 1, 2, 3, and 4, along with comprehensive addressing modes (Immediate, Indirect, Indexed, Extended, PC-relative, Base-relative).
- **Directives Handling:** Support standard assembler directives (`START`, `END`, `BYTE`, `WORD`, `RESB`, `RESW`, `BASE`, `USE`).
- **Block Management:** Allow the division of code into multiple blocks (`DEFAULT`, `DEFAULTB`, `CDATA`, `CBLKS`) that are intelligently reordered and resolved into a continuous absolute memory map.
- **Literal Pooling:** Automatically extract operands prefixed with `&` into a centralized `POOL` block, ensuring no duplication and correct memory allocation.
- **Error Handling:** Implement fail-fast validation that outputs detailed error logs (`error.txt`) upon encountering invalid syntax, undefined symbols, or addressing failures.

## 3. Architecture & Data Flow
The assembler is modularized into distinct Python packages. The high-level data flow is as follows:

1. **Source Input:** The raw `.txt` assembly file is read by the `parser.py`.
2. **Pass 1 (Address Resolution):** The parser cleans the input (removing comments and whitespace) and passes tokens to Pass 1. Pass 1 iterates through the lines, updating a simulated Location Counter (LC).
3. **Table Generation:** During Pass 1, the `blocks.py` and `pool.py` modules construct the Block Table and Pool Table. The LC values are adjusted based on the block sizes, and the absolute Symbol Table is generated.
4. **Intermediate Output:** The results of Pass 1 are written to `intermediate.txt`, acting as the canonical source for Pass 2.
5. **Pass 2 (Code Generation):** `pass2.py` reads the intermediate file and tables. For each instruction, it delegates object code calculation to `assemble_line.py`, which uses `flags_nixpbe.py` to resolve the precise bits for SIC/XE flags.
6. **HTME Generation:** The final step involves packing the generated object codes into properly formatted Header, Text, Modification, and End records.

## 4. Pass 1 Implementation
The core responsibility of Pass 1 is memory mapping.
- **Location Counter Tracking:** Maintained globally and updated per line based on instruction format (1, 2, 3, or 4) or directive footprint (e.g., `RESW` adds `operand * 3`).
- **Block Tracking:** When a `USE` directive is encountered, the current LC for the active block is saved, and the LC is swapped to the saved state of the new block.
- **Address Adjustment:** Once all source lines are processed, `adjust_final_blocks` sequentially places the blocks in memory (`DEFAULT` -> `DEFAULTB` -> `POOL` -> `CDATA` -> `CBLKS`). Absolute addresses for all symbols are then computed by adding the relative LC to the block's absolute starting address.

## 5. Pass 2 Implementation
Pass 2 focuses entirely on translation.
- **Addressing Modes Calculation:** The `flags_nixpbe.py` module determines the `n` (indirect) and `i` (immediate) bits based on `@` and `#` prefixes. The `x` (indexed) bit is toggled if `,X` is appended to the operand.
- **Relative Addressing:** The assembler first attempts to use Program Counter (PC) relative addressing (-2048 to 2047 bytes). If the target address is out of bounds, it falls back to Base-relative addressing (0 to 4095 bytes) if a `BASE` register has been set.
- **Format 4 Handling:** If an instruction is prefixed with `+`, it forces Format 4 (Extended addressing). The `e` bit is set to 1, and the full 20-bit absolute address is embedded directly into the object code, resulting in a 4-byte instruction.

## 6. Program Blocks & Pool Management
### Program Blocks
The implementation handles blocks by keeping an independent Location Counter for each block named in a `USE` directive. During the finalization of Pass 1, the sizes of all blocks are calculated. They are then concatenated to form a single absolute address space. The `blockTable.txt` output clearly shows the starting address and length of each block.

### Pool Management (Literal Pools)
Literals (e.g., `&C'EOF'`, `&X'0F'`) are intercepted during Pass 1. 
- The `pool.py` module checks for existing identical literals to avoid redundancy.
- It calculates the necessary byte length for the literal (e.g., `C'EOF'` requires 3 bytes).
- A synthetic `POOL` block is automatically injected into the block hierarchy (typically immediately following the default code blocks).
- During Pass 2, references to `&` variables are resolved exactly like normal symbols, pointing to the addresses allocated within the `POOL` block.

## 7. HTME Record Generation
The final object program is structured strictly according to SIC/XE standards:
- **Header (H):** Contains the program name, starting absolute address, and total program length.
- **Text (T):** Contains the contiguous machine code. The generator intelligently breaks T-records when the maximum length (30 bytes/60 hex characters) is reached, or when encountering memory reservations (`RESW`/`RESB`) or block boundaries.
- **Modification (M):** Generated exclusively for Format 4 instructions. Since Format 4 contains absolute addresses, they must be flagged for relocation by the loader. The M-record specifies the address of the address field to be modified (LC + 1) and its length in half-bytes (05).
- **End (E):** Specifies the address of the first executable instruction.

## 8. Error Handling
The assembler is designed to fail gracefully. Instead of crashing via unhandled Python exceptions, it catches logical errors and generates an `error.txt` file.
Scenarios handled include:
- Invalid or unrecognized mnemonics.
- Unidentified block names in `USE` directives.
- Undefined symbols used as operands.
- POOLVAR failures, where a pool variable is physically placed too far from the instruction to be reached via PC or Base-relative addressing.

## 9. Bonus: Memory Visualization GUI
To enhance the testing and debugging experience, a standalone GUI tool was developed using `tkinter`.
The Memory Viewer Application:
- Reads the generated `HTME.txt` file.
- Simulates the execution of a system loader, placing the bytes into a simulated 1 MB byte-addressable memory space.
- Correctly applies Modification (M) records, utilizing bitwise arithmetic to update absolute addresses.
- Displays the memory map in a professional, dynamic retro-cyberpunk hexadecimal grid.

## 10. Conclusion
The Modified SIC/XE Assembler successfully implements a complete, standards-compliant systems programming pipeline. By meticulously handling multi-block memory mapping, automated literal pools, and complex relative addressing architectures, the project demonstrates a profound understanding of low-level machine design and compiler/assembler theory. The addition of the HTME GUI viewer further solidifies the project as a complete, end-to-end toolchain.
