#######################################
# VERBOSE OUTPUT MODULE
# Handles all step-by-step visualization
# and debugging output for the interpreter
#######################################

def format_ast(node):
	"""Format AST node as a tree graph that grows downward"""
	from basic import NumberNode, BinOpNode, UnaryOpNode
	from basic import TT_PLUS, TT_MINUS, TT_MUL, TT_DIV

	def get_node_label(node):
		"""Get the label for a node"""
		if isinstance(node, NumberNode):
			return str(node.tok.value)
		elif isinstance(node, BinOpNode):
			op_symbol = {
				TT_PLUS: "+",
				TT_MINUS: "-",
				TT_MUL: "*",
				TT_DIV: "/"
			}.get(node.op_tok.type, node.op_tok.type)
			return f"BinOp({op_symbol})"
		elif isinstance(node, UnaryOpNode):
			op_symbol = {
				TT_MINUS: "-",
				TT_PLUS: "+"
			}.get(node.op_tok.type, node.op_tok.type)
			return f"Unary({op_symbol})"
		else:
			return str(node)

	def get_children(node):
		"""Get children of a node"""
		if isinstance(node, BinOpNode):
			return [node.left_node, node.right_node]
		elif isinstance(node, UnaryOpNode):
			return [node.node]
		else:
			return []

	def build_tree_lines(node):
		"""Build the tree structure as a list of strings"""
		label = get_node_label(node)
		children = get_children(node)

		if not children:
			# Leaf node - just return the label
			return [label], len(label) // 2, len(label) // 2, len(label)

		# Recursively build children
		child_blocks = []
		child_lefts = []
		child_rights = []
		child_widths = []

		for child in children:
			lines, left, right, width = build_tree_lines(child)
			child_blocks.append(lines)
			child_lefts.append(left)
			child_rights.append(right)
			child_widths.append(width)

		# Calculate spacing between children
		spacing = 3
		total_width = sum(child_widths) + (len(children) - 1) * spacing

		# Calculate positions
		child_positions = []
		pos = 0
		for width in child_widths:
			child_positions.append(pos)
			pos += width + spacing

		# Calculate parent position (center between first and last child)
		if len(children) == 1:
			parent_center = child_positions[0] + child_lefts[0]
		else:
			left_connection = child_positions[0] + child_rights[0]
			right_connection = child_positions[-1] + child_lefts[-1]
			parent_center = (left_connection + right_connection) // 2

		# Build result lines
		result = []

		# Line 0: Parent node label
		label_start = max(0, parent_center - len(label) // 2)
		# Make sure line is long enough for the label
		line_width = max(total_width, label_start + len(label))
		line0 = ' ' * line_width
		line0 = line0[:label_start] + label + line0[label_start + len(label):]
		result.append(line0)

		# Line 1: Vertical line down from parent
		line1 = list(' ' * line_width)
		line1[parent_center] = '|'
		result.append(''.join(line1))

		# Line 2: Horizontal line connecting children
		if len(children) > 1:
			line2 = list(' ' * line_width)
			left_pos = child_positions[0] + child_rights[0]
			right_pos = child_positions[-1] + child_lefts[-1]

			for i in range(left_pos, right_pos + 1):
				line2[i] = '-'
			line2[parent_center] = '+'

			for i, pos in enumerate(child_positions):
				if len(children) > 1:
					line2[pos + child_rights[i]] = '+' if i == 0 else '+'
					line2[pos + child_lefts[i]] = '+' if i == len(children) - 1 else '+'

			result.append(''.join(line2))

			# Line 3: Vertical lines down to children
			line3 = list(' ' * line_width)
			for i, pos in enumerate(child_positions):
				line3[pos + child_lefts[i]] = '|'
			result.append(''.join(line3))
		else:
			# For single child (like unary), just add vertical line
			line3 = list(' ' * line_width)
			line3[parent_center] = '|'
			result.append(''.join(line3))

		# Remaining lines: Child blocks
		max_child_height = max(len(block) for block in child_blocks)
		for line_idx in range(max_child_height):
			# Make line long enough to fit all children
			line_width = max(total_width, max(child_positions[i] + len(block[0]) for i, block in enumerate(child_blocks)))
			line = list(' ' * line_width)
			for i, block in enumerate(child_blocks):
				if line_idx < len(block):
					child_line = block[line_idx]
					pos = child_positions[i]
					for j, char in enumerate(child_line):
						if pos + j < len(line) and char != ' ':
							line[pos + j] = char
			result.append(''.join(line).rstrip())

		# Calculate actual width used
		actual_width = max(len(line) for line in result)
		return result, parent_center, parent_center, actual_width

	lines, _, _, _ = build_tree_lines(node)
	return '\n'.join('   ' + line for line in lines)


def print_verbose_execution(fn, text, tokens, ast_node, result, error):
	"""Print stages 1 and 2 of interpretation (Lexer and Parser)"""
	print("\n" + "="*60)
	print("INTERPRETATION STEPS")
	print("="*60)

	# Stage 1: Lexer
	print("\n1. LEXER (Tokenization):")
	print("-" * 40)
	token_str = "[" + ", ".join(str(tok) for tok in tokens) + "]"
	print(f"   {token_str}")

	# Stage 2: Parser
	print("\n2. PARSER (Abstract Syntax Tree):")
	print("-" * 40)
	print(format_ast(ast_node))

	# Stage 3: Interpreter (will be printed during execution)
	print("\n3. INTERPRETER (Execution):")
	print("-" * 40)


class VerboseInterpreterMixin:
	"""Mixin class to add verbose output capabilities to Interpreter"""

	def __init__(self):
		super().__init__()
		self.indent_level = 0

	def print_step(self, message):
		"""Print interpreter step with proper indentation"""
		indent = "   " * self.indent_level
		print(f"{indent}- {message}")

	def get_operation_info(self, op_tok_type):
		"""Get operation name and symbol from token type"""
		from basic import TT_PLUS, TT_MINUS, TT_MUL, TT_DIV

		op_names = {
			TT_PLUS: "Add",
			TT_MINUS: "Subtract",
			TT_MUL: "Multiply",
			TT_DIV: "Divide"
		}
		op_symbols = {
			TT_PLUS: "+",
			TT_MINUS: "-",
			TT_MUL: "*",
			TT_DIV: "/"
		}
		return op_names.get(op_tok_type, "Operation"), op_symbols.get(op_tok_type, "?")
