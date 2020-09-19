from __future__ import annotations
from enum import Enum, auto
from typing import List


class Polynomial:

    coeffs: List[int]
    disp_ch: str = 'x'

    def __init__(self, coeffs, *, disp_ch=None):
        self.coeffs = coeffs
        if disp_ch:
            self.disp_ch = disp_ch

    def __str__(self) -> str:
        """
        Return a string representing the polynomial. Use self.disp_ch ('x' by default) as the base.
        Since `coeffs` stores coefficients in order of ascending powers, this method returns a string
        representing the polynomial in ascending power order. So:
        >>> p = Polynomial([7, 14, 23])
        >>> str(p)
        '7 + 14x + 23x^2'
        >>> q = Polynomial([14, 12, 9, 11], disp_ch='z')
        >>> str(q)
        '14 + 12z + 9z^2 + 11z^3'
        """
        retlist = []

        for (pow, coeff) in enumerate(self.coeffs):
            if coeff == 0:
                continue
            if coeff == 1:
                coeff_part = ""
            else:
                coeff_part = str(coeff)
            if pow == 0:
                pow_part = ""
            elif pow == 1:
                pow_part = self.disp_ch
            else:
                pow_part = f"{self.disp_ch}^{pow}"

            retlist.append(f'{coeff_part}{pow_part}')

        ret = " + ".join(retlist).replace("+ -", "- ")
        return ret

    def __repr__(self) -> str:
        return f'{type(self).__name__}({str(self)})'

    def __add__(self, other: Polynomial) -> Polynomial:
        """
        Return the result of polynomial addition with `other`.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> q = Polynomial([9, 12, 3])
        >>> p + q
        Polynomial(12 + 16x + 8x^2 + 9x^3)
        """
        new_coeffs = [0] * max(len(self.coeffs), len(other.coeffs))

        for (pow, coeff) in enumerate(self.coeffs):
            new_coeffs[pow] += coeff

        for (pow, coeff) in enumerate(other.coeffs):
            new_coeffs[pow] += coeff

        return Polynomial(new_coeffs)

    def __sub__(self, other: Polynomial) -> Polynomial:
        """
        Return the result of polynomial subtraction of `other` from this polynomial.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> q = Polynomial([9, 12, 3])
        >>> p - q
        Polynomial(-6 - 8x + 2x^2 + 9x^3)
        """
        new_coeffs = [0] * max(len(self.coeffs), len(other.coeffs))

        for (pow, coeff) in enumerate(self.coeffs):
            new_coeffs[pow] += coeff

        for (pow, coeff) in enumerate(other.coeffs):
            new_coeffs[pow] -= coeff

        return Polynomial(new_coeffs)

    def __mul__(self, other: Polynomial) -> Polynomial:
        """
        Return the result of polynomial multiplication with `other`.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> q = Polynomial([9, 12, 3])
        >>> p * q
        Polynomial(27 + 72x + 102x^2 + 153x^3 + 123x^4 + 27x^5)
        """
        new_coeffs = [0] * (len(self.coeffs) + len(other.coeffs) - 1)

        for (i, i_co) in enumerate(self.coeffs):
            for (j, j_co) in enumerate(other.coeffs):
                new_coeffs[i + j] += i_co * j_co

        return Polynomial(new_coeffs)

    def derivative(self) -> Polynomial:
        """
        Return the derivative of this polynomial.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> p.derivative()
        Polynomial(4 + 10x + 27x^2)
        """
        if len(self.coeffs) in (0, 1):
            return Polynomial([0])
        else:
            new_coeffs = []
            for (pow, coeff) in enumerate(self.coeffs):
                new_coeffs.append(pow * coeff)
            return Polynomial(new_coeffs[1:])

    @classmethod
    def from_string(cls, s: str) -> Polynomial:
        """Return a polynomial given a string representation.

        >>> Polynomial.from_string('3x^3 - 4x + 5')
        Polynomial(3x^3 - 4x + 5)
        """
        parser = _Parser(s)
        ast = parser.parse()

        # Now we get to have fun turning this ast list into something
        # we can pass to the Polynomial constructor.
        normalized_nodes = []
        last_op_minus = False
        for node_or_op in ast:
            if isinstance(node_or_op, _Node):
                if last_op_minus:
                    node_or_op.coefficient *= -1
                normalized_nodes.append(node_or_op)
            else:
                last_op_minus = True if node_or_op == '-' else False

        normalized_nodes = list(
            sorted(normalized_nodes, key=lambda node: node.exponent))

        # Error checking: We want to make sure there are not two nodes with
        # the same exponent (do your arithmetic yourself, user!)
        # and we also want to make sure that all nodes have the same variable
        # name, since neither of these things are checked by the parser.
        seen_exponents = set()
        for node in normalized_nodes:
            if node.exponent not in seen_exponents:
                seen_exponents.add(node.exponent)
            else:
                raise ParseError(
                    f"Only one term for each exponent is allowed: this string has at "
                    f" least two terms raised to the power of {node.exponent}")

        var_name = None
        for node in normalized_nodes:
            if var_name is None:
                var_name = node.var_name
            elif node.var_name != var_name:
                raise ParseError(
                    f"Only one variable is allowed in string. "
                    f"This has at least two: {var_name} and {node.var_name}")

        # edge case where the nodes were all constant terms
        if var_name is None:
            var_name = 'x'

        # Now we have to fill in the gaps
        largest_exponent = max(
            normalized_nodes, key=lambda node: node.exponent).exponent
        coeffs = [0] * (largest_exponent+1)

        # Slow double loop :(
        for exp in range(largest_exponent+1):
            for node in normalized_nodes:
                if node.exponent == exp:
                    coeffs[exp] = node.coefficient

        return cls(coeffs, disp_ch=var_name)


