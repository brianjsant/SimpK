# SimpK — Simpler K

SimpK is a minimal, array-oriented programming language designed for mathematical computation and teaching vectorized thinking.

Inspired by the K programming language, SimpK removes symbolic density while keeping automatic element-wise arithmetic.

## Quick Start

### GUI Recommended

```bash
python simpk_gui.py
```

Opens the SimpK IDE with syntax highlighting, output panel, AST viewer, token viewer, and built-in examples.

### Command Line

```bash
python src/main.py run <file.simpk>
```

Execute a program.

```bash
python src/main.py lex <file.simpk>
```

Show token stream.

```bash
python src/main.py parse <file.simpk>
```

Show AST.

## Language Reference

## Types

| Type | Example | Notes |
|---|---|---|
| Integer | `5`, `-3`, `42` | Whole numbers |
| Float | `3.14`, `-2.5` | Decimal numbers |
| List | `[1, 2, 3]` | Flat list of numbers only |

## Operators

| Operator | Meaning | Notes |
|---|---|---|
| `+` | Addition | Element-wise for lists |
| `-` | Subtraction | Element-wise for lists |
| `*` | Multiplication | Element-wise for lists |
| `/` | Division | Always returns float |
| `==` | Equality | Returns `1` true or `0` false |
| `>` | Greater than | Returns `1` or `0` |
| `<` | Less than | Returns `1` or `0` |
| `=` | Assignment | Assignment |

## Assignment

```simpk
x = 5
pi = 3.14
nums = [1, 2, 3]
nums[0] = 99  # index assignment
```

## Print

```simpk
print(x)
print(nums + 5)
```

## Conditionals

```simpk
result = if x > 3 then 10 else 20
```

## Functions

```simpk
func square(x) {
    return x * x
}

print(square(7))  # prints 49
```

## Recursion

```simpk
func fact(n) {
    return if n < 2 then 1 else n * fact(n - 1)
}

print(fact(6))  # prints 720
```

## List Operations

```simpk
nums = [1, 2, 3, 4, 5]

print(nums * 2)                    # [2, 4, 6, 8, 10]
print(nums + [10, 20, 30, 40, 50]) # [11, 22, 33, 44, 55]
print(nums[2])                     # 3
```

## Built-in Functions

| Function | Usage | Returns |
|---|---|---|
| `len` | `len(list)` | Length of list |
| `sum` | `sum(list)` | Sum of list |
| `abs` | `abs(x)` | Absolute value |
| `max` | `max(list)` | Maximum value |
| `min` | `min(list)` | Minimum value |

## Input

```simpk
x = input()  # reads a number from the user
print(x * 2)
```

## Comments

```simpk
# This is a comment

x = 5  # inline comment
```
