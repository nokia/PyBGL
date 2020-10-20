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

(RIGHT, LEFT) = range(2)

Op = namedtuple(
    'Op', ['precedence', 'associativity']
)

OPERATORS_ALG = {
    '^' : Op(precedence=4, associativity=RIGHT),
    '*' : Op(precedence=3, associativity=LEFT),
    '/' : Op(precedence=3, associativity=LEFT),
    '+' : Op(precedence=2, associativity=LEFT),
    '-' : Op(precedence=2, associativity=LEFT)
}

OPERATORS_RE = {
    "*" : Op(precedence=4, associativity=LEFT),
    "+" : Op(precedence=4, associativity=LEFT),
    "?" : Op(precedence=3, associativity=LEFT),
    "." : Op(precedence=2, associativity=LEFT),
    "|" : Op(precedence=1, associativity=LEFT),
}

class DefaultShuntingYardVisitor:
    def on_pop_operator(self, o :chr): pass
    def on_push_operator(self, o :chr): pass
    def on_push_output(self, a :chr): pass

class DebugShuntingYardVisitor(DefaultShuntingYardVisitor):
    def on_pop_operator(self, o :chr):  print(f"pop op {o}")
    def on_push_operator(self, o :chr): print(f"push op {o}")
    def on_push_output(self, a :chr):   print(f"push out {a}")

def shunting_yard_postfix(expression :str, map_operators :dict, vis :DefaultShuntingYardVisitor = None) -> deque:
    """
    Shunting-yard algorithm (converts infix notation to Reverse Polish Notation).
    Args:
        expression: str containing the input infix notation.
        map_operators:
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

#list(shunting_yard_postfix("((1.1)?.2.2.2)*?.(3.3)+.(4.4)", RE_OPS))

