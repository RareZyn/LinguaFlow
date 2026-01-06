#######################################
# IMPORTS
#######################################

from strings_with_arrows import *
from verbose_output import VerboseInterpreterMixin, print_verbose_execution
from gemini_controller import get_gemini_controller

#######################################
# CONSTANTS & TOKENS
#######################################

DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Structural keywords that are part of grammar patterns
KEYWORDS = {
    'of', 'and', 'these', 'numbers', 
    'create', 'as', 'find', 'taking', 'do', 'end'
}

#######################################
# ERRORS
#######################################

class Error:
	#Stores position range (pos_start, pos_end)
  #as_string(): Formats error with position indicator using arrows
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details
	
	def as_string(self):
		result  = f'{self.error_name}: {self.details}\n'
		result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

class IllegalCharError(Error):
	#IllegalCharError - Unknown character like @ or $
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
	#InvalidSyntaxError - Grammar violations like 5 + + 3
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
	#Runtime errors like division by zero
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Runtime Error', details)
		self.context = context

	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context

		while ctx:
			result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result

#######################################
# POSITION
# Tracks exact location in source code
#######################################

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx #character index in the text
		self.ln = ln #line number
		self.col = col #column number
		self.fn = fn #filename
		self.ftxt = ftxt #full text of the file

	def advance(self, current_char=None): #(current_char)
	# -	Moves to the next character
  # - Increments index and column
  # - If it encounters \n, increments line number and resets column to 0
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT			= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_WORD_OP  = 'WORD_OP'      # Potential operation word: 'add', 'sum', etc.
TT_KEYWORD  = 'KEYWORD'      # Structural keywords: 'of', 'and', 'these', 'numbers'
TT_LBRACKET = 'LBRACKET'     # [
TT_RBRACKET = 'RBRACKET'     # ]
TT_COMMA    = 'COMMA'        # ,
TT_COLON    = 'COLON'        # :
TT_EOF			= 'EOF'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD    = 'KEYWORD'
TT_EQ         = 'EQ'       # for 'as' logic
TT_NEWLINE    = 'NEWLINE'  # To separate lines

class Token:
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end
	
	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
    """
    Converts raw text into a stream of tokens.
    Now supports both symbolic operators (+, -, *, /) and worded operations (add, sum, etc.)
    """
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in ';\n': # Handle newlines
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_word())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TT_COLON, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        """Extract integer or float from input"""
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_word(self):
        word_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and (self.current_char in LETTERS or self.current_char in DIGITS + '_'):
            word_str += self.current_char
            self.advance()

        word_lower = word_str.lower() # Case insensitive keywords?

        if word_lower in KEYWORDS:
            return Token(TT_KEYWORD, word_lower, pos_start, self.pos)
        else:
            # If not a keyword, it is an Identifier (Variable name)
            return Token(TT_IDENTIFIER, word_str, pos_start, self.pos)

#######################################
# NODES
#######################################

class ListNode:
    def __init__(self, element_nodes):
        self.element_nodes = element_nodes
        self.pos_start = self.element_nodes[0].pos_start if element_nodes else None
        self.pos_end = self.element_nodes[-1].pos_end if element_nodes else None

class NumberNode:
	# - Leaf node containing a single number token
  # - Example: 5 becomes NumberNode(Token(INT, 5))
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	#   - Binary operation with left operand, operator, right operand
  # - Example: 5 + 3 becomes BinOpNode(NumberNode(5), Token(PLUS),NumberNode(3))
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	# - Unary operation (like negation)
  # - Example: -5 becomes UnaryOpNode(Token(MINUS), NumberNode(5))
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class ListOpNode:
	"""
	List operation node for Rule 3: "sum these numbers: [5, 3, 7]"
	Applies operation to all numbers in list left-to-right
	"""
	def __init__(self, op_tok, number_nodes):
		self.op_tok = op_tok  # The resolved operation token (PLUS, MINUS, MUL, DIV)
		self.number_nodes = number_nodes  # List of NumberNode objects

		self.pos_start = self.op_tok.pos_start
		self.pos_end = number_nodes[-1].pos_end if number_nodes else op_tok.pos_end

	def __repr__(self):
		return f'ListOp({self.op_tok}, {self.number_nodes})'
      
