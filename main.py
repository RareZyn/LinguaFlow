import basic

while True:
    text = input('calc > ')
    result, error = basic.run('<stdin>',text)
    if error: print(error.as_string())
    else: print(result)

#   Overall Program Flow

#   When you enter 5 + 3 * 2 in the REPL, here's what happens:

#   Input: "5 + 3 * 2"
#     ↓
#   [Lexer] → Tokens: [INT:5, PLUS, INT:3, MUL, INT:2, EOF]
#     ↓
#   [Parser] → AST: BinOpNode(5, +, BinOpNode(3, *, 2))
#     ↓
#   [Interpreter] → Result: 11