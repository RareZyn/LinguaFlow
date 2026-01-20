"""
User-facing help system displaying supported grammar rules.
"""

HELP_TEXT = """
============================================================
LinguaFlow - Natural Command Interpreter
============================================================

SUPPORTED GRAMMAR PATTERNS:

1. SYMBOLIC OPERATIONS (traditional math)
   Format: {number} OPERATOR {number}
   Examples:
      5 + 3
      10 - 4
      6 * 7
      15 / 3
      (5 + 3) * 2

2. INFIX WORDED OPERATIONS
   Format: {number} OPERATOR_WORD {number}
   Examples:
      5 add 3
      10 subtract 4
      6 multiply 7
      15 divide 3

   Supported words:
      Addition: add, plus, sum
      Subtraction: subtract, minus, difference
      Multiplication: multiply, times, product
      Division: divide, split, quotient

3. FUNCTIONAL FORM (list operations)
   Format: WORD these numbers: [{number}, {number}, ...]
   Examples:
      sum these numbers: [5, 3, 7]
      multiply these numbers: [2, 4, 6]
      subtract these numbers: [10, 3, 2]

   Note: Operations apply left-to-right

4. NATURAL PHRASING
   Format: WORD of {number} and {number}
   Examples:
      sum of 5 and 3
      product of 10 and 2.5
      difference of 20 and 5
      quotient of 15 and 3

5. MIXED RULES
   Combine Rules 1 and 2 (symbolic and infix worded operations)
   Examples:
      5 + 4 subtract 2                              (Rule 1 + Rule 2)
      10 * 2 add 5                                  (Rule 1 + Rule 2)
      2 add 3 times 4                               (Rule 2 + Rule 1)
      5 subtract 3 multiply 2                       (Rule 2 + Rule 1)
      5 multiply sum of 2 and 3                     (Rule 2 + Rule 4)

   Note: Rule 4 (natural phrasing) can be used as the right operand
   in worded operations. Rules 3 and 4 cannot be followed by additional
   operators outside of parentheses.

6. NATURAL LANGUAGE CONVERSION
   Format: calc {natural language question}
   Examples:
      calc what is answer of 10 divided by 2
      calc what is 5 plus 3
      calc calculate 5 times 3 minus 2

   The LLM converts the entire question to symbolic form

============================================================
OPERATION WORDS:

LinguaFlow uses an LLM to understand operation synonyms:
   - Addition: sum, add, plus, total, accumulate, combine, etc.
   - Subtraction: subtract, minus, difference, take away, etc.
   - Multiplication: multiply, times, product, etc.
   - Division: divide, split, quotient, etc.

TYPO DETECTION:
   - The LLM can detect and correct typos in operation words
   - Example: "sam" is recognized as "sum"
   - Gibberish is rejected: "asdfas" will produce an error

The LLM only resolves operation words - the grammar handles
all structure! This follows compiler design principles.

============================================================
SPECIAL COMMANDS:

   help     - Show this help message
   rules    - Show this help message
   exit     - Exit the interpreter

============================================================
"""

def print_help():
	"""Display help text to user"""
	print(HELP_TEXT)

def print_rules_summary():
	"""Display quick rule summary"""
	print("\n" + "="*60)
	print("QUICK RULES SUMMARY")
	print("="*60)
	print("1. {number} OPERATOR {number}           (symbolic)")
	print("2. {number} OPERATOR_WORD {number}      (infix worded)")
	print("3. sum these numbers: [5, 3, 7]        (functional)")
	print("4. sum of 5 and 3                      (natural phrasing)")
	print("5. Mix Rules 1 and 2!                  (combined rules)")
	print("   Examples: 5 + 4 subtract 2")
	print("             5 multiply sum of 2 and 3")
	print("6. calc what is 10 divided by 2        (natural language)")
	print("7. create foo as value")
	print("Create func taking param1 param2 do ...")
	print("\nTypo detection enabled (e.g., 'sam' -> 'sum')")
	print("Type 'help' for detailed information")
	print("="*60 + "\n")