# Second part of the file: implement a parser for polynomial strings.
# For reference:


class _Token:
    def __init__(self, type_: _TokenType, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'({self.type.name}, {repr(self.value)})'

    __str__ = __repr__


class _TokenType(Enum):
    INTEGER = auto()
    OP_PLUS = auto()
    OP_MINUS = auto()
    OP_TIMES = auto()
    OP_EXPONENT = auto()
    VARIABLE = auto()
    EOF = auto()


class ParseError(Exception):
    pass


class _Lexer:
    """The lexer is responsible for translating a string into a stream of tokens
    for consumption by the parser.
    """
    current_char: str  # of length 1

    def __init__(self, text):
        self.text = text
        self.pos = 0

    def get_next_token(self):
        if self.pos > len(self.text) - 1:
            return _Token(_TokenType.EOF)
        self.current_char = self.text[self.pos]

        if self.current_char.isspace():
            self.skip_whitespace()

        if self.current_char.isdigit():
            return self.get_integer()
        elif self.current_char.isalpha():
            return self.get_variable()
        elif self.current_char in ('+', '-', '*', '^'):
            return self.get_operator()
        else:
            raise ParseError(
                f"Error at char #{self.pos}: unexpected character '{self.current_char}'")

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.current_char.isspace():
            self.pos += 1
            self.current_char = self.text[self.pos] if self.pos < len(
                self.text) else None

    def get_integer(self):
        buffer = []
        while self.pos < len(self.text) and self.current_char.isdigit():
            buffer.append(self.current_char)
            self.pos += 1
            self.current_char = self.text[self.pos] if self.pos < len(
                self.text) else None
        return _Token(_TokenType.INTEGER, ''.join(buffer))

    def get_variable(self):
        buffer = []
        while self.pos < len(self.text) and self.current_char.isalpha():
            buffer.append(self.current_char)
            self.pos += 1
            self.current_char = self.text[self.pos] if self.pos < len(
                self.text) else None
        return _Token(_TokenType.VARIABLE, ''.join(buffer))

    def get_operator(self):
        op_char = self.current_char
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]

        if op_char == '+':
            return _Token(_TokenType.OP_PLUS, '+')
        elif op_char == '-':
            return _Token(_TokenType.OP_MINUS, '-')
        elif op_char == '*':
            return _Token(_TokenType.OP_TIMES, '*')
        elif op_char == '^':
            return _Token(_TokenType.OP_EXPONENT, '^')


