"""
SimpK Evaluator
Walks the AST and executes each node, returning values.
"""
 
from ast_nodes import (
    Program, AssignmentStatement, IndexAssignStatement,
    PrintStatement, ReturnStatement, FunctionDef, ExpressionStatement,
    NumberLiteral, ListLiteral, Identifier, BinaryExpression,
    IfExpression, FunctionCall, IndexExpression, InputExpression,
)
 
 
# ── Runtime Errors ─────────────────────────────────────────────────────────────
 
class SimpKError(Exception):
    pass
 
 
class ReturnSignal(Exception):
    """Used to propagate return values out of function bodies."""
    def __init__(self, value):
        self.value = value
 
 
# ── Environment (variable storage) ────────────────────────────────────────────
 
class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent   # for function-local scopes
 
    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise SimpKError(f"Undefined variable '{name}'")
 
    def set(self, name, value):
        self.vars[name] = value
 
    def set_index(self, name, index, value):
        lst = self.get(name)
        if not isinstance(lst, list):
            raise SimpKError(f"Variable '{name}' is not a list")
        if not isinstance(index, (int, float)):
            raise SimpKError("List index must be a number")
        i = int(index)
        if i < 0 or i >= len(lst):
            raise SimpKError(
                f"Index {i} is out of bounds for list of length {len(lst)}"
            )
        lst[i] = value
 
 
# ── Evaluator ─────────────────────────────────────────────────────────────────
 
