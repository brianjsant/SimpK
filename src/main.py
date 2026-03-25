import sys
from lexer import Lexer
from parser import Parser
from ast_nodes import format_ast


def read_source_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def run_lex(filename):
    source = read_source_file(filename)
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    for token in tokens:
        print(token)


def run_parse(filename):
    source = read_source_file(filename)
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse_program()
    print(format_ast(ast))


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python main.py lex <filename>")
        print("  python main.py parse <filename>")
        return

    command = sys.argv[1]
    filename = sys.argv[2]

    try:
        if command == "lex":
            run_lex(filename)
        elif command == "parse":
            run_parse(filename)
        else:
            print(f"Unknown command: {command}")
            print("Use 'lex' or 'parse'.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()