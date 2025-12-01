# LinguaFlow - Architecture Documentation

## Overview

This document explains how LinguaFlow's interpreter works internally, from input to execution.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
    "calc ..." ?                           No prefix
        │                                       │
        ↓                                       ↓
┌───────────────────┐                  ┌──────────────┐
│  Natural Language │                  │    LEXER     │
│  Conversion       │                  │  Tokenize    │
│  (LLM)            │                  └──────────────┘
└───────────────────┘                          ↓
        ↓                                      │
  Get symbolic expr                            │
        │                                      │
        └──────────────┬───────────────────────┘
                       ↓
               ┌──────────────┐
               │    LEXER     │
               │  Tokenize    │
               └──────────────┘
                       ↓
               ┌──────────────┐
               │    PARSER    │
               │  + LLM       │
               │  Resolution  │
               └──────────────┘
                       ↓
               ┌──────────────┐
               │     AST      │
               │  (Abstract   │
               │   Syntax     │
               │    Tree)     │
               └──────────────┘
                       ↓
               ┌──────────────┐
               │ INTERPRETER  │
               │   Execute    │
               └──────────────┘
                       ↓
               ┌──────────────┐
               │    RESULT    │
               └──────────────┘
```

---

## Pipeline Stages

### Stage 0: Input Preprocessing (main.py)

**Purpose**: Handle special prefixes before normal processing

**Process**:
```python
1. Read user input from REPL
2. Check for "calc" prefix
   → If found: Extract sentence, send to LLM for conversion to symbolic
   → If not found: Pass directly to lexer
3. Handle special commands: help, rules, exit
```

**Example**:
```
Input: "calc what is 10 divided by 2"
↓
Extract: "what is 10 divided by 2"
↓
LLM converts: "10 / 2"
↓
Pass to lexer: "10 / 2"
```

**Files**: `main.py:29-44`

---

### Stage 1: Lexical Analysis (Lexer)

**Purpose**: Convert raw text into stream of tokens

**Location**: `basic.py:142-256`

**Process**:
```python
1. Read characters one by one
2. Recognize patterns:
   - Numbers: Digits (with optional decimal point)
   - Symbols: +, -, *, /, (, ), [, ], :, ,
   - Words: Letters only
3. Classify words:
   - Keywords: of, and, these, numbers
   - Operation words: Everything else → WORD_OP
4. Create tokens with position tracking
5. Return token stream + EOF token
```

**Token Types**:
- `TT_INT`, `TT_FLOAT`: Numbers
- `TT_PLUS`, `TT_MINUS`, `TT_MUL`, `TT_DIV`: Symbolic operators
- `TT_LPAREN`, `TT_RPAREN`: Parentheses
- `TT_LBRACKET`, `TT_RBRACKET`, `TT_COMMA`, `TT_COLON`: List syntax
- `TT_KEYWORD`: Structural keywords
- `TT_WORD_OP`: Potential operation words (needs LLM validation)
- `TT_EOF`: End of input

**Example**:
```
Input: "5 add 3"
↓
Tokens: [INT:5, WORD_OP:add, INT:3, EOF]
```

---

### Stage 2: Syntax Analysis (Parser)

**Purpose**: Recognize grammar patterns and build Abstract Syntax Tree (AST)

**Location**: `basic.py:347-702`

**Key Components**:

#### Pattern Recognition
The parser tries to match one of 6 grammar patterns:

```python
def expr(self):
    # Try Rule 3: Functional form
    if WORD_OP followed by "these":
        return functional_expr()

    # Try Rule 4: Natural phrasing
    if WORD_OP followed by "of":
        return natural_phrasing_expr()

    # Try Rule 2: Infix worded
    if number followed by WORD_OP:
        return infix_worded_expr()

    # Default: Rule 1 (Symbolic) with mixed rule support
    return symbolic_expr()