class Evaluator:
    def __init__(self, output_callback=None, input_callback=None):
        """
        output_callback: called with a string whenever print() is executed.
                         Defaults to built-in print.
        input_callback:  called with no args to read a line from the user.
                         Defaults to built-in input().
        """
        self.global_env = Environment()
        # Built-in functions stored in global env as special markers
        self._builtins = {
            'len': self._builtin_len,
            'sum': self._builtin_sum,
            'abs': self._builtin_abs,
            'max': self._builtin_max,
            'min': self._builtin_min,
        }
        self.output_callback = output_callback or (lambda s: print(s))
        self.input_callback  = input_callback  or (lambda: input())
 
    # ── Built-ins ──────────────────────────────────────────────────────────────
 
    def _builtin_len(self, args):
        if len(args) != 1:
            raise SimpKError("len() takes exactly 1 argument")
        v = args[0]
        if not isinstance(v, list):
            raise SimpKError("len() requires a list argument")
        return float(len(v))
 
    def _builtin_sum(self, args):
        if len(args) != 1:
            raise SimpKError("sum() takes exactly 1 argument")
        v = args[0]
        if not isinstance(v, list):
            raise SimpKError("sum() requires a list argument")
        return sum(v)
 
    def _builtin_abs(self, args):
        if len(args) != 1:
            raise SimpKError("abs() takes exactly 1 argument")
        v = args[0]
        if not isinstance(v, (int, float)):
            raise SimpKError("abs() requires a number argument")
        return abs(v)
 
    def _builtin_max(self, args):
        if len(args) == 1 and isinstance(args[0], list):
            return max(args[0])
        if len(args) >= 2 and all(isinstance(a, (int, float)) for a in args):
            return max(args)
        raise SimpKError("max() requires a list or two numbers")
 
    def _builtin_min(self, args):
        if len(args) == 1 and isinstance(args[0], list):
            return min(args[0])
        if len(args) >= 2 and all(isinstance(a, (int, float)) for a in args):
            return min(args)
        raise SimpKError("min() requires a list or two numbers")
 
    # ── Value formatting ───────────────────────────────────────────────────────
 
    def _format_value(self, val):
        if isinstance(val, list):
            parts = [self._format_value(v) for v in val]
            return '[' + ', '.join(parts) + ']'
        if isinstance(val, float) and val == int(val):
            return str(int(val))
        return str(val)
 
    # ── Main eval dispatch ─────────────────────────────────────────────────────
 
    def eval(self, node, env=None):
        if env is None:
            env = self.global_env
        return self._eval_node(node, env)
 
    def _eval_node(self, node, env):
 
        # ── Program ────────────────────────────────────────────────────────────
        if isinstance(node, Program):
            result = None
            for stmt in node.statements:
                result = self._eval_node(stmt, env)
            return result
 
        # ── Function definition ────────────────────────────────────────────────
        if isinstance(node, FunctionDef):
            # Store the function definition in the environment
            env.set(node.name, ('__func__', node, env))
            return None
 
        # ── Assignment ─────────────────────────────────────────────────────────
        if isinstance(node, AssignmentStatement):
            value = self._eval_node(node.value, env)
            env.set(node.name.name, value)
            return value
 
        # ── Index Assignment ───────────────────────────────────────────────────
        if isinstance(node, IndexAssignStatement):
            index = self._eval_node(node.index, env)
            value = self._eval_node(node.value, env)
            env.set_index(node.name, index, value)
            return value
 
        # ── Print ──────────────────────────────────────────────────────────────
        if isinstance(node, PrintStatement):
            val = self._eval_node(node.expression, env)
            self.output_callback(self._format_value(val))
            return None
 
        # ── Return ─────────────────────────────────────────────────────────────
        if isinstance(node, ReturnStatement):
            val = self._eval_node(node.expression, env)
            raise ReturnSignal(val)
 
        # ── Expression statement ───────────────────────────────────────────────
        if isinstance(node, ExpressionStatement):
            return self._eval_node(node.expression, env)
 
        # ── Number literal ─────────────────────────────────────────────────────
        if isinstance(node, NumberLiteral):
            return node.value
 
        # ── List literal ───────────────────────────────────────────────────────
        if isinstance(node, ListLiteral):
            return [self._eval_node(el, env) for el in node.elements]
 
        # ── Identifier ─────────────────────────────────────────────────────────
        if isinstance(node, Identifier):
            return env.get(node.name)
 
        # ── Binary expression ──────────────────────────────────────────────────
        if isinstance(node, BinaryExpression):
            return self._eval_binary(node, env)
 
        # ── If expression ──────────────────────────────────────────────────────
        if isinstance(node, IfExpression):
            cond = self._eval_node(node.condition, env)
            if isinstance(cond, list):
                raise SimpKError("Lists cannot be used directly as conditions")
            if cond != 0:
                return self._eval_node(node.then_expr, env)
            else:
                return self._eval_node(node.else_expr, env)
 
        # ── Function call ──────────────────────────────────────────────────────
        if isinstance(node, FunctionCall):
            return self._eval_call(node, env)
 
        # ── Index expression ───────────────────────────────────────────────────
        if isinstance(node, IndexExpression):
            target = self._eval_node(node.target, env)
            index  = self._eval_node(node.index, env)
            if not isinstance(target, list):
                raise SimpKError("Indexing is only allowed on lists")
            if not isinstance(index, (int, float)):
                raise SimpKError("List index must be a number")
            i = int(index)
            if i < 0 or i >= len(target):
                raise SimpKError(
                    f"Index {i} is out of bounds for list of length {len(target)}"
                )
            return target[i]
 
        # ── Input expression ───────────────────────────────────────────────────
        if isinstance(node, InputExpression):
            raw = self.input_callback()
            raw = raw.strip()
            try:
                if '.' in raw:
                    return float(raw)
                return int(raw)
            except ValueError:
                raise SimpKError(
                    f"input() received a non-numeric value: '{raw}'. "
                    "SimpK only supports numbers."
                )
 
        raise SimpKError(f"Unknown AST node type: {type(node).__name__}")
 
    # ── Binary arithmetic & comparison ─────────────────────────────────────────
 
    def _eval_binary(self, node, env):
        left  = self._eval_node(node.left,  env)
        right = self._eval_node(node.right, env)
        op    = node.operator
 
        # Both numbers
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return self._num_op(left, right, op)
 
        # List op number  →  element-wise
        if isinstance(left, list) and isinstance(right, (int, float)):
            return [self._num_op(el, right, op) for el in left]
 
        # Number op list  →  element-wise
        if isinstance(left, (int, float)) and isinstance(right, list):
            return [self._num_op(left, el, op) for el in right]
 
        # List op list  →  element-wise (must be same length)
        if isinstance(left, list) and isinstance(right, list):
            if op == '==':
                return 1 if (
                    len(left) == len(right) and
                    all(self._num_op(a, b, '==') for a, b in zip(left, right))
                ) else 0
            if len(left) != len(right):
                raise SimpKError(
                    f"Lists must have the same length for '{op}' "
                    f"(got {len(left)} and {len(right)})"
                )
            return [self._num_op(a, b, op) for a, b in zip(left, right)]
 
        raise SimpKError(
            f"Invalid operation '{op}' between "
            f"{self._type_name(left)} and {self._type_name(right)}"
        )
 
    def _num_op(self, a, b, op):
        if op == '+':  return a + b
        if op == '-':  return a - b
        if op == '*':  return a * b
        if op == '/':
            if b == 0:
                raise SimpKError("Division by zero")
            return a / b
        if op == '==': return 1 if a == b else 0
        if op == '>':  return 1 if a > b  else 0
        if op == '<':  return 1 if a < b  else 0
        raise SimpKError(f"Unknown operator '{op}'")
 
    def _type_name(self, val):
        if isinstance(val, list): return 'List'
        if isinstance(val, float): return 'Float'
        if isinstance(val, int): return 'Integer'
        return type(val).__name__
 
    # ── Function call ──────────────────────────────────────────────────────────
 
    def _eval_call(self, node, env):
        name = node.name
 
        # Built-in functions
        if name in self._builtins:
            args = [self._eval_node(a, env) for a in node.args]
            return self._builtins[name](args)
 
        # User-defined functions
        func_val = env.get(name)
        if not (isinstance(func_val, tuple) and func_val[0] == '__func__'):
            raise SimpKError(f"'{name}' is not a function")
 
        _, func_def, closure_env = func_val
 
        if len(node.args) != len(func_def.params):
            raise SimpKError(
                f"Function '{name}' expects {len(func_def.params)} argument(s), "
                f"got {len(node.args)}"
            )
 
        # Create a new environment for the function call (child of closure)
        local_env = Environment(parent=closure_env)
        for param, arg_node in zip(func_def.params, node.args):
            local_env.set(param, self._eval_node(arg_node, env))
 
        try:
            for stmt in func_def.body:
                self._eval_node(stmt, local_env)
        except ReturnSignal as r:
            return r.value
 
        return 0  # functions without return default to 0
