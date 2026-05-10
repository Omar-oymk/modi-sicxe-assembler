# Modified SIC/XE Assembler

A complete, two-pass assembler for a modified version of the SIC/XE (Simplified Instructional Computer Extra Equipment) architecture. This project implements a robust systems programming pipeline that translates SIC/XE assembly language into relocatable object code, featuring advanced handling of program blocks and literal pools.

## 🎯 Project Overview

This assembler processes source code written in the SIC/XE assembly language and generates corresponding machine object code, specifically formatted into Header, Text, Modification, and End (HTME) records. The assembler is designed to accurately handle complex addressing modes, program blocks (using the `USE` directive), and literal pools (using the `&` operand prefix).

The assembler strictly adheres to a two-pass architecture:
- **Pass 1:** Assigns addresses to all statements, manages program blocks, handles literal pools, and generates an intermediate file along with comprehensive symbol, block, and pool tables.
- **Pass 2:** Translates instructions and generates the final object code and HTME records, utilizing the tables and intermediate file generated during Pass 1.

## 🏗️ Architecture

The system pipeline is cleanly separated into modular components:
1. **Lexical Analysis & Parsing (`core/parser.py`):** Acts as "Pass 1a". This module is heavily overloaded: it reads input, removes comments, evaluates block assignments (`USE`), calculates literal pools (`&`), and tracks the relative Location Counters (LC) across blocks.
2. **Table Aggregation (`core/pass1.py`):** Acts as "Pass 1b". It acts as a passive orchestrator that consumes the output of the parser to construct the absolute Symbol Table, Block Table, and Pool Table.
3. **Pass 2 Pipeline (`core/pass_2/pass2.py`):**
   - Resolves PC-relative, Base-relative, Immediate, Indirect, and Extended addressing modes.
   - Generates format 1, 2, 3, and 4 object codes.
   - Outputs the final HTME records.
4. **GUI Visualization (Bonus):** A retro-cyberpunk themed graphical memory visualization tool built with Tkinter (`gui/memory_viewer.py`) to simulate object code loading and memory modifications.

### Block System
The assembler supports multiple program blocks via the `USE` directive:
- `DEFAULT` / `DEFAULTB`: Standard code blocks.
- `CDATA`: Initialized data block.
- `CBLKS`: Uninitialized memory allocation block.
Pass 1 assigns relative addresses within each block, and later adjusts them into a continuous memory layout, recalculating absolute addresses for all symbols.

### POOL Block Behavior (Literal Pools)
Literal operands prefixed with `&` (e.g., `&C'EOF'`, `&X'0F'`) are automatically extracted and placed into a dedicated `POOL` block.
- **Deduplication:** Repeated identical literals are merged.
- **Auto-Allocation:** The `POOL` block is seamlessly inserted into the final memory layout.
- **Addressing:** Pass 2 properly resolves these pool variables using PC/Base-relative addressing.

## 📂 File Structure

```text
modi-sicxe-assembler/
│
├── assembler.py          # Main entry point CLI
├── README.md             # Project documentation
│
├── core/                 # Core assembler logic
│   ├── pass1.py          # Pass 1 orchestrator
│   ├── parser.py         # Pass 1 parser & LC management
│   ├── blocks.py         # Block management and address adjustment
│   ├── pool.py           # Literal pool extraction and deduplication
│   ├── tables.py         # Opcode dictionaries and data models
│   └── pass_2/           # Pass 2 logic
│       ├── pass2.py            # Pass 2 orchestrator
│       ├── assemble_line.py    # Object code generation router
│       ├── flags_nixpbe.py     # Addressing mode calculations
│       ├── parser_pass2.py     # Parses Pass 1 intermediate outputs
│       └── htme/               # HTME record generators
│
├── gui/                  # Graphical memory viewer
│   └── memory_viewer.py
│
├── input/                # Sample assembly source files
│   ├── in.txt
│   └── fullin.txt
│
└── output/               # Generated outputs (created on run)
    ├── intermediate.txt
    ├── symbTable.txt
    ├── PoolTable.txt
    ├── blockTable.txt
    ├── out_pass2.txt
    ├── HTME.txt
    └── error.txt         # (Only generated if assembly fails)
```

## 🚀 Execution Instructions

The project runs via a single command from the root directory.

### Standard Execution
```bash
python assembler.py input/in.txt
```
All output files will be automatically generated in the `output/` folder.

### Execution with GUI Memory Visualization
To assemble the code and launch the retro-cyberpunk memory viewer to inspect the loaded HTME records:
```bash
python assembler.py input/in.txt --gui
```

## 📄 Input/Output Formats

### Input Format
Source code should be standard SIC/XE assembly language text files.
Supported directives: `START`, `END`, `BYTE`, `WORD`, `RESB`, `RESW`, `BASE`, `USE`.
Comments are prefixed with `;`.

### Output Files
- **`intermediate.txt`:** Displays LC, Symbol, Instruction, and Operand for each line.
- **`symbTable.txt`:** Contains absolute memory addresses for all labels.
- **`blockTable.txt`:** Lists all blocks, their final absolute starting addresses, and sizes.
- **`PoolTable.txt`:** Lists extracted literal pools, their values, lengths, and assigned addresses.
- **`out_pass2.txt`:** A comprehensive listing showing the source line alongside its generated object code.
- **`HTME.txt`:** The final relocatable object code (Header, Text, Modification, End records).

## ⚠️ Error Handling

The assembler performs strict validation. If an error is detected, the process terminates immediately, and an `error.txt` file is generated in the `output/` directory containing details such as the Program Counter (PC), the line number, and a description of the failure.

**Handled Errors Include:**
1. **Unidentified Block Names:** Using a `USE` directive with an unregistered block.
2. **Unidentified Symbol:** Referencing a label that doesn't exist in the Symbol Table (raises a precise error mapping to the program counter).
3. **Invalid Instructions:** Using an unrecognized mnemonic.
4. **POOLVAR Error:** Attempting to address a literal pool variable that is physically placed too far to be reached via PC or Base-relative addressing.

## 🛠️ Implementation Details
- **Language:** Python 3.x
- **No external dependencies** (Standard library only; `tkinter` used for GUI).
- **Bitwise Operations:** Heavy use of bitwise shifting and masking to assemble the precise `n, i, x, b, p, e` flags required by SIC/XE format 3 and 4 instructions.

## 👥 Contributors
- [Omar Ossama]
- [Abdullah Ahmed]
