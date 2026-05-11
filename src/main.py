import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from ast_nodes import format_ast
from evaluator import Evaluator, SimpKError
 
 
def read_source_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()
 
 
def run_lex(filename):
    source = read_source_file(filename)
    lexer = Lexer(source)
    try:
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)
    except LexerError as e:
        print(f"Lex Error: {e}")
 
 
def run_parse(filename):
    source = read_source_file(filename)
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse_program()
        print(format_ast(ast))
    except (LexerError, ParseError) as e:
        print(f"Parse Error: {e}")
 
 
def run_eval(filename):
    source = read_source_file(filename)
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse_program()
        evaluator = Evaluator()
        evaluator.eval(ast)
    except (LexerError, ParseError) as e:
        print(f"Parse Error: {e}")
    except SimpKError as e:
        print(f"Runtime Error: {e}")
 
 
def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python main.py lex   <filename>")
        print("  python main.py parse <filename>")
        print("  python main.py run   <filename>")
        return
 
    command  = sys.argv[1]
    filename = sys.argv[2]
 
    if command == 'lex':
        run_lex(filename)
    elif command == 'parse':
        run_parse(filename)
    elif command == 'run':
        run_eval(filename)
    else:
        print(f"Unknown command: '{command}'")
        print("Use 'lex', 'parse', or 'run'.")
 
 
if __name__ == '__main__':
    main()
