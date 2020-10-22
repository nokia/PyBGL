#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from collections import deque

from pybgl.nfa import (
    Nfa, add_edge, add_vertex, edges, epsilon,
    label, is_final, set_initials, set_final,
    source, target, vertices
)
from pybgl.shunting_yard_postfix import (
    MAP_OPERATORS_RE, DefaultShuntingYardVisitor,
    catify, shunting_yard_postfix
)

#-------------------------------------------------------------
# AST to NFA operations
#
# Thomson algorithm creates several NFA with a single initial
# state and a single final state and combine them to form
# the NFA representing a regular expression.
#
# The following functions implement the .|+*? operators.
#-------------------------------------------------------------

def literal(a :chr) -> Nfa:
    nfa = Nfa(2)
    add_edge(0, 1, a, nfa)
    set_final(1, nfa)
    return (nfa, 0, 1)

def insert_automaton(g1 :Nfa, g2 :Nfa) -> dict:
    map21 = dict()
    for q2 in vertices(g2):
        q1 = add_vertex(g1)
        if is_final(q2, g2):
            set_final(q1, g1)
        map21[q2] = q1
    for e2 in edges(g2):
        q2 = source(e2, g2)
        r2 = target(e2, g2)
        a  = label(e2, g2)
        q1 = map21[q2]
        r1 = map21[r2]
        add_edge(q1, r1, a, g1)
    return map21

def concatenation(nfa1 :Nfa, q01 :int, f1 :int, nfa2 :Nfa, q02 :int, f2 :int) -> Nfa:
    eps = epsilon(nfa1)
    map21 = insert_automaton(nfa1, nfa2)
    q02 = map21[q02]
    f2 = map21[f2]
    add_edge(f1, q02, eps, nfa1)
    set_final(f1, nfa1, False)
    return (nfa1, q01, f2)

def alternation(nfa1 :Nfa, q01 :int, f1 :int, nfa2 :Nfa, q02 :int, f2 :int) -> Nfa:
    eps = epsilon(nfa1)
    map21 = insert_automaton(nfa1, nfa2)
    q02 = map21[q02]
    f2  = map21[f2]
    set_final(f1, nfa1, False)
    add_edge(q01, q02, eps, nfa1)
    add_edge(f1, f2, eps, nfa1)
    return (nfa1, q01, f2)

def zero_or_one(nfa :Nfa, q0 :int, f :int) -> Nfa:
    eps = epsilon(nfa)
    add_edge(q0, f, eps, nfa)
    return (nfa, q0, f)

def zero_or_more(nfa :Nfa, q0 :int, f :int) -> Nfa:
    eps = epsilon(nfa)
    s = add_vertex(nfa)
    t = add_vertex(nfa)
    add_edge(f, q0, eps, nfa)
    add_edge(s, q0, eps, nfa)
    add_edge(f, t, eps, nfa)
    add_edge(s, t, eps, nfa)
    set_initials({s}, nfa)
    set_final(f, nfa, False)
    set_final(t, nfa)
    return (nfa, s, t)

def one_or_more(nfa :Nfa, q0 :int, f :int) -> Nfa:
    eps = epsilon(nfa)
    add_edge(f, q0, eps, nfa)
    return (nfa, q0, f)

#-------------------------------------------------------------
# Thompson algorithm
#-------------------------------------------------------------

def thompson_compile_nfa(expression :str) -> Nfa:
    expression = "".join([
        a for a in catify(
            expression,
            is_binary = lambda o: o in "|",
            is_unary  = lambda o: o in "*+?",
            cat="."
        )
    ])

    class ThompsonShuntingYardVisitor(DefaultShuntingYardVisitor):
        def __init__(self):
            self.cur_id = 0
            self.nfas = deque()
        def on_push_output(self, a):
            if a in {".", "|"}:
                (nfa2, q02, f2) = self.nfas.pop()
                (nfa1, q01, f1) = self.nfas.pop()
                f = (
                    concatenation if a == "." else
                    union         if a == "|" else
                    None
                )
                (nfa1, q01, f1) = f(nfa1, q01, f1, nfa2, q02, f2)
            elif a in {"?", "*", "+"}:
                (nfa1, q01, f1) = self.nfas.pop()
                f = (
                    zero_or_one  if a == "?" else
                    zero_or_more if a == "*" else
                    one_or_more  if a == "+" else
                    None
                )
                (nfa1, q01, f1) = f(nfa1, q01, f1)
            else:
                (nfa1, q01, f1) = literal(a)
            self.nfas.append((nfa1, q01, f1))

    vis = ThompsonShuntingYardVisitor()
    shunting_yard_postfix(expression, map_operators=MAP_OPERATORS_RE, vis=vis)
    assert len(vis.nfas) == 1
    (nfa, q0, f) = vis.nfas.pop()
    return (nfa, q0, f)


