from token_types import TokenType
from ast_nodes import (
    Program, AssignmentStatement, IndexAssignStatement,
    PrintStatement, ReturnStatement, FunctionDef, ExpressionStatement,
    NumberLiteral, ListLiteral, Identifier, BinaryExpression,
    IfExpression, FunctionCall, IndexExpression, InputExpression,
)
 
 
class ParseError(Exception):
    pass
 
 
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0]
 
    # ── Helpers ────────────────────────────────────────────────────────────────
 
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
 
    def eat(self, token_type):
        if self.current_token.type == token_type:
            tok = self.current_token
            self.advance()
            return tok
        raise ParseError(
            f"Expected {token_type.name}, got {self.current_token.type.name} "
            f"(value={self.current_token.value!r})"
        )
 
    def skip_newlines(self):
        while self.current_token.type == TokenType.NEWLINE:
            self.advance()
 
    def require_statement_end(self):
        if self.current_token.type == TokenType.NEWLINE:
            self.skip_newlines()
        elif self.current_token.type == TokenType.RBRACE:
            pass  # closing brace ends block; don't consume here
        elif self.current_token.type != TokenType.EOF:
            raise ParseError(
                f"Expected newline or end of statement, "
                f"got {self.current_token.type.name} (value={self.current_token.value!r})"
            )
 
    # ── Expressions ────────────────────────────────────────────────────────────
 
    def parse_expression(self):
        """Top-level expression: handles if/then/else and comparison operators."""
        # if expression
        if self.current_token.type == TokenType.IF:
            return self.parse_if_expression()
        return self.parse_comparison()
 
    def parse_if_expression(self):
        self.eat(TokenType.IF)
        condition = self.parse_comparison()
        self.eat(TokenType.THEN)
        then_expr = self.parse_comparison()
        self.eat(TokenType.ELSE)
        else_expr = self.parse_comparison()
        return IfExpression(condition, then_expr, else_expr)
 
    def parse_comparison(self):
        node = self.parse_additive()
        while self.current_token.type in (TokenType.EQEQ, TokenType.GT, TokenType.LT):
            op = self.current_token.value
            self.advance()
            right = self.parse_additive()
            node = BinaryExpression(node, op, right)
        return node
 
    def parse_additive(self):
        node = self.parse_term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            node = BinaryExpression(node, op, right)
        return node
 
    def parse_term(self):
        node = self.parse_unary()
        while self.current_token.type in (TokenType.STAR, TokenType.SLASH):
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            node = BinaryExpression(node, op, right)
        return node
 
    def parse_unary(self):
        # Unary minus: -expr
        if self.current_token.type == TokenType.MINUS:
            self.advance()
            operand = self.parse_postfix()
            return BinaryExpression(NumberLiteral(0), '-', operand)
        return self.parse_postfix()
 
    def parse_postfix(self):
        """Handle indexing: expr[index]"""
        node = self.parse_primary()
        while self.current_token.type == TokenType.LBRACKET:
            self.advance()
            index = self.parse_expression()
            self.eat(TokenType.RBRACKET)
            node = IndexExpression(node, index)
        return node
 
    def parse_primary(self):
        tok = self.current_token
 
        # Integer literal
        if tok.type == TokenType.INTEGER:
            self.advance()
            return NumberLiteral(tok.value)
 
        # Float literal
        if tok.type == TokenType.FLOAT:
            self.advance()
            return NumberLiteral(tok.value)
 
        # List literal [a, b, c]
        if tok.type == TokenType.LBRACKET:
            return self.parse_list_literal()
 
        # Parenthesized expression
        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return expr
 
        # input()
        if tok.type == TokenType.INPUT:
            self.advance()
            self.eat(TokenType.LPAREN)
            self.eat(TokenType.RPAREN)
            return InputExpression()
 
        # Identifier or function call
        if tok.type == TokenType.IDENTIFIER:
            name = tok.value
            self.advance()
            if self.current_token.type == TokenType.LPAREN:
                return self.parse_function_call(name)
            return Identifier(name)
 
        raise ParseError(f"Unexpected token in expression: {tok}")
 
    def parse_list_literal(self):
        self.eat(TokenType.LBRACKET)
        elements = []
        self.skip_newlines()
        if self.current_token.type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
                if self.current_token.type == TokenType.RBRACKET:
                    break
                elements.append(self.parse_expression())
        self.eat(TokenType.RBRACKET)
        return ListLiteral(elements)
 
    def parse_function_call(self, name):
        self.eat(TokenType.LPAREN)
        args = []
        self.skip_newlines()
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()
                if self.current_token.type == TokenType.RPAREN:
                    break
                args.append(self.parse_expression())
        self.eat(TokenType.RPAREN)
        return FunctionCall(name, args)
 
    # ── Statements ─────────────────────────────────────────────────────────────
 
    def parse_statement(self):
        self.skip_newlines()
 
        # Function definition
        if self.current_token.type == TokenType.FUNC:
            return self.parse_function_def()
 
        # Return statement
        if self.current_token.type == TokenType.RETURN:
            self.advance()
            expr = self.parse_expression()
            self.require_statement_end()
            return ReturnStatement(expr)
 
        # Print statement
        if self.current_token.type == TokenType.PRINT:
            self.advance()
            self.eat(TokenType.LPAREN)
            expr = self.parse_expression()
            self.eat(TokenType.RPAREN)
            self.require_statement_end()
            return PrintStatement(expr)
 
        # Assignment or index-assignment or expression-statement
        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
 
            # Index assignment: name[idx] = expr
            if self.current_token.type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.eat(TokenType.RBRACKET)
                self.eat(TokenType.EQUAL)
                value = self.parse_expression()
                self.require_statement_end()
                return IndexAssignStatement(name, index, value)
 
            # Regular assignment: name = expr
            if self.current_token.type == TokenType.EQUAL:
                self.advance()
                value = self.parse_expression()
                self.require_statement_end()
                return AssignmentStatement(Identifier(name), value)
 
            # Function call as statement: name(args)
            if self.current_token.type == TokenType.LPAREN:
                call = self.parse_function_call(name)
                self.require_statement_end()
                return ExpressionStatement(call)
 
            raise ParseError(
                f"Expected '=', '[', or '(' after identifier '{name}', "
                f"got {self.current_token.type.name}"
            )
 
        raise ParseError(
            f"Unexpected token at start of statement: {self.current_token}"
        )
 
    def parse_block(self):
        """Parse { statements } block."""
        self.eat(TokenType.LBRACE)
        self.skip_newlines()
        statements = []
        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            stmt = self.parse_statement()
            statements.append(stmt)
            self.skip_newlines()
        self.eat(TokenType.RBRACE)
        return statements
 
    def parse_function_def(self):
        self.eat(TokenType.FUNC)
        name_tok = self.eat(TokenType.IDENTIFIER)
        name = name_tok.value
        self.eat(TokenType.LPAREN)
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params.append(self.eat(TokenType.IDENTIFIER).value)
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                params.append(self.eat(TokenType.IDENTIFIER).value)
        self.eat(TokenType.RPAREN)
        self.skip_newlines()
        body = self.parse_block()
        self.skip_newlines()
        return FunctionDef(name, params, body)
 
    def parse_program(self):
        statements = []
        self.skip_newlines()
        while self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
            self.skip_newlines()
        return Program(statements)