```

#### LLM Resolution Integration
When parser encounters `WORD_OP` token:

```python
def resolve_word_op(self, word_tok):
    1. Send word to LLM
    2. LLM analyzes: Is it a math operation? (with typo detection)
    3. LLM responds: +, -, *, / or ERROR
    4. Create resolved token
    5. Display resolution to user
    6. Return resolved token
```

**Files**: `basic.py:378-420`

#### Grammar Rules Implementation

**Rule 1: Symbolic**
```python
symbolic_expr → term ((+|-|WORD_OP) term)*
term → factor ((*|/|WORD_OP) factor)*
factor → number | (expr) | unary_op factor | natural_phrasing_expr
```

**Rule 2: Infix Worded**
```python
infix_worded_expr → number WORD_OP number
```

**Rule 3: Functional**
```python
functional_expr → WORD_OP "these" "numbers" ":" "[" number_list "]"
number_list → number ("," number)*
```

**Rule 4: Natural Phrasing**
```python
natural_phrasing_expr → WORD_OP "of" number "and" number
```

**Rule 5: Mixed Rules**
- Achieved through composability of all rules
- Rules 3 (functional) and 4 (natural phrasing) can be factors
- Rule 2 (infix worded) operators work anywhere operators are valid
- Dynamic resolution during parsing
- Any combination of Rules 1-4 can be chained together
- No limit on how many rules can be combined

**Rule 6: Natural Language**
- Handled in Stage 0 (preprocessing)
- Converts to symbolic, then parsed normally

#### AST Node Types

**NumberNode**:
```python
NumberNode(tok)
- Leaf node containing a number
- Example: 5 → NumberNode(Token(INT, 5))
```

**BinOpNode**:
```python
BinOpNode(left_node, op_tok, right_node)
- Binary operation
- Example: 5 + 3 → BinOpNode(NumberNode(5), Token(PLUS), NumberNode(3))
```

**UnaryOpNode**:
```python
UnaryOpNode(op_tok, node)
- Unary operation (negation)
- Example: -5 → UnaryOpNode(Token(MINUS), NumberNode(5))
```

**ListOpNode**:
```python
ListOpNode(op_tok, number_nodes)
- List operation for Rule 3
- Example: sum[5,3,7] → ListOpNode(Token(PLUS), [NumberNode(5), NumberNode(3), NumberNode(7)])
```

**Example AST**:
```
Input: "5 + 3 * 2"

AST:
    BinOp(+)
      /    \
     5    BinOp(*)
           /    \
          3      2
```

---

### Stage 3: Interpretation (Execution)

**Purpose**: Traverse AST and execute operations

**Location**: `basic.py:784-905`

**Process**: Visitor pattern traversal

```python
def visit(self, node, context):
    # Dispatch to appropriate visitor method
    method_name = f'visit_{type(node).__name__}'
    return self.visit_NumberNode(node, context)
           or self.visit_BinOpNode(node, context)
           or self.visit_UnaryOpNode(node, context)
           or self.visit_ListOpNode(node, context)
```

#### Visitor Methods

**visit_NumberNode**:
```python
1. Extract value from token
2. Create Number object
3. Set position and context
4. Return result
```

**visit_BinOpNode**:
```python
1. Visit left operand (recursive)
2. Visit right operand (recursive)
3. Perform operation based on op_tok:
   - PLUS: left + right
   - MINUS: left - right
   - MUL: left * right
   - DIV: left / right (check division by zero)
4. Return result
```

**visit_UnaryOpNode**:
```python
1. Visit operand (recursive)
2. Apply unary operation:
   - MINUS: negate value
   - PLUS: keep value
3. Return result
```

**visit_ListOpNode**:
```python
1. Start with first number
2. For each remaining number:
   - Apply operation to accumulator and current number
   - Update accumulator
3. Return final result
```

#### Runtime Values

**Number Class**:
```python
- value: numeric value
- pos_start, pos_end: position tracking
- context: execution context

Methods:
- added_to(other) → performs addition
- subbed_by(other) → performs subtraction
- multed_by(other) → performs multiplication
- dived_by(other) → performs division (with zero check)
```

**Example Execution**:
```
AST: BinOp(+, NumberNode(5), BinOp(*, NumberNode(3), NumberNode(2)))

