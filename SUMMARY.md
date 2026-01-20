# LinguaFlow - Complete Feature Summary

## Overview

LinguaFlow is a grammar-first natural command interpreter that combines formal grammar with LLM semantic assistance for mathematical expressions. This document provides a comprehensive overview of all features.

---

## Supported Grammar Rules

### Rule 1: Symbolic Operations
Traditional mathematical notation using symbols.

**Format**: `{number} OPERATOR {number}`

**Examples**:
```
5 + 3              → 8
10 - 4             → 6
6 * 7              → 42
15 / 3             → 5.0
(5 + 3) * 2        → 16
```

**Features**:
- Standard operator precedence (multiplication/division before addition/subtraction)
- Parentheses for grouping
- Unary operators: `-5`, `+3`
- Supports integers and floats

---

### Rule 2: Infix Worded Operations
Mathematical expressions using operation words between numbers.

**Format**: `{number} OPERATOR_WORD {number}`

**Examples**:
```
5 add 3            → 8
10 subtract 4      → 6
6 multiply 7       → 42
15 divide 3        → 5.0
```

**Supported Words**:
- **Addition**: add, plus, sum
- **Subtraction**: subtract, minus, difference
- **Multiplication**: multiply, times, product
- **Division**: divide, split, quotient

---

### Rule 3: Functional Form
Apply operations to lists of numbers.

**Format**: `WORD these numbers: [{number}, {number}, ...]`

**Examples**:
```
sum these numbers: [5, 3, 7]         → 15
multiply these numbers: [2, 4, 6]    → 48
subtract these numbers: [10, 3, 2]   → 5
```

**Behavior**:
- Operations apply left-to-right
- Example: `[5, 3, 7]` with `+` becomes `(5+3)+7 = 15`
- Minimum 1 number required in list
- Commas are optional

---

### Rule 4: Natural Phrasing
Natural language expressions using "of" and "and".

**Format**: `WORD of {number} and {number}`

**Examples**:
```
sum of 5 and 3          → 8
product of 10 and 2.5   → 25.0
difference of 20 and 5  → 15
quotient of 15 and 3    → 5.0
```

**Keywords Required**:
- Must use exact keywords: "of" and "and"
- Order matters: `WORD of {number} and {number}`

---

### Rule 5: Mixed Rules
Combine Rules 1 and 2 (symbolic and infix worded operations).

**Format**: Mix symbolic operators (+, -, *, /) with worded operators (add, subtract, etc.)

**Examples**:
```
5 + 4 subtract 2                        → 7    (Rule 1 + Rule 2)
10 * 2 add 5                            → 25   (Rule 1 + Rule 2)
2 add 3 times 4                         → 14   (Rule 2 + Rule 1)
5 subtract 3 multiply 2                 → 4    (Rule 2 + Rule 1)
5 multiply sum of 2 and 3               → 25   (Rule 2 + Rule 4)
(sum of 5 and 3) - 2                    → 6    (Rule 4 in parentheses + Rule 1)
```

**How It Works**:
- Rule 1 (symbolic) and Rule 2 (infix worded) can be freely mixed
- Rule 4 (natural phrasing) can be used as the right operand in worded operations
- Parser dynamically resolves WORD_OP tokens as encountered
- Maintains standard operator precedence
- Rules 3 and 4 must be wrapped in parentheses to use with other operators

**Supported Combinations**:
- Rule 1 + Rule 2: `5 + 4 subtract 2` ✓
- Rule 2 + Rule 4: `5 multiply sum of 2 and 3` ✓
- Rule 3/4 with operators: Use parentheses like `(sum of 5 and 3) - 2` ✓

**Limitations**:
- Rules 3 and 4 cannot be directly followed by operators without parentheses
- Example: `sum of 5 and 3 - 2` will NOT work (missing parentheses)
- Example: `sum these numbers: [5, 3] * 2` will NOT work (missing parentheses)

---

### Rule 6: Natural Language Conversion
Convert complete natural language questions to symbolic expressions.

**Format**: `calc {natural language question}`

**Examples**:
```
calc what is answer of 10 divided by 2    → 10 / 2 → 5.0
calc what is 5 plus 3                     → 5 + 3 → 8
calc calculate 5 times 3 minus 2          → 5 * 3 - 2 → 13
```

