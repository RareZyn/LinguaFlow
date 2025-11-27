"""
User-facing help system displaying supported grammar rules.
"""

HELP_TEXT = """
============================================================
LinguaFlow - Natural Command Interpreter
============================================================

SUPPORTED GRAMMAR PATTERNS:

1. SYMBOLIC OPERATIONS (traditional math)
   Format: {number} SYMBOL {number}
   Examples:
      5 + 3
      10 - 4
      6 * 7
      15 / 3
      (5 + 3) * 2

2. INFIX WORDED OPERATIONS
   Format: {number} WORD {number}
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

============================================================
OPERATION WORDS:

LinguaFlow uses an LLM to understand operation synonyms:
   - Addition: sum, add, plus, total, accumulate, combine, etc.
   - Subtraction: subtract, minus, difference, take away, etc.
   - Multiplication: multiply, times, product, etc.
   - Division: divide, split, quotient, etc.

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
	print("1. {number} + {number}              (symbolic)")
	print("2. {number} add {number}            (infix worded)")
	print("3. sum these numbers: [5, 3, 7]    (functional)")
	print("4. sum of 5 and 3                  (natural phrasing)")
	print("\nType 'help' for detailed information")
	print("="*60 + "\n")