Execution trace:
1. Visit BinOp(+)
   1.1. Visit left: NumberNode(5) → Number(5)
   1.2. Visit right: BinOp(*)
        1.2.1. Visit left: NumberNode(3) → Number(3)
        1.2.2. Visit right: NumberNode(2) → Number(2)
        1.2.3. Multiply: 3 * 2 → Number(6)
   1.3. Add: 5 + 6 → Number(11)
2. Return: Number(11)
```

---

## LLM Integration

### Component: GeminiController

**Location**: `gemini_controller.py`

**Purpose**: Interface between interpreter and Gemini LLM

#### Method 1: resolve_operation_word()

**Purpose**: Resolve single operation word to symbol

```python
def resolve_operation_word(word):
    1. Send word to LLM with system instruction
    2. LLM analyzes:
       - Is it a known operation? (add, sum, multiply...)
       - Is it a typo? (sam → sum)
       - Is it gibberish? (asdfas)
    3. LLM responds: +, -, *, / or ERROR
    4. Validate response
    5. Return (symbol, error)
```

**System Instruction**:
- Defines LLM's role as semantic resolver
- Lists operation synonyms
- Includes typo detection rules
- Rejects gibberish

**Example**:
```
Input: "sum"
LLM: "+"

Input: "sam" (typo)
LLM: "+" (corrected)

Input: "asdfas" (gibberish)
LLM: "ERROR"
```

#### Method 2: convert_natural_to_symbolic()

**Purpose**: Convert natural language sentence to symbolic expression

```python
def convert_natural_to_symbolic(sentence):
    1. Build prompt with conversion rules
    2. Send sentence to LLM
    3. LLM extracts mathematical expression
    4. Clean response (remove quotes)
    5. Validate result
    6. Return (expression, error)
```

**Example**:
```
Input: "what is answer of 10 divided by 2"
LLM: "10 / 2"

Input: "calculate 5 times 3 minus 2"
LLM: "5 * 3 - 2"
```

---

## Error Handling

### Error Types

**IllegalCharError** (`basic.py:38-41`):
- Unknown character in input
- Example: `5 @ 3` → "Illegal Character: '@'"

**InvalidSyntaxError** (`basic.py:43-46`):
- Grammar pattern not recognized
- Missing operands or operators
- Example: `5 +` → "Expected int or float"

**RTError** (`basic.py:48-70`):
- Runtime errors during execution
- Division by zero
- Includes traceback

### Position Tracking

**Position Class** (`basic.py:77-99`):
```python
- idx: character index
- ln: line number
- col: column number
- fn: filename
- ftxt: full text

Used for:
- Error messages with exact location
- Visual error indicators (arrows)
```

**Example Error Display**:
```
Invalid Syntax: Expected int or float
File <stdin>, line 1

5 +
    ^
```

---

## Execution Flows

### Flow 1: Simple Symbolic Expression

```
Input: "5 + 3"

[Stage 0] No preprocessing needed
    ↓
[Stage 1: Lexer]
    "5 + 3" → [INT:5, PLUS, INT:3, EOF]
    ↓
[Stage 2: Parser]
    Match symbolic_expr pattern
    Build AST: BinOp(+, NumberNode(5), NumberNode(3))
    ↓
[Stage 3: Interpreter]
    Visit BinOp:
      - Visit left: Number(5)
      - Visit right: Number(3)
      - Add: 5 + 3 = 8
    ↓
Result: 8
```

### Flow 2: Worded Operation with LLM

```
Input: "5 add 3"

[Stage 0] No preprocessing needed
    ↓
[Stage 1: Lexer]
    "5 add 3" → [INT:5, WORD_OP:add, INT:3, EOF]
    ↓
[Stage 2: Parser]
    Match infix_worded_expr pattern
    Encounter WORD_OP:add
    → Call resolve_word_op("add")
    → LLM responds: "+"
    → Display: [LLM Resolution] 'add' → '+'
    Build AST: BinOp(+, NumberNode(5), NumberNode(3))
    ↓