class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
        self.pos_start = self.node_to_call.pos_start
        
        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[-1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

#######################################
# PARSE RESULT
#######################################

class ParseResult:
	#Wrapper for parser results to track errors
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		#If the result has an error, propagate it upward
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node

		return res

	def success(self, node):
		#Mark parsing succeeded, return the AST node
		self.node = node
		return self

	def failure(self, error):
		#Mark parsing failed, store the error
		self.error = error
		return self

#######################################
# PARSER
#######################################

class Parser:
    """
    Parser with grammar-first approach + LLM semantic resolution.
    
    Supports:
    1. Statements: create x as 5, find func x
    2. Symbolic Math: 5 + 3
    3. Natural Phrasing: sum of 5 and 3
    """
    def __init__(self, tokens, use_llm=True):
        self.tokens = tokens
        self.tok_idx = -1
        self.use_llm = use_llm
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def peek(self, offset=1):
        """Look ahead at token without advancing"""
        peek_idx = self.tok_idx + offset
        if peek_idx < len(self.tokens):
            return self.tokens[peek_idx]
        return None

    def parse(self):
        # Entry point: Parse a list of statements
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Unexpected token"
            ))
        return res

    ###################################
    # Statement Parsing (Level 0)
    ###################################

    def statements(self):
        statements = []
        res = ParseResult()

        # Skip empty lines at start
        while self.current_tok.type == TT_NEWLINE:
            res.register(self.advance())

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True
        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register(self.advance())
                newline_count += 1
            
            if newline_count == 0: break
            
            statement = res.register(self.statement())
            if not statement: break
            statements.append(statement)

        return res.success(ListNode(statements))

    def statement(self):
        # Check for keywords first
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'create':
            return self.create_statement()
        elif self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'find':
            return self.call_statement()
        
        # If not a keyword statement, it's a math expression
        expr = self.expr()
        if expr.error:
            # If we can't parse an expression, it might be the end of a block (like 'end')
            return None 
        return expr

    def create_statement(self):
        res = ParseResult()
        res.register(self.advance()) # consume 'create'

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier"))
        
        var_name = self.current_tok
        res.register(self.advance())

        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'as':
            # Variable Assignment: create x as 5
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))
        
        elif self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'taking':
            # Function Definition: create func taking a b do ... end
            res.register(self.advance())
            arg_name_toks = []

            while self.current_tok.type == TT_IDENTIFIER:
                arg_name_toks.append(self.current_tok)
                res.register(self.advance())
            
            if self.current_tok.type != TT_KEYWORD or self.current_tok.value != 'do':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'do'"))
            
            res.register(self.advance())

            body = res.register(self.statements())
            if res.error: return res

            if self.current_tok.type != TT_KEYWORD or self.current_tok.value != 'end':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'end'"))
            
            res.register(self.advance())
            return res.success(FuncDefNode(var_name, arg_name_toks, body))

        return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'as' or 'taking'"))

    def call_statement(self):
        # Grammar: find FUNC_NAME ARG1 ARG2 ...
        res = ParseResult()
        res.register(self.advance()) # consume 'find'

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected Function Name"))
        
        node_to_call = VarAccessNode(self.current_tok)
        res.register(self.advance())

        arg_nodes = []
        # Greedily consume factors as arguments until Newline or EOF
        while self.current_tok.type not in (TT_NEWLINE, TT_EOF, TT_KEYWORD, TT_RBRACKET):
            arg = res.register(self.factor()) 
            if res.error: break
            arg_nodes.append(arg)
        
        return res.success(CallNode(node_to_call, arg_nodes))

    ###################################
    # Expression Parsing (Level 1)
    ###################################

    def expr(self):
        res = ParseResult()

        # Check for Natural Language Rules first
        if self.current_tok.type == TT_WORD_OP:
            if self.peek() and self.peek().type == TT_KEYWORD and self.peek().value == 'these':
                return self.functional_expr()
            elif self.peek() and self.peek().type == TT_KEYWORD and self.peek().value == 'of':
                return self.natural_phrasing_expr()

        # Fallback to Symbolic/Infix
        return self.symbolic_expr()

    def symbolic_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS, TT_WORD_OP))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_WORD_OP))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        # 1. Unary Operation (+5, -5)
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        # 2. Numbers
        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        # 3. Variables (Identifiers)
        elif tok.type == TT_IDENTIFIER:
            res.register(self.advance())
            return res.success(VarAccessNode(tok))

        # 4. Parentheses
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"))

        # 5. Nested Natural Language Rules (Recursive)
        elif tok.type == TT_WORD_OP:
            if self.peek() and self.peek().type == TT_KEYWORD and self.peek().value == 'these':
                return self.functional_expr()
            elif self.peek() and self.peek().type == TT_KEYWORD and self.peek().value == 'of':
                return self.natural_phrasing_expr()
            else:
                return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float, identifier, or '('"))

        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float, identifier, or '('"))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        # Loop while token is an operator OR a potential identifier (word)
        # Using parentheses () allows multi-line checks without backslashes
        while (self.current_tok.type in ops or 
               self.current_tok.type == TT_IDENTIFIER):
            
            op_tok = self.current_tok

            # 1. AI Logic: If it is a word, ask Gemini
            if op_tok.type == TT_IDENTIFIER:
                resolved_op, error = self.resolve_word_op(op_tok)
                
                if error:
                    # AI says it's not a math word. 
                    # It might be the start of a new variable (e.g. "x").
                    # Break the loop so the parser can handle it elsewhere.
                    break
                
                # If valid, switch the token to the resolved symbol (e.g., PLUS)
                op_tok = resolved_op

                # CRITICAL PRECEDENCE CHECK:
                # If we found '+' but this function is only looking for '*' (term),
                # we must stop here.
                if op_tok.type not in ops:
                    break

            # 2. Standard Logic: Consume the operator and parse the right side
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    ###################################
    # Specific Grammar Rules
    ###################################

    def functional_expr(self):
        # Pattern: WORD_OP these numbers: [ ... ]
        res = ParseResult()
        word_tok = self.current_tok
        resolved_op, error = self.resolve_word_op(word_tok)
        if error: return res.failure(InvalidSyntaxError(word_tok.pos_start, word_tok.pos_end, error))
        res.register(self.advance())

        res.register(self.advance()) # these
        res.register(self.advance()) # numbers
        res.register(self.advance()) # :
        res.register(self.advance()) # [

        number_nodes = []
        while self.current_tok.type in (TT_INT, TT_FLOAT):
            number_nodes.append(NumberNode(self.current_tok))
            res.register(self.advance())
            if self.current_tok.type == TT_COMMA:
                res.register(self.advance())

        if self.current_tok.type != TT_RBRACKET:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ']'"))
        res.register(self.advance())

        return res.success(ListOpNode(resolved_op, number_nodes))

    def natural_phrasing_expr(self):
        # Pattern: WORD_OP of X and Y
        res = ParseResult()
        word_tok = self.current_tok
        resolved_op, error = self.resolve_word_op(word_tok)
        if error: return res.failure(InvalidSyntaxError(word_tok.pos_start, word_tok.pos_end, error))
        res.register(self.advance())

        res.register(self.advance()) # of
        
        left_node = NumberNode(self.current_tok)
        if self.current_tok.type not in (TT_INT, TT_FLOAT):
             return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected number"))
        res.register(self.advance())

        res.register(self.advance()) # and

        right_node = NumberNode(self.current_tok)
        if self.current_tok.type not in (TT_INT, TT_FLOAT):
             return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected number"))
        res.register(self.advance())

        return res.success(BinOpNode(left_node, resolved_op, right_node))

    def resolve_word_op(self, word_tok):
        if not self.use_llm:
            return None, f"Cannot resolve operation word '{word_tok.value}' without LLM"
        try:
            gemini = get_gemini_controller()
            symbol, error = gemini.resolve_operation_word(word_tok.value)
            if error: return None, error

            symbol_to_type = {'+': TT_PLUS, '-': TT_MINUS, '*': TT_MUL, '/': TT_DIV}
            if symbol not in symbol_to_type: return None, f"Invalid symbol '{symbol}' returned by LLM"

            print(f"\n[LLM Resolution] '{word_tok.value}' → '{symbol}'")
            return Token(symbol_to_type[symbol], symbol, word_tok.pos_start, word_tok.pos_end), None
        except Exception as e:
            return None, f"LLM error: {str(e)}"

