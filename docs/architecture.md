# Architecture Overview

This document provides a comprehensive overview of the architecture for the Modified SIC/XE Assembler project. It describes the main components, their interactions, and the overall design principles that guide the development of the system.

------------------------------------------------
## High Level System Pipeline

The assembler is built on a classical two-pass architecture, cleanly separating the concerns of memory mapping and object code generation. 

### 1. Data Flow
1. **Input Stage:** The system reads an assembly text file (`.txt`) containing SIC/XE instructions, directives, and comments.
2. **Pass 1 (The Mapping Phase):** The logic is unconventionally split across two modules:
   - **Pass 1a (The Overloaded Parser):** `core/parser.py` cleans the input, extracts symbols, evaluates block assignments (`USE`), calculates literal pools (`&`), tracks the Location Counter (LC), and builds `Line` objects.
   - **Pass 1b (Table Aggregation):** `core/pass1.py` consumes the results of the parser to finalize the sizes and positions of blocks, and ultimately constructs the Symbol and Pool tables.
3. **Table Construction:** During Pass 1, several critical tables are constructed in memory and dumped to the `output/` directory:
   - `intermediate.txt`: The normalized, line-by-line representation of the source.
   - `symbTable.txt`: Absolute memory addresses of all labels.
   - `blockTable.txt`: Starting addresses and sizes of all program blocks.
   - `PoolTable.txt`: Deduped literal pool variables with absolute addresses.
4. **Pass 2 (The Generation Phase):** The assembler reads the intermediate file and tables, translates instructions into hexadecimal object code, and calculates relative address displacements.
5. **Output Stage:** The final Machine Object Code is assembled into HTME format (`HTME.txt`) and a human-readable list file (`out_pass2.txt`) is generated.

------------------------------------------------
## Core System Components

### 1. Parser, Lexer & LC Engine (`core/parser.py`)
- **Responsibility:** This module serves as "Pass 1a". It acts as the entry point for the source code, handling lexical analysis by stripping out comments, but it is heavily **overloaded**. It acts as a semantic analyzer and partial assembler by actively tracking the simulated Location Counter (LC), validating directives, and switching Location Counters when `USE` is encountered.
- **Output:** A list of structured `Line` objects representing every actionable statement, alongside raw relative LCs.

### 2. Table Orchestrator (`core/pass1.py` & `core/tables.py`)
- **Responsibility:** This module serves as "Pass 1b". Despite its name, it does *not* do the heavy lifting of Pass 1 (LC tracking and parsing). Instead, it acts as a passive aggregator that consumes the `Line` objects produced by `parser.py` to finalize the Block Table, Pool Table, and Symbol Table.

### 3. Block Manager (`core/blocks.py`)
- **Responsibility:** Manages the separation of concerns within the assembly file using the `USE` directive.
- **Mechanism:** Tracks independent Location Counters for `DEFAULT`, `DEFAULTB`, `CDATA`, and `CBLKS`. At the end of Pass 1, it concatenates these blocks into a linear address space, generating the `blockTable.txt`.

### 4. Literal Pool Synthesizer (`core/pool.py`)
- **Responsibility:** Detects `&` prefixed literal operands (e.g., `&C'EOF'`) and manages them.
- **Mechanism:** Avoids duplicate literal declarations. It synthesizes a virtual `POOL` block that is automatically appended to the memory layout, tracking lengths and assigned addresses for Pass 2 resolution.

### 5. Instruction Assembler & Address Resolver (`core/pass_2/assemble_line.py` & `flags_nixpbe.py`)
- **Responsibility:** Translates `Line` objects into SIC/XE object code.
- **Mechanism:** 
  - Resolves `n` (indirect) and `i` (immediate) bits via `@` and `#`.
  - Attempts PC-Relative addressing first. If the displacement is out of bounds (-2048 to 2047), it automatically falls back to Base-Relative addressing (0 to 4095).
  - Encodes the final `n, i, x, b, p, e` bits into the target hexadecimal string.

### 6. HTME Generator (`core/pass_2/htme/`)
- **Responsibility:** Formats the final relocatable object program.
- **Mechanism:**
  - **Header (`header.py`):** Calculates program bounds.
  - **Text (`text.py`):** Packs object code seamlessly, intelligently breaking records at block boundaries or upon hitting the 30-byte record limit.
  - **Modification (`modification.py`):** Flags Format 4 absolute addresses so the ultimate loader knows they require relocation at runtime.
  - **End (`end.py`):** Marks the first executable instruction.

------------------------------------------------
## Design Principles

- **Modularity:** Heavy use of isolated Python modules allows for easy debugging and future enhancements (e.g., adding a macro processor).
- **Fail-Fast Error Handling:** The system refuses to assemble invalid code. It catches errors such as unregistered blocks, undefined symbols, and unreachable pool variables, immediately terminating and generating an `error.txt` diagnostic file.
- **Stateless Object Generation:** Pass 2 relies entirely on the finalized tables produced by Pass 1, ensuring determinism and preventing forward-reference bugs.
