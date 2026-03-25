from enum import Enum, auto


class TokenType(Enum):
    INTEGER = auto()
    IDENTIFIER = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQUAL = auto()

    LPAREN = auto()
    RPAREN = auto()

    PRINT = auto()
    NEWLINE = auto()
    EOF = auto()


class Token:
    def __init__(self, token_type, value=None, position=None):
        self.type = token_type
        self.value = value
        self.position = position

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type.name}, {self.value})"
        return f"Token({self.type.name})"