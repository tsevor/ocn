VALID_IN_SYMBOL_NAME = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
VALID_IN_SYMBOL_NAME_START = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
OPERATORS_IN_EXPRESSION = "+-*/%()"
OPERATORS = "(){}[];:*=,-."
WHITESPACE = " \t\r\n"

TOKEN_NAMES = [
	"VARIABLE", # $VAR
	"LPAREN", # (
	"RPAREN", # )
]

KEYWORDS = [
	"obj",
	"scene",
	"import",
	"as",
]

KWT_NAMES = {
	"obj": "KEYWORD_OBJECT",
	"scene": "KEYWORD_SCENE",
	"import": "KEYWORD_IMPORT",
	"as": "KEYWORD_AS",
}

class Token:
	def __init__(self, type, value):
		self.type = type
		self.value = value


class Lexer:

	def __init__(self, text):
		self.line = 1
		self.col = 1
		self.pos = 0
		self.text = text
		self.tokens = []
		self.depth = 0

	def tokenize(self):
		while self.pos < len(self.text) - 1:
			self.next_token()

	def next_token(self):
		ptr = 0

		if self.comment_check():
			return

		if self.whitespace_check():
			return

		# variables and expressions
		if self.get(ptr) == "$":
			ptr += 1
			if self.get(ptr) in VALID_IN_SYMBOL_NAME_START:
				while self.get(ptr) in VALID_IN_SYMBOL_NAME:
					ptr += 1
				self.add_token("VARIABLE", self.advance(ptr))
				return
			elif self.get(ptr) == "(":
				ptr += 1
				self.add_token("EXPRESSION_OPEN", self.advance(ptr))
				self.depth += 1
				self.tokenize_expression()
				return

		if self.get(ptr) in OPERATORS:
			if self.get(ptr) == "(":
				ptr += 1
				self.add_token("LPAREN", self.advance(ptr))
			elif self.get(ptr) == ")":
				ptr += 1
				self.add_token("RPAREN", self.advance(ptr))
			elif self.get(ptr) == "{":
				ptr += 1
				self.add_token("LBRACE", self.advance(ptr))
			elif self.get(ptr) == "}":
				ptr += 1
				self.add_token("RBRACE", self.advance(ptr))
			elif self.get(ptr) == "[":
				ptr += 1
				self.add_token("LBRACKET", self.advance(ptr))
			elif self.get(ptr) == "]":
				ptr += 1
				self.add_token("RBRACKET", self.advance(ptr))
			elif self.get(ptr) == "=":
				ptr += 1
				self.add_token("ASSIGNMENT", self.advance(ptr))
			elif self.get(ptr) == ",":
				ptr += 1
				self.add_token("COMMA", self.advance(ptr))
			elif self.get(ptr) == ":":
				ptr += 1
				self.add_token("COLON", self.advance(ptr))
			elif self.get(ptr) == "*":
				ptr += 1
				self.add_token("STAR", self.advance(ptr))
			elif self.get(ptr) == ";":
				ptr += 1
				self.add_token("SEMICOLON", self.advance(ptr))
			elif self.get(ptr) == ".":
				ptr += 1
				self.add_token("DOT", self.advance(ptr))
			elif self.get(ptr) == "-":
				ptr += 1
				self.add_token("MINUS", self.advance(ptr))
			return

		if self.word_check():
			return

		if self.literal_check():
			return

		# error
		else:
			print(self.advance(1), end="")

	def tokenize_expression(self):
		depth = self.depth
		while self.depth >= depth:
			self.next_token_expression()

	def next_token_expression(self):
		ptr = 0

		if self.comment_check():
			return

		if self.whitespace_check():
			return

		# variables
		if self.get(ptr) == "$":
			ptr += 1
			if self.get(ptr) in VALID_IN_SYMBOL_NAME_START:
				while self.get(ptr) in VALID_IN_SYMBOL_NAME:
					ptr += 1
				self.add_token("VARIABLE", self.advance(ptr))
				return
			else:
				raise SyntaxError(f"invalid character after $ in expression at line:{self.line}:{self.col}")

		if self.get(ptr) in OPERATORS_IN_EXPRESSION:
			if self.get(ptr) in "+-":
				ptr += 1
				self.add_token("PLUSMINUSOPER", self.advance(ptr))
			elif self.get(ptr) in "*/%":
				ptr += 1
				self.add_token("MULTDIVOPER", self.advance(ptr))
			elif self.get(ptr) == "(":
				ptr += 1
				self.add_token("LPAREN", self.advance(ptr))
				self.depth += 1
			elif self.get(ptr) == ")":
				ptr += 1
				self.add_token("RPAREN", self.advance(ptr))
				self.depth -= 1
			return

		if self.literal_check():
			return

		# all words fail here

		raise SyntaxError(f"invalid character in expression at line {self.line}:{self.col}")

	def comment_check(self):
		ptr = 0
		if self.get(ptr) == "#":
			while self.get(ptr) != "\n":
				ptr += 1
				if self.pos + ptr >= len(self.text):
					return True
			self.advance(ptr)
			self.line += 1
			self.col = 1
			return True
		return False

	def whitespace_check(self):
		ptr = 0
		if self.get(ptr) in WHITESPACE:
			while self.get(ptr) in WHITESPACE:
				if self.get(ptr) == "\n":
					self.line += 1
					self.col = 0 # advance adds 1
					if self.pos + ptr >= len(self.text):
						return True
				ptr += 1
			self.advance(ptr)
			return True
		return False

	def literal_check(self):
		ptr = 0
		char = self.get(ptr)

		# Strings
		if char == "\"":
			while True:
				ptr += 1
				curr = self.get(ptr)
				if curr == "": # EOF handling
					raise SyntaxError(f"Unterminated string at {self.line}:{self.col}")
				if curr == "\\":
					ptr += 1 # Skip escaped char
					continue
				if curr == "\"":
					ptr += 1
					self.add_token("LITERAL_STRING", self.advance(ptr))
					return True

		# Numbers
		if char.isnumeric():
			# Base handling (0b, 0o, 0x)
			if char == "0":
				next_char = self.get(ptr + 1)
				if next_char in "box":
					base_char = next_char
					ptr += 2
					valid_set = {
						"b": "01_",
						"o": "01234567_",
						"x": "0123456789ABCDEFabcdef_"
					}[base_char]

					while self.get(ptr) in valid_set:
						ptr += 1
					
					# Define suffixes separately to avoid f-string nesting issues
					suffixes = {'b': 'BIN', 'o': 'OCT', 'x': 'HEX'}
					token_type = f"LITERAL_{suffixes[base_char]}_INT"
					
					self.add_token(token_type, self.advance(ptr))
					return True

				elif self.get(ptr + 1).isnumeric():
					raise SyntaxError(f"Leading zero on decimal number at {self.line}:{self.col}")

			# Standard Int / Float / Scientific
			has_dot = False
			has_exponent = False

			while True:
				curr = self.get(ptr)
				if curr.isnumeric() or curr == "_":
					ptr += 1
				elif curr == "." and not has_dot and not has_exponent:
					has_dot = True
					ptr += 1
				elif curr in "eE" and not has_exponent:
					has_exponent = True
					ptr += 1
					if self.get(ptr) in "+-":
						ptr += 1
				else:
					break

			token_type = "LITERAL_FLOAT" if (has_dot or has_exponent) else "LITERAL_INT"
			self.add_token(token_type, self.advance(ptr))
			return True

		# Keywords / Named Literals
		keywords = {
			"true": "LITERAL_BOOL",
			"false": "LITERAL_BOOL",
			"null": "LITERAL_NULL",
			"inf": "LITERAL_FLOAT",
			"nan": "LITERAL_FLOAT"
		}

		for word, t_type in keywords.items():
			length = len(word)
			if self.getslice(ptr, ptr + length) == word:
				if self.get(ptr + length) not in VALID_IN_SYMBOL_NAME:
					self.add_token(t_type, self.advance(length))
					return True

		return False

	def word_check(self):
		ptr = 0
		if self.get(ptr) in VALID_IN_SYMBOL_NAME_START:
			while self.get(ptr) in VALID_IN_SYMBOL_NAME:
				ptr += 1
			word = self.advance(ptr)
			if word in KEYWORDS:
				self.add_token(KWT_NAMES[word], word)
			else:
				self.add_token("WORD", word)
			return True
		return False

	def get(self, ptr):
		return self.text[self.pos + ptr]

	def getslice(self, ptr, ptr2):
		return self.text[self.pos + ptr : self.pos + ptr2]

	def advance(self, amount):
		self.col += amount
		removed = self.getslice(0, amount)
		self.pos += amount
		return removed

	def add_token(self, type, value = None):
		self.tokens.append(Token(type, value))
		print(f"\n{self.line}:{self.col}: {type}({value})")





def loads(ocn_text):
	lexer = Lexer(ocn_text)
	lexer.tokenize()


def load(filename):
	with open(filename, "r") as f:
		data = f.read()

	return loads(data)
