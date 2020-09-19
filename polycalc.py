"""A simple command-line calculator for polynomial arithmetic
(and derivatives, if you want).
"""
from polynomial import Polynomial, ParseError
import operator
import sys

WELCOME = """Welcome to polycalc.py!
Please enter 'quit', 'exit', Ctrl+C, or Ctrl+D at any time to exit.
"""

FAREWELL = """Thanks for trying me out!"""


def main():
    print(WELCOME)
    while True:
        try:
            poly1 = input_poly("Polynomial #1: ")
            operation = input_operation(
                "Operation (+, -, *, or 'D/d' for derivative): ")
            if operation == 'D':
                print(poly1.derivative())
                continue
            poly2 = input_poly("Polynomial #2: ")
            print(operation(poly1, poly2))
        except (EOFError, KeyboardInterrupt):
            sys.exit(-1)


def input_poly(prompt):
    while True:
        poly_s = input_or_quit(prompt)
        try:
            return Polynomial.from_string(poly_s)
        except ParseError as e:
            print(e)
            print("Please re-enter.")


def input_operation(prompt):
    OP_LOOKUP = {
        '+': operator.add,
        '*': operator.mul,
        '-': operator.sub
    }

    while True:
        op = input_or_quit(prompt)
        if op.upper() == 'D':
            return 'D'
        try:
            return OP_LOOKUP[op]
        except KeyError:
            print(f"Error: unrecognized operation {op!r}. Please re-enter.")


def input_or_quit(prompt):
    val = input(prompt)
    check = val.lower()
    if check in ('quit', 'exit'):
        print(FAREWELL)
        sys.exit(0)
    return val


if __name__ == "__main__":
    main()
