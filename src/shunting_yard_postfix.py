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

from collections import deque, namedtuple

#------------------------------------------------------------------------
# Map token related to operators with the corresponding description
#------------------------------------------------------------------------

(RIGHT, LEFT) = range(2)

Op = namedtuple(
    "Op", ["cardinality", "precedence", "associativity"]
)

OPERATORS_ALG = {
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

OPERATORS_RE = {
    # Unary operators
    "*" : Op(cardinality=1, precedence=4, associativity=LEFT),
    "+" : Op(cardinality=1, precedence=4, associativity=LEFT),
    "?" : Op(cardinality=1, precedence=3, associativity=LEFT),
    # TODO add {n} {n,m} {n,} operators
    # Binary operators
    "." : Op(cardinality=2, precedence=2, associativity=LEFT),
    "|" : Op(cardinality=2, precedence=1, associativity=LEFT),
}

#------------------------------------------------------------------------
# Tokenization (token = atomic sequence of characters)
#------------------------------------------------------------------------

# See https://docs.python.org/3/library/re.html#writing-a-tokenizer
import re
def re_escape(s :chr) -> str:
    return "".join(
        a if a not in "|[]{}.+*?()^$\\"
        else "\\" + a
        for a in s
    )

RE_OPERATORS_ALG = [
    re_escape(op)
    for op in list(OPERATORS_ALG.keys()) + list("()")
]

RE_OPERATORS_RE = [
    re_escape(op)
    for op in list(OPERATORS_RE.keys()) + list("()")
] + [
    # Extra repetition operators
    "\\{\\s*\\d+(\\s*,)?(\\s*\\d+)?\\s*\\}",
    # Character classes
    "\\[.*\\]",
    # Escape sequences
    "(\\\\(d|s|w))",
]

# TODO add re_ignore
def tokenize(expression :str, re_operators :set, operator_to_token = None):
    if not operator_to_token:
        # Depending if prev_is_operator is True of False, we can detect
        # whether an operator refers to its unary or binary version.
        operator_to_token = lambda prev_is_operator, operator: operator
    pattern = "|".join(re_operator for re_operator in set(re_operators))
    tokenizer = re.compile(pattern)
    start = 0
    prev_is_operator = True
    for match in tokenizer.finditer(expression):
        operand = expression[start:match.start()]
        if operand:
            yield operand
            prev_is_operator = False
        operator = match.group(0)
        if operator:
            yield operator_to_token(prev_is_operator, operator)
            prev_is_operator = True
        start = match.end()
    operand = expression[start:]
    if operand:
        yield operand

def alg_operator_to_token(prev_is_operator :bool, operator :chr) -> str:
    if prev_is_operator and operator not in "()":
        if   operator == "+": return "u+"
        elif operator == "-": return "u-"
        else: raise RuntimeError(f"Invalid unary operator '{operator}'")
    else:
        return operator

tokenize_alg = lambda expr: tokenize(expr, RE_OPERATORS_ALG, alg_operator_to_token)
tokenize_re  = lambda expr: tokenize(expr, RE_OPERATORS_RE)

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
    tokenize      :callable = tokenize,
    map_opener_closer = None,
    vis :DefaultShuntingYardVisitor = None
) -> deque:
    """
    Shunting-yard algorithm (converts infix notation to Reverse Polish Notation).
    Args:
        expression: Tokenized `iter` containing the input infix notation.
            See also tokenize_alg, tokenize_re.
        map_operators: `dict{str : Op}` defining the grammar.
        tokenize: Pass function in charge to tokenize expression or `None`.
        vis: A `DefaultShuntingYardVisitor` instance handling event raised by this function.
    Returns:
        The corresponding Reverse Polish Notation.
    """
    if tokenize:
        expression = tokenize(
            expression,
            [re_escape(op) for op in list(map_operators.keys()) + ["(", ")"]]
        )
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

