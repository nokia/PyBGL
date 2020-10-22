#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl
#
# Adapted from: https://gist.github.com/nitely/497540eb017ed8a75aecb6a4e609c9a2
# Explanations: https://medium.com/@gregorycernera/converting-regular-expressions-to-postfix-notation-with-the-shunting-yard-algorithm-63d22ea1cf88

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

import re
from collections import deque, namedtuple

(RIGHT, LEFT) = range(2)

# cardinality is not required by shunting_yard_postfix algorithm, but
# might be useful to process the Reverse Polonese Notation it returns.
Op = namedtuple(
    "Op", ["cardinality", "precedence", "associativity"]
)

#------------------------------------------------------------------------
# Tokenization (token = atomic sequence of characters)
#------------------------------------------------------------------------

# See https://docs.python.org/3/library/re.html#writing-a-tokenizer
def re_escape(s :chr) -> str:
    return "".join(
        a if a not in "|[]{}.+*?()^$\\"
        else "\\" + a
        for a in s
    )

def tokenize(
    expression        :str,
    re_operators      :set,
    operator_to_token :callable = None,
    operand_to_token  :callable = None
) -> iter:
    """
    Tokenize an input string.
    Args:
        expression: `str` containing the input expression to tokenize.
        re_operators: `set(str)` storing the regular expression to recognize operators.
            Each string must be compatible with `re.compile`.
            Examples: `RE_OPERATORS_ALG`, `RE_OPERATORS_RE`.
        operator_to_token: `None` or Callback used to convert an operator to a dedicated type.
            Can be used to determine whether we process the unary or binary version
            of an operator (see e.g. `alg_operator_to_token`)
        operand_to_token; `None` or Callback used to process an operand (strip, cast, etc.)
    Returns:
        An iterator over the tokenized expression.
    """
    if not operator_to_token:
        operator_to_token = lambda prev_token, prev_is_operator, operator: operator
    if not operand_to_token:
        operand_to_token = lambda operand: operand

    pattern = "|".join(re_operator for re_operator in set(re_operators))
    tokenizer = re.compile(pattern)
    start = 0
    (prev_token, prev_is_operator) = (None, True)
    for match in tokenizer.finditer(expression):
        operand = expression[start:match.start()]
        if operand:
            yield operand_to_token(operand)
            (prev_token, prev_is_operator) = (operand, False)
        operator = match.group(0)
        if operator:
            yield operator_to_token(prev_token, prev_is_operator, operator)
            (prev_token, prev_is_operator) = (operator, True)
        start = match.end()
    operand = expression[start:]
    if operand:
        yield operand_to_token(operand)

#------------------------------------------------------------------------
# Algebra tokenization
#------------------------------------------------------------------------

MAP_OPERATORS_ALG = {
    # Unary operators
    "u+" : Op(cardinality=1, precedence=3, associativity=RIGHT),
    "u-" : Op(cardinality=1, precedence=3, associativity=RIGHT),
    # Binary operators
    "^" : Op(cardinality=2, precedence=4, associativity=RIGHT),
    "*" : Op(cardinality=2, precedence=3, associativity=LEFT),
    "/" : Op(cardinality=2, precedence=3, associativity=LEFT),
    "+" : Op(cardinality=2, precedence=2, associativity=LEFT),
    "-" : Op(cardinality=2, precedence=2, associativity=LEFT),
}

RE_OPERATORS_ALG = [
    re_escape(op)
    for op in list(MAP_OPERATORS_ALG.keys()) + list("()")
]

def alg_operator_to_token(prev_token :str, prev_is_operator :bool, operator :str) -> str:
    if prev_is_operator and prev_token != ")" and operator != "(":
        if   operator == "+": return "u+"
        elif operator == "-": return "u-"
        else: raise RuntimeError(f"Invalid unary operator '{operator}'")
    else:
        return operator

def alg_operand_to_token(operand):
    return float(operand.strip())

def tokenizer_alg(expression :str) -> iter:
    return tokenize(
        expression,
        RE_OPERATORS_ALG,
        operator_to_token = alg_operator_to_token,
        operand_to_token = alg_operand_to_token
    )

#------------------------------------------------------------------------
# Regexp tokenization
#------------------------------------------------------------------------

MAP_OPERATORS_RE = {
    # Unary operators
    "*" : Op(cardinality=1, precedence=4, associativity=LEFT),
    "+" : Op(cardinality=1, precedence=4, associativity=LEFT),
    "?" : Op(cardinality=1, precedence=3, associativity=LEFT),
    # Binary operators
    "." : Op(cardinality=2, precedence=2, associativity=LEFT),
    "|" : Op(cardinality=2, precedence=1, associativity=LEFT),
}