#######################################
# RUNTIME RESULT
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

#######################################
# VALUES
#######################################

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)

#######################################
# CONTEXT
#######################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos

#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent # Parent scope (for functions)

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

#######################################
# INTERPRETER & VALUE
#######################################

class Interpreter(VerboseInterpreterMixin):
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################
    # Standard Math Visits
    ###################################

    def visit_NumberNode(self, node, context):
        self.print_step(f"Visit NumberNode: {node.tok.value}")
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_BinOpNode(self, node, context):
        res = RTResult()

        # Get operation name and symbol
        op_name, op_symbol = self.get_operation_info(node.op_tok.type)

        self.print_step(f"{op_name} operation ({op_symbol}):")

        # Visit left node
        self.indent_level += 1
        self.print_step("Evaluate left operand:")
        self.indent_level += 1
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        self.indent_level -= 1

        # Visit right node
        self.print_step("Evaluate right operand:")
        self.indent_level += 1
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        self.indent_level -= 1

        # Perform operation
        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)

        if error:
            return res.failure(error)
        else:
            self.print_step(f"Result: {left.value} {op_symbol} {right.value} = {result.value}")
            self.indent_level -= 1
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()

        self.print_step(f"Unary operation ({node.op_tok.type}):")
        self.indent_level += 1

        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
            self.print_step(f"Negate: -{number.value}")

        self.indent_level -= 1

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_ListOpNode(self, node, context):
        """
        Handle list operations: sum these numbers: [5, 3, 7]
        Apply operation left-to-right: 5 + 3 + 7
        """
        res = RTResult()

        op_name, op_symbol = self.get_operation_info(node.op_tok.type)
        self.print_step(f"List {op_name} operation:")
        self.indent_level += 1

        if len(node.number_nodes) == 0:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                "Cannot perform operation on empty list",
                context
            ))

        # Start with first number
        result = res.register(self.visit(node.number_nodes[0], context))
        if res.error: return res

        # Apply operation to remaining numbers
        for i in range(1, len(node.number_nodes)):
            next_num = res.register(self.visit(node.number_nodes[i], context))
            if res.error: return res

            # Perform operation
            if node.op_tok.type == TT_PLUS:
                result, error = result.added_to(next_num)
            elif node.op_tok.type == TT_MINUS:
                result, error = result.subbed_by(next_num)
            elif node.op_tok.type == TT_MUL:
                result, error = result.multed_by(next_num)
            elif node.op_tok.type == TT_DIV:
                result, error = result.dived_by(next_num)

            if error:
                return res.failure(error)

        self.print_step(f"Final result: {result.value}")
        self.indent_level -= 1
        return res.success(result.set_pos(node.pos_start, node.pos_end))

    ###################################
    # New Statement & Function Visits
    ###################################

    def visit_ListNode(self, node, context):
        # Visits a list of statements
        res = RTResult()
        elements = []
        
        # Make sure your ListNode class has 'element_nodes' attribute
        for element_node in node.element_nodes: 
            elements.append(res.register(self.visit(element_node, context)))
            if res.error: return res
        
        # Return the result of the LAST statement executed
        if len(elements) > 0:
            return res.success(elements[-1]) 
        return res.success(Number(0))

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(node.pos_start, node.pos_end, f"'{var_name}' is not defined", context))
        
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_FuncDefNode(self, node, context):
        res = RTResult()
        func_name = node.var_name_tok.value
        body_node = node.body_node
        arg_names = node.arg_name_toks
        
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)
        context.symbol_table.set(func_name, func_value)
        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        # Ensure value_to_call is actually a function before executing
        if isinstance(value_to_call, BaseFunction):
            call_res = value_to_call.execute(args)
            return res.success(call_res.value)
        
        return res.failure(RTError(node.pos_start, node.pos_end, "Identifier is not a function", context))
    	
class BaseFunction(Number):
    def __init__(self, name):
        super().__init__(0)
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()
        if len(args) != len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args)} args passed, {len(arg_names)} expected",
                self.context
            ))
        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name.value, arg_value)

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    # --- ADD THIS METHOD ---
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    # -----------------------

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_args(self.arg_names, args))
        if res.error: return res

        self.populate_args(self.arg_names, args, exec_ctx)

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.error: return res
        return res.success(value)

#######################################
# RUN
#######################################

def run(fn, text, symbol_table):
    """
    Execute the interpreter pipeline.
    
    Args:
        fn: Filename (usually '<stdin>')
        text: Input text to process
        symbol_table: The global memory for variables
    """
    # 1. Generate Tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # 2. Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # Optional: Print verbose output if you want to see the tree
    # print_verbose_execution(fn, text, tokens, ast.node, None, None)

    # 3. Run Interpreter
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = symbol_table  # Set the persistent memory
    
    result = interpreter.visit(ast.node, context)

    # 4. Return Result
    if result.error:
        return None, result.error
    
    # If the result is a list of statements, we usually just return the value of the last one
    return result.value, None