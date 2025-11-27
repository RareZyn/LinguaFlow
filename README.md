# LinguaFlow - Quick Start Guide

## What is LinguaFlow?

LinguaFlow is a **grammar-first natural command interpreter** that combines formal grammar with LLM semantic assistance. It allows you to write mathematical expressions in 4 different ways - from traditional symbols to natural language phrases.

**Key Feature**: The grammar handles ALL structure. The LLM only helps resolve operation words (is "sum" the same as "+"?).

---

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up your Gemini API key** (for LLM features):
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

Get a free API key at: https://makersuite.google.com/app/apikey

---

## Running LinguaFlow

```bash
python main.py
```

You'll see a welcome screen with rule examples, then the `calc >` prompt.

---

## Supported Input Formats

### 1. Symbolic (Traditional Math)
```
calc > 5 + 3
Result: 8

calc > (5 + 3) * 2
Result: 16

calc > 10.5 / 2
Result: 5.25
```

### 2. Infix Worded
```
calc > 5 add 3
[LLM Resolution] 'add' → '+'
Result: 8

calc > 10 multiply 2
[LLM Resolution] 'multiply' → '*'
Result: 20

calc > 15 divide 3
[LLM Resolution] 'divide' → '/'
Result: 5.0
```

### 3. Functional Form (List Operations)
```
calc > sum these numbers: [5, 3, 7]
[LLM Resolution] 'sum' → '+'
Result: 15

calc > multiply these numbers: [2, 4, 3]
[LLM Resolution] 'multiply' → '*'
Result: 24
```

### 4. Natural Phrasing
```
calc > sum of 5 and 3
[LLM Resolution] 'sum' → '+'
Result: 8

calc > product of 10 and 2.5
[LLM Resolution] 'product' → '*'
Result: 25.0

calc > difference of 20 and 5
[LLM Resolution] 'difference' → '-'
Result: 15
```

---

## Special Commands

```
calc > help          # Show detailed help
calc > rules         # Show rule summary
calc > exit          # Quit the interpreter
```

---

## Understanding LLM Resolution

When you use operation words (add, sum, multiply, etc.), LinguaFlow:

1. **Recognizes the grammar pattern** (e.g., "5 add 3" matches Rule 2)
2. **Asks LLM**: "Is 'add' a synonym for +, -, *, or /?"
3. **LLM responds**: "+"
4. **Displays resolution**: `[LLM Resolution] 'add' → '+'`
5. **Continues parsing** with the resolved symbol

The LLM understands many synonyms:
- **Addition**: add, sum, plus, total, accumulate, combine, etc.
- **Subtraction**: subtract, minus, difference, take away, etc.
- **Multiplication**: multiply, times, product, etc.
- **Division**: divide, split, quotient, etc.

---


## Understanding Output

LinguaFlow shows verbose execution steps:

```
calc > 5 add 3

============================================================
INTERPRETATION STEPS
============================================================

1. LEXER (Tokenization):
----------------------------------------
   [INT:5, WORD_OP:add, INT:3, EOF]

[LLM Resolution] 'add' → '+'

2. PARSER (Abstract Syntax Tree):
----------------------------------------
   BinOp(+)
     |
   +-+-+
   |   |
   5   3

3. INTERPRETER (Execution):
----------------------------------------
   - Add operation (+):
      - Evaluate left operand: 5
      - Evaluate right operand: 3
      - Result: 5 + 3 = 8

4. RESULT:
----------------------------------------
   8
============================================================
```

This helps you understand:
- How input is tokenized (Lexer)
- How the syntax tree is built (Parser)
- When LLM resolution occurs
- How the expression is evaluated (Interpreter)

---

## Troubleshooting

### "Gemini API key not provided"
- Make sure you have a `.env` file in the project directory
- The file should contain: `GEMINI_API_KEY=your_actual_api_key`
- Get a free key at https://makersuite.google.com/app/apikey

### "Unknown operation word"
- The LLM couldn't recognize the word as a math operation
- Try using a clearer synonym (e.g., "add" instead of "xadd")
- Or use symbolic notation: `+`, `-`, `*`, `/`

### "Invalid Syntax" errors
- Check the pattern matches one of the 4 rules
- For Rule 3 (functional), use exact syntax: `sum these numbers: [1, 2, 3]`
- For Rule 4 (natural), use exact syntax: `sum of 5 and 3`

---

## Example Session

```
calc > 5 + 3
Result: 8

calc > 5 add 3
[LLM Resolution] 'add' → '+'
Result: 8

calc > sum these numbers: [5, 3, 7]
[LLM Resolution] 'sum' → '+'
Result: 15

calc > product of 10 and 2.5
[LLM Resolution] 'product' → '*'
Result: 25.0

calc > help
[Shows detailed help documentation]

calc > exit
Goodbye!
```

---

## What Makes LinguaFlow Special?

1. **Grammar-First Design**: Structure is defined by formal grammar, not AI guesswork
2. **LLM as Helper**: AI only validates word meanings, doesn't generate code
3. **Explainable**: You see exactly when and how LLM is used
4. **Flexible**: 4 different ways to express the same operation
5. **Educational**: Shows compiler pipeline stages (Lexer → Parser → Interpreter)
6. **Compiler Principles**: Follows academic compiler design patterns

