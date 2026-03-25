from token_types import TokenType
from ast_nodes import (
    Program,
    AssignmentStatement,
    PrintStatement,
    BinaryExpression,
    NumberLiteral,
    Identifier,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.advance()
        else:
            raise Exception(
                f"Expected {token_type.name}, got {self.current_token.type.name}"
            )

    def skip_newlines(self):
        while self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def require_statement_end(self):
        if self.current_token.type == TokenType.NEWLINE:
            self.skip_newlines()
        elif self.current_token.type != TokenType.EOF:
            raise Exception(
                f"Expected NEWLINE or EOF after statement, got {self.current_token.type.name}"
            )

    def parse_factor(self):
        token = self.current_token

        if token.type == TokenType.INTEGER:
            self.advance()
            return NumberLiteral(token.value)

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value)

        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return expr

        raise Exception(f"Unexpected token in factor: {token}")

    def parse_term(self):
        node = self.parse_factor()

        while self.current_token.type in (TokenType.STAR, TokenType.SLASH):
            op = self.current_token.value
            self.advance()
            right = self.parse_factor()
            node = BinaryExpression(node, op, right)

        return node

    def parse_expression(self):
        node = self.parse_term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            node = BinaryExpression(node, op, right)

        return node

    def parse_statement(self):
        if self.current_token.type == TokenType.IDENTIFIER:
            name = Identifier(self.current_token.value)
            self.advance()
            self.eat(TokenType.EQUAL)
            value = self.parse_expression()
            self.require_statement_end()
            return AssignmentStatement(name, value)

        if self.current_token.type == TokenType.PRINT:
            self.advance()
            self.eat(TokenType.LPAREN)
            expr = self.parse_expression()
            self.eat(TokenType.RPAREN)
            self.require_statement_end()
            return PrintStatement(expr)

        raise Exception(
            f"Unexpected token at start of statement: {self.current_token}"
        )

    def parse_program(self):
        statements = []

        self.skip_newlines()

        while self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)

        return Program(statements)