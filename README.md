# SimpK Phase 1

SimpK (Simpler K) is a minimal, array-oriented programming language designed for mathematical computation and teaching vectorized thinking. Inspired by the K programming language, SimpK removes symbolic density and complex operators while keeping automatic element-wise arithmetic. The language focuses only on numbers and flat lists of numbers, making all operations expression-based and predictable.

This Phase 1 implementation only supports a minimal core parser. The goal of this phase is to tokenize source code, parse it, and print an Abstract Syntax Tree (AST). This project does not execute programs.

## Phase 1 Features Supported

This implementation supports:

- Integer literals
- Identifiers
- Arithmetic operators: `+`, `-`, `*`, `/`
- Assignment statements
- Print statements using `print(...)`
- Parenthesized expressions
- Newline-separated statements

## Example SimpK program:

x = 5

y = x + 2 * 3

print(y)

## Project Structure
	simpk/
	  src/
	    ast_nodes.py
	    lexer.py
	    parser.py
	    token_types.py
	    main.py
	  tests/
	    valid_1-10.simpk
	    invalid_1-5.simpk
	  README.md

## How to Run

**Run from the project root folder.**

### Lex a file
```bash
python src/main.py lex tests/valid_1.simpk
```

**This prints the token stream.**

### Parse a file
```bash
python src/main.py parse tests/valid_1.simpk
```

**This prints the AST in tree form.**

## Language Rules in This Version

**Statements are separated by newlines**

**Assignment syntax:**

x = 5

**Print syntax:**

print(x)

**Expressions follow normal arithmetic precedence:**

* and / before + and - 
  
**Parentheses override precedence**

## Grammar Used
program     -> statement* EOF

statement   -> assignment | print_stmt

assignment  -> IDENTIFIER '=' expression

print_stmt  -> 'print' '(' expression ')'

expression  -> term (('+' | '-') term)*

term        -> factor (('*' | '/') factor)*

factor      -> INTEGER | IDENTIFIER | '(' expression ')'

## Example Parse Output

**For this input:**

x = 5

y = x + 2 * 3

print(y)

**The parser prints a tree like:**

	Program
	  AssignmentStatement
	    Identifier(x)
	    NumberLiteral(5)
	  AssignmentStatement
	    Identifier(y)
	    BinaryExpression(+)
	      Identifier(x)
	      BinaryExpression(*)
	        NumberLiteral(2)
	        NumberLiteral(3)
	  PrintStatement
	    Identifier(y)
    
## Files
**token_types.py** defines token kinds and the Token class

**lexer.py** converts source code into tokens

**parser.py** builds the AST from tokens

**ast_nodes.py** defines AST node classes and formatting

**main.py** provides the command-line interface