**How It Works**:
1. User types "calc" prefix
2. LLM converts entire sentence to symbolic expression
3. Symbolic expression is processed by normal parser
4. Result is calculated and displayed

**Note**: This is different from other rules - the LLM converts the entire sentence, not just operation words.

---

## LLM Semantic Resolution

### Operation Word Resolution

When the parser encounters an operation word, the LLM resolves it to a mathematical symbol.

**Process**:
1. Parser encounters WORD_OP token (e.g., "sum", "multiply")
2. Query LLM: "Is this word a mathematical operation?"
3. LLM responds with: `+`, `-`, `*`, `/`, or `ERROR`
4. Parser replaces WORD_OP with corresponding operator token
5. Parsing continues normally

**Supported Synonyms**:
- **Addition**: sum, add, plus, total, accumulate, aggregate, combine
- **Subtraction**: subtract, minus, difference, take away, remove
- **Multiplication**: multiply, times, product
- **Division**: divide, split, quotient

---

### Typo Detection

The LLM can detect and correct common typos in operation words while rejecting gibberish.

**Typo Correction Examples**:
```
sam of 5 and 3         → Recognizes "sam" as "sum" → 8
5 multipy 3            → Recognizes "multipy" as "multiply" → 15
prodct of 6 and 7      → Recognizes "prodct" as "product" → 42
```

**Gibberish Rejection Examples**:
```
asdfas of 5 and 3      → ERROR: Unknown operation word
qwerty 5 and 3         → ERROR: Unknown operation word
```

**How It Works**:
- LLM uses natural language understanding to detect close misspellings
- Rejects words with no relation to mathematical operations
- Provides clear error messages for unrecognized words

---

## Special Commands

| Command | Description |
|---------|-------------|
| `help` | Display complete help documentation |
| `rules` | Display quick rules summary |
| `exit` | Exit the interpreter |
| `quit` | Exit the interpreter |

---

## Operator Precedence

LinguaFlow follows standard mathematical operator precedence:

1. **Parentheses**: `()`
2. **Unary operators**: `-`, `+`
3. **Multiplication and Division**: `*`, `/`
4. **Addition and Subtraction**: `+`, `-`

**Examples**:
```
5 + 3 * 2              → 11   (multiply first)
(5 + 3) * 2            → 16   (parentheses first)
5 add 3 multiply 2     → 11   (precedence maintained with words)
```

---

## Error Handling

### Lexical Errors
- **Illegal characters**: `@`, `$`, `#`, etc.
- **Position tracking**: Shows exact location of error

### Syntax Errors
- **Grammar violations**: Missing keywords, incorrect patterns
- **Examples**:
  - `sum 5 and 3` (missing "of")
  - `5 +` (missing operand)
  - `sum of 5` (missing "and" and second operand)

### Runtime Errors
- **Division by zero**: `10 / 0`
- **Traceback**: Shows execution context

### LLM Errors
- **Unknown operation words**: Unrecognizable words or gibberish
- **API errors**: Quota exceeded, connection issues
- **Fallback**: Use symbolic notation if LLM unavailable

---

## Verbose Output

LinguaFlow displays all execution stages for educational purposes:

### Stage 1: Lexer (Tokenization)
Shows how input is broken into tokens:
```
Input: 5 add 3
Tokens: [INT:5, WORD_OP:add, INT:3, EOF]
```

### Stage 2: LLM Resolution
Shows when and how LLM is used:
```
[LLM Resolution] 'add' → '+'
```

### Stage 3: Parser (Abstract Syntax Tree)
Shows the structure recognized by parser:
```
BinOp(+)
  |
+-+-+
|   |
5   3
```

### Stage 4: Interpreter (Execution)
Shows step-by-step evaluation:
```
- Add operation (+):
   - Evaluate left operand: 5
   - Evaluate right operand: 3
   - Result: 5 + 3 = 8
```

### Stage 5: Result
Final computed value:
```
Result: 8
```

---

## Implementation Details

### Grammar-First Design

**Principle**: The formal grammar handles ALL structural recognition. The LLM only assists with semantic meaning.

**What Grammar Does**:
- Recognizes patterns (Rule 1-6)
- Validates syntax
- Builds Abstract Syntax Tree (AST)
- Controls operator precedence

