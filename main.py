import basic
from dotenv import load_dotenv
from help_rules import print_help, print_rules_summary

# Load environment variables from .env file
load_dotenv()

# Display startup banner and rules
print("\n" + "="*60)
print("  LinguaFlow - Natural Command Interpreter")
print("  Grammar-First Design with LLM Semantic Assistance")
print("="*60)
print_rules_summary()

while True:
    text = input('calc > ').strip()

    # Handle special commands
    if text.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
    elif text.lower() in ['help', 'rules']:
        print_help()
        continue
    elif text == '':
        continue

    # Run interpreter
    result, error = basic.run('<stdin>', text)
    if error: print(error.as_string())

#   Overall Program Flow

#   When you enter 5 + 3 * 2 in the REPL, here's what happens:

#   Input: "5 + 3 * 2"
#     ↓
#   [Lexer] → Tokens: [INT:5, PLUS, INT:3, MUL, INT:2, EOF]
#     ↓
#   [Parser] → AST: BinOpNode(5, +, BinOpNode(3, *, 2))
#     ↓
#   [Interpreter] → Result: 11