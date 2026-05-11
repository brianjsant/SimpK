class Program:
    def __init__(self, statements):
        self.statements = statements
 
 
# Statements 
class AssignmentStatement:
    """x = expr"""
    def __init__(self, name, value):
        self.name = name          # Identifier node
        self.value = value        # expression node
 
class IndexAssignStatement:
    """nums[0] = expr"""
    def __init__(self, name, index, value):
        self.name = name
        self.index = index
        self.value = value
 
class PrintStatement:
    """print(expr)"""
    def __init__(self, expression):
        self.expression = expression
 
class ReturnStatement:
    """return expr"""
    def __init__(self, expression):
        self.expression = expression
 
class FunctionDef:
    """func name(params) { body }"""
    def __init__(self, name, params, body):
        self.name = name          # string
        self.params = params      # list of strings
        self.body = body          # list of statement nodes
 
class ExpressionStatement:
    """A bare expression used as a statement (e.g. a function call for side effects)"""
    def __init__(self, expression):
        self.expression = expression
 
 
# Expressions
 
class NumberLiteral:
    def __init__(self, value):
        self.value = value        # int or float
 
class ListLiteral:
    def __init__(self, elements):
        self.elements = elements  # list of expression nodes
 
class Identifier:
    def __init__(self, name):
        self.name = name
 
class BinaryExpression:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator  # string: '+', '-', '*', '/', '==', '>', '<'
        self.right = right
 
class IfExpression:
    """if condition then expr1 else expr2"""
    def __init__(self, condition, then_expr, else_expr):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr
 
class FunctionCall:
    """name(args)"""
    def __init__(self, name, args):
        self.name = name          # string
        self.args = args          # list of expression nodes
 
class IndexExpression:
    """expr[index]"""
    def __init__(self, target, index):
        self.target = target
        self.index = index
 
class InputExpression:
    """input()"""
    def __init__(self):
        pass
 
 
# Pretty Printer
 
def format_ast(node, indent=0):
    spaces = "  " * indent
 
    if isinstance(node, Program):
        lines = [f"{spaces}Program"]
        for stmt in node.statements:
            lines.append(format_ast(stmt, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, FunctionDef):
        params = ", ".join(node.params)
        lines = [f"{spaces}FunctionDef({node.name}, [{params}])"]
        for stmt in node.body:
            lines.append(format_ast(stmt, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, AssignmentStatement):
        lines = [f"{spaces}AssignmentStatement"]
        lines.append(format_ast(node.name, indent + 1))
        lines.append(format_ast(node.value, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, IndexAssignStatement):
        lines = [f"{spaces}IndexAssignStatement({node.name})"]
        lines.append(f"{spaces}  index: " + format_ast(node.index, 0).strip())
        lines.append(f"{spaces}  value: " + format_ast(node.value, 0).strip())
        return "\n".join(lines)
 
    if isinstance(node, PrintStatement):
        lines = [f"{spaces}PrintStatement"]
        lines.append(format_ast(node.expression, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, ReturnStatement):
        lines = [f"{spaces}ReturnStatement"]
        lines.append(format_ast(node.expression, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, ExpressionStatement):
        lines = [f"{spaces}ExpressionStatement"]
        lines.append(format_ast(node.expression, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, BinaryExpression):
        lines = [f"{spaces}BinaryExpression({node.operator})"]
        lines.append(format_ast(node.left, indent + 1))
        lines.append(format_ast(node.right, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, IfExpression):
        lines = [f"{spaces}IfExpression"]
        lines.append(f"{spaces}  condition:")
        lines.append(format_ast(node.condition, indent + 2))
        lines.append(f"{spaces}  then:")
        lines.append(format_ast(node.then_expr, indent + 2))
        lines.append(f"{spaces}  else:")
        lines.append(format_ast(node.else_expr, indent + 2))
        return "\n".join(lines)
 
    if isinstance(node, FunctionCall):
        lines = [f"{spaces}FunctionCall({node.name})"]
        for arg in node.args:
            lines.append(format_ast(arg, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, IndexExpression):
        lines = [f"{spaces}IndexExpression"]
        lines.append(format_ast(node.target, indent + 1))
        lines.append(format_ast(node.index, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, ListLiteral):
        lines = [f"{spaces}ListLiteral"]
        for el in node.elements:
            lines.append(format_ast(el, indent + 1))
        return "\n".join(lines)
 
    if isinstance(node, NumberLiteral):
        return f"{spaces}NumberLiteral({node.value})"
 
    if isinstance(node, Identifier):
        return f"{spaces}Identifier({node.name})"
 
    if isinstance(node, InputExpression):
        return f"{spaces}InputExpression"
 
    return f"{spaces}UnknownNode({type(node).__name__})"
 