[Stage 3: Interpreter]
    Visit BinOp:
      - Visit left: Number(5)
      - Visit right: Number(3)
      - Add: 5 + 3 = 8
    ↓
Result: 8
```

### Flow 3: Typo Detection

```
Input: "sam of 5 and 3"

[Stage 0] No preprocessing needed
    ↓
[Stage 1: Lexer]
    "sam of 5 and 3" → [WORD_OP:sam, KEYWORD:of, INT:5, KEYWORD:and, INT:3, EOF]
    ↓
[Stage 2: Parser]
    Match natural_phrasing_expr pattern
    Encounter WORD_OP:sam
    → Call resolve_word_op("sam")
    → LLM detects typo: "sam" is close to "sum"
    → LLM responds: "+"
    → Display: [LLM Resolution] 'sam' → '+'
    Build AST: BinOp(+, NumberNode(5), NumberNode(3))
    ↓
[Stage 3: Interpreter]
    Visit BinOp:
      - Visit left: Number(5)
      - Visit right: Number(3)
      - Add: 5 + 3 = 8
    ↓
Result: 8
```

### Flow 4: Mixed Rules

```
Input: "5 + 4 subtract 2"

[Stage 0] No preprocessing needed
    ↓
[Stage 1: Lexer]
    "5 + 4 subtract 2" → [INT:5, PLUS, INT:4, WORD_OP:subtract, INT:2, EOF]
    ↓
[Stage 2: Parser]
    Match symbolic_expr pattern
    Parse: 5
    Parse: + operator
    Parse: 4
    Build partial: BinOp(+, NumberNode(5), NumberNode(4))
    Encounter WORD_OP:subtract
    → Call resolve_word_op("subtract")
    → LLM responds: "-"
    → Display: [LLM Resolution] 'subtract' → '-'
    Parse: 2
    Build complete: BinOp(-, BinOp(+, NumberNode(5), NumberNode(4)), NumberNode(2))
    ↓
[Stage 3: Interpreter]
    Visit outer BinOp(-):
      - Visit left BinOp(+):
          - Visit left: Number(5)
          - Visit right: Number(4)
          - Add: 5 + 4 = 9
      - Visit right: Number(2)
      - Subtract: 9 - 2 = 7
    ↓
Result: 7
```

### Flow 5: Complex Mixed Rules

```
Input: "5 multiply sum of 2 and 3"

[Stage 0] No preprocessing needed
    ↓
[Stage 1: Lexer]
    "5 multiply sum of 2 and 3" → [INT:5, WORD_OP:multiply, WORD_OP:sum, KEYWORD:of, INT:2, KEYWORD:and, INT:3, EOF]
    ↓
[Stage 2: Parser]
    Match symbolic_expr pattern
    Parse term:
      Parse factor: 5 → NumberNode(5)
    Encounter WORD_OP:multiply
    → Call resolve_word_op("multiply")
    → LLM responds: "*"
    → Display: [LLM Resolution] 'multiply' → '*'
    Parse next term:
      Parse factor:
        Encounter WORD_OP:sum followed by KEYWORD:of
        → Delegate to natural_phrasing_expr()
        → Call resolve_word_op("sum")
        → LLM responds: "+"
        → Display: [LLM Resolution] 'sum' → '+'
        → Parse: sum of 2 and 3
        → Build: BinOpNode(+, NumberNode(2), NumberNode(3))
      Return from natural_phrasing_expr
    Build complete: BinOp(*, NumberNode(5), BinOp(+, NumberNode(2), NumberNode(3)))
    ↓
[Stage 3: Interpreter]
    Visit outer BinOp(*):
      - Visit left: Number(5)
      - Visit right BinOp(+):
          - Visit left: Number(2)
          - Visit right: Number(3)
          - Add: 2 + 3 = 5
      - Multiply: 5 * 5 = 25
    ↓
