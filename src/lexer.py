from token_types import TokenType, Token
 
KEYWORDS = {
    "print":  TokenType.PRINT,
    "func":   TokenType.FUNC,
    "return": TokenType.RETURN,
    "if":     TokenType.IF,
    "then":   TokenType.THEN,
    "else":   TokenType.ELSE,
    "input":  TokenType.INPUT,
}
 
 
class LexerError(Exception):
    def __init__(self, message, position):
        super().__init__(message)
        self.position = position
 
 
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0] if text else None
 
    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
 
    def peek(self):
        peek_pos = self.pos + 1
        return self.text[peek_pos] if peek_pos < len(self.text) else None
 
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in (' ', '\t', '\r'):
            self.advance()
 
    def skip_comment(self):
        # Comments start with #
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
 
    def read_number(self):
        start = self.pos
        result = ''
        is_float = False
 
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
 
        if self.current_char == '.' and (self.peek() is None or self.peek().isdigit() or self.peek() == ' '):
            is_float = True
            result += '.'
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
 
        if is_float:
            return Token(TokenType.FLOAT, float(result), start)
        return Token(TokenType.INTEGER, int(result), start)
 
    def read_identifier(self):
        start = self.pos
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        token_type = KEYWORDS.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, start)
 
    def get_next_token(self):
        while self.current_char is not None:
            # Whitespace
            if self.current_char in (' ', '\t', '\r'):
                self.skip_whitespace()
                continue
 
            # Comment
            if self.current_char == '#':
                self.skip_comment()
                continue
 
            # Newline
            if self.current_char == '\n':
                self.advance()
                return Token(TokenType.NEWLINE, '\\n', self.pos - 1)
 
            # Numbers
            if self.current_char.isdigit():
                return self.read_number()
 
            # Identifiers / keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()
 
            # Two-character operators
            if self.current_char == '=' and self.peek() == '=':
                self.advance(); self.advance()
                return Token(TokenType.EQEQ, '==', self.pos - 2)
 
            # Single-character tokens
            char = self.current_char
            self.advance()
 
            if char == '=':  return Token(TokenType.EQUAL,    '=')
            if char == '+':  return Token(TokenType.PLUS,     '+')
            if char == '-':  return Token(TokenType.MINUS,    '-')
            if char == '*':  return Token(TokenType.STAR,     '*')
            if char == '/':  return Token(TokenType.SLASH,    '/')
            if char == '>':  return Token(TokenType.GT,       '>')
            if char == '<':  return Token(TokenType.LT,       '<')
            if char == '(':  return Token(TokenType.LPAREN,   '(')
            if char == ')':  return Token(TokenType.RPAREN,   ')')
            if char == '[':  return Token(TokenType.LBRACKET, '[')
            if char == ']':  return Token(TokenType.RBRACKET, ']')
            if char == '{':  return Token(TokenType.LBRACE,   '{')
            if char == '}':  return Token(TokenType.RBRACE,   '}')
            if char == ',':  return Token(TokenType.COMMA,    ',')
 
            raise LexerError(
                f"Unexpected character '{char}' at position {self.pos - 1}",
                self.pos - 1
            )
 
        return Token(TokenType.EOF, None, self.pos)
 
    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
