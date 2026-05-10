# Pass 1 - Architecture & Flow

Pass 1 of the Modified SIC/XE Assembler focuses entirely on parsing the assembly code, tracking memory allocation, evaluating program blocks, identifying literal pools, and constructing the core tables (Symbol, Block, and Pool Tables) that Pass 2 will need for final code generation.

## 1. Core Modules Involved
- **`core/parser.py` (The Overloaded Parser)**: Acts as "Pass 1a". It does far more than read and tokenize; it actively calculates the Location Counter (LC), manages relative memory allocation, and catches directive/instruction syntax errors.
- **`core/pass1.py` (The Table Orchestrator)**: Acts as "Pass 1b". Despite the file name, it does *not* do the core LC mapping. It merely consumes the objectified output of `parser.py` to finalize absolute block addresses and construct the main tables.
- **`core/blocks.py`**: Manages the multiple program blocks.
- **`core/pool.py`**: Detects literals (using `&`) and tracks literal pools.
- **`core/tables.py`**: Contains the hardcoded OPCODES, DIRECTIVES, and the logic to calculate size footprints for memory reservation directives (`RESW`, `RESB`, `BYTE`, `WORD`).

## 2. Architectural Quirk: The Unconventional Split
The architecture of Pass 1 in this project is notably unconventional and somewhat confusing. In a standard two-pass assembler, "Pass 1" is a unified process that handles lexical parsing, semantic analysis (Location Counter tracking), and symbol table generation simultaneously. 

However, in this assembler, Pass 1 is heavily fragmented:
*   **The Parser does too much:** `core/parser.py` is overloaded. It does not just act as a lexer. It operates as the core semantic engine, calculating the LC, processing `USE` directives to maintain multiple parallel block counters, and trapping layout errors. 
*   **Pass1 does too little:** `core/pass1.py` acts as a passive aggregator. It relies entirely on the parsed `Line` structures and intermediate LC arrays dumped by `parser.py`. Its only job is to calculate the final contiguous block sizes and resolve the Symbol Table and Pool Table absolute addresses. 

This creates a pipeline where `parser.py` is essentially **Pass 1a** and `pass1.py` is **Pass 1b**.

## 3. Detailed Execution Flow

### Step 1: Lexical Parsing (`parser.py`)
1. Reads lines from the input text file.
2. Strips out comments (anything after `;`).
3. Splits lines by whitespace to identify tokens (Labels, Instructions, Operands).
4. Matches the mnemonic against `tables.OPCODES`. If the instruction starts with `+`, it flags it as Format 4.
5. Emits an intermediate list of `Line` objects representing every valid statement.

### Step 2: Location Counter Calculation
As instructions are parsed, a simulated `Location Counter (LC)` is maintained:
- **Format 1 instructions:** LC += 1
- **Format 2 instructions:** LC += 2
- **Format 3 instructions:** LC += 3
- **Format 4 instructions:** LC += 4
- **`RESB n`**: LC += n
- **`RESW n`**: LC += 3 * n
- **`BYTE/WORD`**: LC += calculated size of the constant.

### Step 3: Block Management (`blocks.py`)
Whenever the parser encounters a `USE <blockname>` directive:
- The current LC is saved into the state of the active block.
- The LC is swapped to the previously saved state of the *new* block (or `0000` if it's the first time the block is used).
- This creates parallel location counters, meaning symbols in different blocks are assigned relative addresses within their respective blocks.

### Step 4: Literal Pooling (`pool.py`)
During parsing, if an operand starts with `&` (e.g., `&C'EOF'`, `&X'0F'`):
1. The literal is added to a pending Pool Table list.
2. Identical literals are deduplicated to save memory.
3. Pass 1 automatically synthesizes a `POOL` block that will act as the storage block for these literals.
4. The necessary byte size of the literal is recorded.

### Step 5: Absolute Address Resolution
Once the entire source file is parsed:
1. `blocks.py` calculates the final absolute sizes of every block.
2. Blocks are ordered contiguously in memory (`DEFAULT` -> `DEFAULTB` -> `POOL` -> `CDATA` -> `CBLKS`).
3. **Symbol Table generation (`handle_symboltable`)**: Pass 1 iterates over every symbol. It looks up the block the symbol was defined in, and calculates its true absolute memory address by adding the symbol's relative LC to the absolute starting address of its block.
4. **Pool Table generation**: The `POOL` block's absolute starting address is assigned, and individual literals are given contiguous absolute addresses within that block.

### Step 6: Output Generation
Pass 1 outputs the following artifacts to the `output/` directory:
- `intermediate.txt`
- `symbTable.txt`
- `blockTable.txt`
- `PoolTable.txt`
