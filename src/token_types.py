from enum import Enum, auto
 
 
class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    # Identifiers & Keywords
    IDENTIFIER = auto()
    PRINT = auto()
    FUNC = auto()
    RETURN = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    INPUT = auto()
    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    # Comparison operators
    EQEQ = auto()    # ==
    GT = auto()      # >
    LT = auto()      # <
    # Assignment
    EQUAL = auto()   # =
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    # Structure
    NEWLINE = auto()
    EOF = auto()
 
 
class Token:
    def __init__(self, token_type, value=None, position=None):
        self.type = token_type
        self.value = value
        self.position = position
 
    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type.name}, {self.value!r})"
        return f"Token({self.type.name})"