class _Node:
    """The `_Node` class is a helper class for the `_Parser`. Every `_Node`
    represents a term of a polynomial.
    """

    def __init__(self, coefficient, var_name, exponent):
        self.coefficient = coefficient
        self.var_name = var_name
        self.exponent = exponent

    def __repr__(self):
        return f'Node({self.coefficient} * {self.var_name} ^ {self.exponent})'


class _Parser:
    """The `_Parser` class is responsible for taking a stream of tokens
    (provided by its `lexer` member) and turning them into a list of
    nodes each representing one term of a polynomial.

    The grammar which this parser accepts is not recursive; only a subset of
    arithmetic expressions are accepted, for simplicity's sake. (We cannot add,
    subtract, multiply, or exponentiate numbers with numbers, only with variables.)

    There are some hackish things to accomodate the fact that there are implicit
    exponents and coefficients allowed in the grammar. I am making these explicit in the
    parser. Of course, one could normalize it elsewhere, but this seems to work decently
    well, and it's part of the grammar, even if one couldn't write a formal rule for it.

    Also note that once the parse() method has been called, the parser is in an unstable
    state. One must explicitly call reset() before calling the parse() method again.
    """

    def __init__(self, s: str):
        self.lexer = _Lexer(s)
        self.advance()

    def reset(self):
        """Useful for debugging"""
        self.lexer = _Lexer(self.lexer.text)
        self.advance()

    def advance(self):
        self.current_token = self.lexer.get_next_token()

    def eat(self, type_: _TokenType, optional: bool = False):
        """Skip a token, checking that it is of the proper type.
        The `optional` flag is provided so that we can allow for the optional
        presence of the multiplication operator at certain points in the grammar.
        """
        if self.current_token.type != type_:
            if optional:
                return
            raise ParseError(
                f"Expected token of type {type_}, found {self.current_token.type} (beginning at char #{self.lexer.pos})")
        self.advance()

    def parse(self) -> List[_Node]:
        """Main parsing method."""
        result = []
        while self.current_token.type != _TokenType.EOF:
            node = self.parse_node()
            op = self.parse_addop()
            result.append(node)
            if op is not None:
                result.append(op)
        return result

    def parse_node(self) -> _Node:
        assert self.current_token.type in (
            _TokenType.INTEGER, _TokenType.VARIABLE)

        coefficient: int
        var_name: str
        exponent: int

        if self.current_token.type == _TokenType.INTEGER:
            coefficient = int(self.current_token.value)
        elif self.current_token.type == _TokenType.VARIABLE:
            coefficient = 1
            var_name = self.current_token.value

        self.advance()
        self.eat(_TokenType.OP_TIMES, optional=True)

        token = self.current_token
        if token.type == _TokenType.VARIABLE:
            self.advance()
            var_name = token.value
        else:
            if 'var_name' not in locals():  # hackish, but effective
                var_name = None

        token = self.current_token
        if token.type == _TokenType.OP_EXPONENT:
            self.advance()
            exp_token = self.current_token
            self.eat(_TokenType.INTEGER)
            exponent = int(exp_token.value)
        else:
            # We know, if var_name has been set to something other than `None`, and we
            # have no explicit exponent, that this node has an implicit exponent of 1.
            # This seems somewhat inelegant, but var_name's being set is exactly
            # equivalent to the informmation we need to make the choice about exponent
            exponent = 0 if var_name is None else 1

        return _Node(coefficient, var_name, exponent)

    def parse_addop(self):
        token_type = self.current_token.type
        if token_type == _TokenType.OP_PLUS:
            ret = '+'
        elif token_type == _TokenType.OP_MINUS:
            ret = '-'
        elif token_type == _TokenType.EOF:
            ret = None
        self.advance()
        return ret


if __name__ == '__main__':
    import doctest
    doctest.testmod()
