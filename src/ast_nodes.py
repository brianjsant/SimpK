class Program:
    def __init__(self, statements):
        self.statements = statements


class AssignmentStatement:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class PrintStatement:
    def __init__(self, expression):
        self.expression = expression


class BinaryExpression:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class NumberLiteral:
    def __init__(self, value):
        self.value = value


class Identifier:
    def __init__(self, name):
        self.name = name


def format_ast(node, indent=0):
    spaces = "  " * indent

    if isinstance(node, Program):
        lines = [f"{spaces}Program"]
        for stmt in node.statements:
            lines.append(format_ast(stmt, indent + 1))
        return "\n".join(lines)

    if isinstance(node, AssignmentStatement):
        lines = [f"{spaces}AssignmentStatement"]
        lines.append(format_ast(node.name, indent + 1))
        lines.append(format_ast(node.value, indent + 1))
        return "\n".join(lines)

    if isinstance(node, PrintStatement):
        lines = [f"{spaces}PrintStatement"]
        lines.append(format_ast(node.expression, indent + 1))
        return "\n".join(lines)

    if isinstance(node, BinaryExpression):
        lines = [f"{spaces}BinaryExpression({node.operator})"]
        lines.append(format_ast(node.left, indent + 1))
        lines.append(format_ast(node.right, indent + 1))
        return "\n".join(lines)

    if isinstance(node, NumberLiteral):
        return f"{spaces}NumberLiteral({node.value})"

    if isinstance(node, Identifier):
        return f"{spaces}Identifier({node.name})"

    return f"{spaces}UnknownNode"