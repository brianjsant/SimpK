from token_types import TokenType, Token


KEYWORDS = {
    "print": TokenType.PRINT,
}


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0] if text else None

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_spaces_and_tabs(self):
        while self.current_char is not None and self.current_char in (" ", "\t", "\r"):
            self.advance()

    def number(self):
        start = self.pos
        result = ""

        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        return Token(TokenType.INTEGER, int(result), start)

    def identifier(self):
        start = self.pos
        result = ""

        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            result += self.current_char
            self.advance()

        if result in KEYWORDS:
            return Token(KEYWORDS[result], result, start)

        return Token(TokenType.IDENTIFIER, result, start)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char in (" ", "\t", "\r"):
                self.skip_spaces_and_tabs()
                continue

            if self.current_char == "\n":
                self.advance()
                return Token(TokenType.NEWLINE, "\\n", self.pos - 1)

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.STAR, "*")

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.SLASH, "/")

            if self.current_char == "=":
                self.advance()
                return Token(TokenType.EQUAL, "=")

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")")

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha() or self.current_char == "_":
                return self.identifier()

            raise Exception(
                f"Unexpected character '{self.current_char}' at position {self.pos}"
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