**What LLM Does**:
- Resolves operation word synonyms
- Detects and corrects typos
- Converts natural language to symbolic (Rule 6 only)

**What LLM Does NOT Do**:
- Generate code or expressions (except Rule 6)
- Determine syntax structure
- Execute operations

---

### Parser Enhancements

**Dynamic WORD_OP Resolution**:
- Parser resolves operation words on-the-fly during parsing
- Supports mixed rules without pre-processing
- Maintains operator precedence with worded operators

**Natural Phrasing as Factors**:
- Natural phrasing expressions can be used within larger expressions
- Example: `(sum of 5 and 3) * 2` or `sum of 5 and 3 - 2`

---

## Performance Characteristics

### LLM API Calls

Number of LLM calls per expression:

| Expression | LLM Calls | Reason |
|------------|-----------|--------|
| `5 + 3` | 0 | Pure symbolic |
| `5 add 3` | 1 | One WORD_OP |
| `5 + 4 subtract 2` | 1 | One WORD_OP (subtract) |
| `5 add 4 subtract 2` | 2 | Two WORD_OPs |
| `sum of 5 and 3` | 1 | One WORD_OP |
| `sum of 5 and 3 - 2` | 1 | One WORD_OP (mixed rule) |
| `calc what is 5 plus 3` | 1 | Natural language conversion |

### Optimization Opportunities

Future optimizations could include:
- Caching common operation word resolutions
- Local typo correction before LLM call
- Batch LLM requests for multiple WORD_OPs

---

## Examples by Category

### Basic Operations
```
5 + 3                           → 8
10.5 / 2                        → 5.25
(5 + 3) * 2                     → 16
```

### Worded Operations
```
5 add 3                         → 8
10 multiply 2                   → 20
15 divide 3                     → 5.0
```

### List Operations
```
sum these numbers: [5, 3, 7]              → 15
multiply these numbers: [2, 4, 3]         → 24
```

### Natural Phrasing
```
sum of 5 and 3                  → 8
product of 10 and 2.5           → 25.0
```

### Mixed Rules
```
5 + 4 subtract 2                → 7
sum of 5 and 3 - 2              → 6
10 * 2 add 5                    → 25
(product of 2 and 3) * 4        → 24
```

### Natural Language
```
calc what is 10 divided by 2    → 5.0
calc calculate 5 times 3        → 15
```

### Typo Correction
```
sam of 5 and 3                  → 8
5 multipy 3                     → 15
```

### Complex Expressions
```
5 add 3 multiply 2              → 11
(sum of 2 and 3) * 4            → 20
product of 10 and 2 add 5       → 25
```

---

## Troubleshooting

### "Gemini API key not provided"
**Solution**: Create `.env` file with `GEMINI_API_KEY=your_key`

### "Unknown operation word"
**Possible Causes**:
- Complete gibberish (not a typo)
- Word too far from any mathematical operation

**Solutions**:
- Use clearer synonym
- Use symbolic notation: `+`, `-`, `*`, `/`
- Check spelling

### "Invalid Syntax"
**Possible Causes**:
- Missing keywords ("of", "and", "these", "numbers")
- Incorrect pattern order
- Missing operands

**Solutions**:
- Check pattern matches one of 6 rules
- Use `help` command to see examples
- Verify all required keywords are present

### "LLM quota exceeded"
**Solutions**:
- Wait a few moments
- Check API key has remaining quota
- Use symbolic operations (don't require LLM)

---

## Limitations

1. **Typo Detection**: Very complex or multiple typos might not be caught
2. **Natural Language**: Limited to mathematical expressions only
3. **API Dependency**: Features 2-6 require LLM API access
4. **Quota Limits**: Heavy usage might hit rate limits

---

## Summary

LinguaFlow provides **6 flexible ways** to express mathematical operations:

1. **Symbolic**: Traditional math notation
2. **Infix Worded**: Numbers with operation words
3. **Functional**: List operations
4. **Natural Phrasing**: Conversational syntax
5. **Mixed Rules**: Combine any patterns
6. **Natural Language**: Full sentence conversion

All while maintaining a **grammar-first architecture** where structure is formally defined and the LLM only assists with semantic understanding.
