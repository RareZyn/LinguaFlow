import basic
import sys
import os
from dotenv import load_dotenv
from help_rules import print_help, print_rules_summary
from gemini_controller import get_gemini_controller

# Load environment variables
load_dotenv()

def run_code(text, filename, symbol_table):
    """Execute LinguaFlow code and return result."""
    # Handle "calc" prefix logic for natural language conversion
    if text.lower().startswith('calc '):
        natural_query = text[5:].strip()
        try:
            gemini = get_gemini_controller()
            symbolic_expr, error = gemini.convert_natural_to_symbolic(natural_query)

            if error:
                print(f"Error: {error}")
                return None, None

            print(f"\n[Natural Language Conversion] '{natural_query}' -> '{symbolic_expr}'")
            text = symbolic_expr
        except Exception as e:
            print(f"Error converting natural language: {str(e)}")
            return None, None

    # Run Interpreter
    result, error = basic.run(filename, text, symbol_table)
    return result, error


def run_file(filepath):
    """Execute a .lf file."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    # Check file extension
    if not filepath.endswith('.lf'):
        print(f"Warning: File '{filepath}' does not have .lf extension.")

    # Read file contents
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    if not code.strip():
        print("Error: File is empty.")
        sys.exit(1)

    # Initialize symbol table
    symbol_table = basic.SymbolTable()
    symbol_table.set("null", basic.Number(0))

    # Display what file is being run
    filename = os.path.basename(filepath)
    print(f"\n[Running {filename}]\n")

    # Execute the code
    result, error = run_code(code, filepath, symbol_table)

    if error:
        print("\n" + "!" * 60)
        print("ERROR OCCURRED")
        print("!" * 60)
        print(error.as_string())
        print("!" * 60 + "\n")
        sys.exit(1)
    elif result:
        print("\n" + "=" * 60)
        print(f"RESULT: {result}")
        print("=" * 60 + "\n")


def run_repl():
    """Run interactive REPL mode."""
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

        # Handle Commands
        if text.lower() in ['exit', 'quit']:
            break
        elif text.lower() in ['help', 'rules']:
            print_help()
            continue

        # Run the code
        result, error = run_code(text, '<stdin>', global_symbol_table)

        if error:
            print("\n" + "!" * 60)
            print("ERROR OCCURRED")
            print("!" * 60)
            print(error.as_string())
            print("!" * 60 + "\n")
        elif result:
            print("\n" + "=" * 60)
            print(f"RESULT: {result}")
            print("=" * 60 + "\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # File mode: python main.py script.lf
        run_file(sys.argv[1])
    else:
        # REPL mode: python main.py
        run_repl()