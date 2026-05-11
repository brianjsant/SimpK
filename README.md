SimpK — Simpler K
SimpK is a minimal, array-oriented programming language designed for mathematical computation and teaching vectorized thinking. Inspired by the K programming language, SimpK removes symbolic density while keeping automatic element-wise arithmetic.

Quick Start
GUI (Recommended)
python simpk_gui.py
Opens the SimpK IDE with syntax highlighting, output panel, AST viewer, token viewer, and built-in examples.
Command Line
python src/main.py run   <file.simpk>    # Execute a program
python src/main.py lex   <file.simpk>    # Show token stream
python src/main.py parse <file.simpk>    # Show AST

Language Reference
Types
TypeExampleNotesInteger5, -3, 42Whole numbersFloat3.14, -2.5Decimal numbersList[1, 2, 3]Flat list of numbers only
Operators
OperatorMeaningNotes+AdditionElement-wise for lists-SubtractionElement-wise for lists*MultiplicationElement-wise for lists/DivisionAlways returns float==EqualityReturns 1 (true) or 0 (false)>Greater thanReturns 1 or 0<Less thanReturns 1 or 0=Assignmentx = expr
Assignment
x = 5
pi = 3.14
nums = [1, 2, 3]
nums[0] = 99        # index assignment
Print
print(x)
print(nums + 5)
Conditionals
result = if x > 3 then 10 else 20
Functions
func square(x) {
    return x * x
}
print(square(7))    # prints 49
Recursion
func fact(n) {
    return if n < 2 then 1 else n * fact(n - 1)
}
print(fact(6))      # prints 720
List operations
nums = [1, 2, 3, 4, 5]
print(nums * 2)         # [2, 4, 6, 8, 10]
print(nums + [10, 20, 30, 40, 50])   # [11, 22, 33, 44, 55]
print(nums[2])          # 3
Built-in functions
FunctionUsageReturnslen(lst)length of listIntegersum(lst)sum of listNumberabs(x)absolute valueNumbermax(lst)maximum valueNumbermin(lst)minimum valueNumber
Input
x = input()     # reads a number from the user
print(x * 2)
Comments
# This is a comment
x = 5  # inline comment

Error Behavior
SimpK stops at the first error with a clear message:
Runtime Error: Undefined variable 'a'
Runtime Error: Division by zero
Runtime Error: Index 5 is out of bounds for list of length 3
Runtime Error: Lists must have the same length for '+' (got 2 and 3)
Parse Error: Expected RPAREN, got NEWLINE

Project Structure
simpk/
  simpk_gui.py          ← GUI IDE (run this!)
  src/
    token_types.py      ← Token definitions
    lexer.py            ← Tokenizer
    parser.py           ← Recursive descent parser
    ast_nodes.py        ← AST node classes + pretty printer
    evaluator.py        ← Tree-walk interpreter
    main.py             ← CLI entry point
  tests/
    valid_1-10.simpk    ← Valid programs
    invalid_1-5.simpk   ← Programs that should error
  README.md

Grammar
program     → statement* EOF
statement   → func_def | assignment | index_assign | print_stmt
              | return_stmt | expr_stmt
func_def    → 'func' IDENTIFIER '(' params ')' '{' statement* '}'
params      → (IDENTIFIER (',' IDENTIFIER)*)?
assignment  → IDENTIFIER '=' expression
index_assign→ IDENTIFIER '[' expression ']' '=' expression
print_stmt  → 'print' '(' expression ')'
return_stmt → 'return' expression
expr_stmt   → expression
expression  → if_expr | comparison
if_expr     → 'if' comparison 'then' comparison 'else' comparison
comparison  → additive (('==' | '>' | '<') additive)*
additive    → term (('+' | '-') term)*
term        → unary (('*' | '/') unary)*
unary       → '-' postfix | postfix
postfix     → primary ('[' expression ']')*
primary     → INTEGER | FLOAT | list_lit | '(' expression ')'
              | IDENTIFIER '(' args ')' | IDENTIFIER | 'input' '(' ')'
list_lit    → '[' (expression (',' expression)*)? ']'
args        → (expression (',' expression)*)?

What Makes SimpK Different
SimpK focuses only on numbers and lists and automatically performs element-wise operations — so [1,2,3] * 2 gives [2, 4, 6] without any loop. Unlike Python or Java, it has no objects, no strings, and no complex libraries. Loops are intentionally absent; array operations replace them entirely. All constructs return values, keeping the language expression-based and consistent. The small number of features makes the language easy to learn and the implementation fully understandable in one semester.