Result: 25
```

### Flow 6: Natural Language Conversion

```
Input: "calc what is 10 divided by 2"

[Stage 0: Preprocessing]
    Detect "calc" prefix
    Extract: "what is 10 divided by 2"
    → Call convert_natural_to_symbolic()
    → LLM converts: "10 / 2"
    → Display: [Natural Language Conversion] ... → '10 / 2'
    Replace input: "10 / 2"
    ↓
[Stage 1: Lexer]
    "10 / 2" → [INT:10, DIV, INT:2, EOF]
    ↓
[Stage 2: Parser]
    Match symbolic_expr pattern
    Build AST: BinOp(/, NumberNode(10), NumberNode(2))
    ↓
[Stage 3: Interpreter]
    Visit BinOp(/):
      - Visit left: Number(10)
      - Visit right: Number(2)
      - Divide: 10 / 2 = 5.0
    ↓
Result: 5.0
```

---

## Key Design Principles

### 1. Grammar-First Architecture

**What It Means**:
- Formal grammar defines ALL valid structures
- Parser enforces grammar rules strictly
- LLM assists but never generates structure

**Why It Matters**:
- Predictable behavior
- Verifiable correctness
- Clear separation of concerns
- Educational value (follows compiler theory)

### 2. Separation of Concerns

**Lexer**:
- Only handles character-to-token conversion
- No semantic understanding
- Pure pattern recognition

**Parser**:
- Only handles syntax structure
- Uses LLM for semantic resolution
- Builds AST according to grammar

**Interpreter**:
- Only handles execution
- No parsing logic
- Visitor pattern for clean traversal

**LLM**:
- Only handles semantic understanding
- Doesn't generate code (except Rule 6)
- Doesn't control structure

### 3. Explainability

**Verbose Output**:
- Shows all pipeline stages
- Displays LLM interactions
- Helps users understand execution

**Error Messages**:
- Position tracking
- Visual indicators
- Clear descriptions

---

## Performance Characteristics

### Time Complexity

| Stage | Complexity | Notes |
|-------|------------|-------|
| Lexer | O(n) | n = input length |
| Parser | O(n) | Linear scan with backtracking |
| LLM Resolution | O(1) | Per WORD_OP, but network latency |
| Interpreter | O(nodes) | AST traversal |

### LLM API Calls

- **Rule 1 (Symbolic)**: 0 calls
- **Rule 2 (Infix)**: 1 call per expression
- **Rule 3 (Functional)**: 1 call per expression
- **Rule 4 (Natural)**: 1 call per expression
- **Rule 5 (Mixed)**: 1 call per WORD_OP
- **Rule 6 (Natural Lang)**: 1 call per expression

### Memory Usage

- **Tokens**: O(n) where n = input length
- **AST**: O(nodes) where nodes = expression complexity
- **Call Stack**: O(depth) where depth = expression nesting

---

## File Structure

```
LinguaFlow/
├── main.py                    # REPL entry point, Stage 0 preprocessing
├── basic.py                   # Core interpreter (Stages 1-3)
│   ├── Lexer                 # Lines 142-256
│   ├── Parser                # Lines 347-702
│   └── Interpreter           # Lines 784-905
├── gemini_controller.py       # LLM interface
├── help_rules.py              # Help system
├── grammar.txt                # Formal grammar specification
├── strings_with_arrows.py     # Error visualization
├── verbose_output.py          # Execution tracing
├── README.md                  # Quick start guide
├── SUMMARY.md                 # Complete feature documentation
└── ARCHITECTURE.md            # This file
```

---

## Summary

LinguaFlow implements a classic three-stage compiler pipeline:

1. **Lexer**: Text → Tokens
2. **Parser**: Tokens → AST (with LLM semantic assistance)
3. **Interpreter**: AST → Result

The architecture maintains strict separation between:
- **Grammar**: Controls structure (formal, verifiable)
- **LLM**: Assists with semantics (flexible, natural)

This design provides both the rigor of formal language theory and the flexibility of natural language understanding.
