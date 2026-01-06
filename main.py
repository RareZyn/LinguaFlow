import basic
from dotenv import load_dotenv
from help_rules import print_help, print_rules_summary
from gemini_controller import get_gemini_controller

# Load environment variables
load_dotenv()

# Display startup banner
print("\n" + "="*60)
print("  LinguaFlow - Natural Command Interpreter")
print("  Grammar-First Design with LLM Semantic Assistance")
print("="*60)
print_rules_summary()

# Initialize Global Symbol Table ONCE
global_symbol_table = basic.SymbolTable()
global_symbol_table.set("null", basic.Number(0))

while True:
    print("calc > (Type 'RUN' on a new line to execute)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == 'RUN':
            break
        lines.append(line)
    
    text = '\n'.join(lines)
    if not text: continue

    # 1. Handle Commands
    if text.lower() in ['exit', 'quit']:
        break
    elif text.lower() in ['help', 'rules']:
        print_help()
        continue

    # 2. Handle "calc" prefix logic BEFORE running interpreter
    if text.lower().startswith('calc '):
        natural_query = text[5:].strip()
        try:
            gemini = get_gemini_controller()
            symbolic_expr, error = gemini.convert_natural_to_symbolic(natural_query)

            if error:
                print(f"Error: {error}")
                continue

            print(f"\n[Natural Language Conversion] '{natural_query}' → '{symbolic_expr}'")
            text = symbolic_expr 
        except Exception as e:
            print(f"Error converting natural language: {str(e)}")
            continue

    # 3. Run Interpreter (ONLY ONCE)
    result, error = basic.run('<stdin>', text, global_symbol_table)
    
    if error: 
        print(error.as_string())
    elif result:
        # The interpreter already returns the value of the last executed statement
        print(result)