RE_OPERATORS_RE = [
    re_escape(op)
    for op in list(MAP_OPERATORS_RE.keys()) + ["(", ")"]
] + [
    # Extra repetition operators
    "\\{\\s*\\d+(\\s*,)?(\\s*\\d+)?\\s*\\}",
    # Character classes
    "\\[.*\\]",
    # Escape sequences (not exhaustive)
    "(\\\\(d|s|w))",
]

def tokenizer_re(expression :str) -> iter:
     return tokenize(expression, RE_OPERATORS_RE)

def catify(
    expression :str,
    is_binary  :callable = None,
    is_unary   :callable = None,
    is_opening :callable = None,
    is_closing :callable = None,
    cat        :str      = "."
) -> iter:
    """
    Add concatenation operator in an input regular expression.
    Args:
        expression: A `str` containing a regular expression.
        is_binary: `Callback(chr) -> bool` returning `True`
            iff the character is a binary operator.
        is_unary: `Callback(chr) -> bool` returning `True`
            iff the character is a unary operator.
        is_opening: `Callback(chr) -> bool` returning `True`
            iff the character is a opening operator.
        is_closing: `Callback(chr) -> bool` returning `True`
            iff the character is a closing operator.
        cat: `chr` representing the concatenation operator.
    Returns:
        The `iter` corresponding to `expression` by adding `cat`
        in the appropriate places.
    """
    if not is_binary:
        is_binary = lambda o: o == "|"
    if not is_unary:
        is_unary = lambda o: o in "*+?" or (len(o) > 2 and o[0] in "\\{[")
    if not is_opening:
        is_opening = lambda o: o == "("
    if not is_closing:
        is_closing = lambda o: o == ")"
    is_operator = lambda o: is_unary(o) or is_binary(o)

    prev_needs_dot = False
    for a in expression:
        if prev_needs_dot and not is_operator(a) and not is_closing(a):
            yield cat
            yield a
        else:
            yield a
        prev_needs_dot = not is_binary(a) and not is_opening(a)

#------------------------------------------------------------------------
# Shutting Yard algorithm
#------------------------------------------------------------------------

class DefaultShuntingYardVisitor:
    def on_pop_operator(self, o :str): pass
    def on_push_operator(self, o :str): pass
    def on_push_output(self, a :str): pass

class DebugShuntingYardVisitor(DefaultShuntingYardVisitor):
    def on_pop_operator(self, o :str):  print(f"pop op {o}")
    def on_push_operator(self, o :str): print(f"push op {o}")
    def on_push_output(self, a :str):   print(f"push out {a}")

def shunting_yard_postfix(
    expression    :iter,
    map_operators :dict,
    map_opener_closer = None,
    vis :DefaultShuntingYardVisitor = None
) -> deque:
    """
    Shunting-yard algorithm (converts infix notation to Reverse Polish Notation).
    Args:
        expression: Tokenized `iter` containing the input infix notation.
            Each iteration must move to the next token.
            Functions like `tokenize_alg`, `tokenize_re` can help to transform
            a `str` to the appropriate iterable.
        map_operators: `dict{str : Op}` defining the grammar.
        vis: A `DefaultShuntingYardVisitor` instance handling event raised by this function.
    Returns:
        The corresponding Reverse Polish Notation.
    """
    if not vis:
        vis = DefaultShuntingYardVisitor()

    output = deque() # queue
    operators = deque() # stack

    # Internals
    def preceeds(o1 :chr, o2 :chr) -> bool:
        return (
            (
                map_operators[o2].associativity == RIGHT and
                map_operators[o1].precedence > map_operators[o2].precedence
            ) or (
                map_operators[o2].associativity == LEFT and
                map_operators[o1].precedence >= map_operators[o2].precedence
            )
        )

    def pop_operator() -> chr:
        o = operators.pop()
        vis.on_pop_operator(o)
        return o

    def push_operator(o :chr) -> chr:
        operators.append(o)
        vis.on_push_operator(o)

    def push_output(a :chr) -> chr:
        output.append(a)
        vis.on_push_output(a)

    for a in expression:
        if a == "(":
            push_operator(a)
        elif a == ")":
            o = pop_operator()
            while o and o != "(":
                push_output(o)
                o = pop_operator()
        elif a in map_operators.keys():
            while operators and operators[-1] in map_operators.keys() and preceeds(operators[-1], a):
                push_output(pop_operator())
            push_operator(a)
        else:
            push_output(a)

    while operators:
        push_output(pop_operator())
    return output

