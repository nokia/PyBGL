#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

import copy, re, string
from collections import deque

from pybgl.nfa import (
    Nfa, add_edge, add_vertex, edges, epsilon,
    label, is_final, set_initials, set_final,
    source, target, vertices
)
from pybgl.shunting_yard_postfix import (
    MAP_OPERATORS_RE, DefaultShuntingYardVisitor,
    shunting_yard_postfix, tokenizer_re
)

#-------------------------------------------------------------
# AST to NFA operations
#
# Thomson algorithm creates several NFA with a single initial
# state and a single final state and combine them to form
# the NFA representing a regular expression.
#
# The following functions craft NFAs resulting from the
# following operators:
#   .     concatenation
#   |     alternation
#   ?     0-1 repetition
#   *     0 or more repetitions
#   +     1 or more repetitions
#   {n}   n repetitions
#   {n,}  n or more repetitions
#   {,m}  0-m repetitions
#   {n,m} n-m repetitions
#   [x]   bracket expression
#   \x    escape sequence
#-------------------------------------------------------------

def literal(a :chr) -> Nfa:
    nfa = Nfa(2)
    add_edge(0, 1, a, nfa)
    set_final(1, nfa)
    return (nfa, 0, 1)

def insert_automaton(g1 :Nfa, g2 :Nfa, map21 :dict = None) -> dict:
    if not map21:
        map21 = dict()
    for q2 in vertices(g2):
        if q2 in map21.keys():
            continue
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

def concatenation(nfa1 :Nfa, q01 :int, f1 :int, nfa2 :Nfa, q02 :int, f2 :int) -> tuple:
    map21 = {q02 : f1}
    map21 = insert_automaton(nfa1, nfa2, map21)
    f2 = map21[f2]
    set_final(f1, nfa1, False)
    return (nfa1, q01, f2)

def alternation(nfa1 :Nfa, q01 :int, f1 :int, nfa2 :Nfa, q02 :int, f2 :int) -> tuple:
    map21 = {q02 : q01, f2 : f1}
    map21 = insert_automaton(nfa1, nfa2, map21)
    f2  = map21[f2]
    return (nfa1, q01, f2)

def zero_or_one(nfa :Nfa, q0 :int, f :int) -> tuple:
    eps = epsilon(nfa)
    add_edge(q0, f, eps, nfa)
    return (nfa, q0, f)

def zero_or_more(nfa :Nfa, q0 :int, f :int) -> tuple:
    eps = epsilon(nfa)
    add_edge(f, q0, eps, nfa)
    add_edge(q0, f, eps, nfa)
    return (nfa, q0, f)

def one_or_more(nfa :Nfa, q0 :int, f :int) -> tuple:
    eps = epsilon(nfa)
    add_edge(f, q0, eps, nfa)
    return (nfa, q0, f)

def repetition(nfa :Nfa, q0 :int, f :int, m :int) -> tuple:
    assert m >= 0
    if m == 0:
        nfa = Nfa(1)
        set_final(0, nfa)
        (nfa, q0, f) = (nfa, 0, 0)
    elif m > 1:
        eps = epsilon(nfa)
        ori = copy.deepcopy(nfa)
        q0_ori = q0
        f_ori = f
        for _ in range(m - 1):
            set_final(f, nfa, False)
            (nfa, q0, f) = concatenation(nfa, q0, f, ori, q0_ori, f_ori)
    return (nfa, q0, f)

def repetition_range(nfa :Nfa, q0 :int, f :int, m :int, n :int) -> tuple:
    assert n is None or m <= n, "The lower bound {m} must be less than the upper bound {n}"
    if   (m, n) == (0, 1):
        return zero_or_one(nfa, q0, f)
    elif (m, n) == (0, None):
        return zero_or_more(nfa, q0, f)
    elif (m, n) == (1, None):
        return one_or_more(nfa, q0, f)

    ori = copy.deepcopy(nfa)
    if n is None:
        (nfa1, q01, f1) = repetition(nfa, q0, f, m - 1)
        (nfa2, q02, f2) = one_or_more(ori, q0, f)
        return concatenation(nfa1, q01, f1, nfa2, q02, f2)
    else:
        (q0_ori, f_ori, ori) = (q0, f, copy.deepcopy(nfa))
        (nfa, _, f) = repetition(nfa, q0, f, m)
        finals = {f}
        # The m-n following NFA instances are optional. We add them
        # one by one to get their respective final states to build an
        # epsilon-transition toward a same and unique final state.
        for i in range(n - m):
            (nfa, q0, f) = concatenation(nfa, q0, f, ori, q0_ori, f_ori)
            finals.add(f)
        eps = epsilon(nfa)
        for pred_f in finals:
            if pred_f != f:
                add_edge(pred_f, f, eps, nfa)
        return (nfa, q0, f)

def bracket(chars :iter) -> tuple:
    nfa = Nfa(2)
    set_final(1, nfa)
    for a in chars:
        add_edge(0, 1, a, nfa)
    return (nfa, 0, 1)

#-------------------------------------------------------------
# Internal parsers
#-------------------------------------------------------------

def parse_repetition(s :str) -> tuple:
    r = re.compile(r"{\s*(\d+)\s*}")
    match = r.match(s)
    if match:
        m = n = int(match.group(1))
    else:
        r = re.compile(r"{\s*(\d*)\s*,\s*(\d*)\s*}")
        match = r.match(s)
        assert match, f"Invalid token {s}: Not well-formed"
        m = int(match.group(1)) if match.group(1) else 0
        n = int(match.group(2)) if match.group(2) else None
    return (m, n)

DEFAULT_ALPHABET = string.printable

def parse_bracket(s :str, whole_alphabet :iter = None) -> set:
    if not whole_alphabet:
        whole_alphabet = DEFAULT_ALPHABET
    if not (s[0] == "[" and s[-1] == "]"):
        raise ValueError(f"Invalid parameter: s = {s}")
    if len(s) < 3:
        raise ValueError(f"Unmatched []: s = {s}")

    reverse = (s[1] == "^")
    i = 2 if s[1] == "^" else 1
    accepted = set()
    last_non_hat = None
    imax = len(s)

    while i < imax - 1:
        a = s[i]
        if a == "-" and last_non_hat:
            m = ord(last_non_hat)
            n = ord(s[i + 1])
            if m > n:
                raise ValueError(f"Invalid end of interval in s = {s} at index m = {m}")
            for c in range(m, n + 1):
                accepted.add(chr(c))
            i += 1
        else:
            if a == "\\":
                accepted |= parse_escaped(s[i:i+2])
                i += 1
            else:
                accepted.add(a)
        last_non_hat = a
        i += 1
    return accepted if not reverse else set(whole_alphabet) - accepted

def parse_escaped(s :str, whole_alphabet :iter = None) -> set:
    MAP_ESCAPED_BRACKET = {
        r"\d" : "[0-9]",
        r"\D" : "[^0-9]",
        r"\s" : "[ \t]",
        r"\S" : "[^ \t]",
        # \w and \W should depend on the locale. Here, we assume ASCII.
        r"\w" : "[0-9A-Za-z]",
        r"\W" : "[^0-9A-Za-z]",
    }
    MAP_ESCAPED_SPECIAL = {
        r"\a" : "\a",
        r"\b" : "\b",
        r"\f" : "\f",
        r"\n" : "\n",
        r"\r" : "\r",
        r"\t" : "\t",
        r"\v" : "\v",
    }
    if len(s) == 2:
        if s in {
            r"\+", r"\*", r"\?", r"\.", r"\|",
            r"\[", r"\]", r"\(", r"\)", r"\{", r"\}"
        }:
            return {s[1]}
        elif s in {r"\A", r"\B", r"\Z"}:
            raise ValueError(f"Escape sequence {s} not supported")
        else:
            a = MAP_ESCAPED_SPECIAL.get(s)
            if a is not None:
                return {a}
            r = MAP_ESCAPED_BRACKET.get(s)
            if r is not None:
                chars = parse_bracket(r, whole_alphabet)
                return chars
    else:
        if s[1] in {"x", "u", "U", "N", "0"}:
            raise ValueError(f"Escape sequence {s} not supported")
    raise ValueError(f"Invalid escape sequence {s}")

#-------------------------------------------------------------
# Thompson algorithm
#-------------------------------------------------------------

def thompson_compile_nfa(expression :str, whole_alphabet = None) -> Nfa:
    if not expression:
        g = Nfa(1)
        set_final(0, g)
        return (g, 0, 0)
    if whole_alphabet is None:
        whole_alphabet = DEFAULT_ALPHABET
    expression = list(tokenizer_re(expression, cat = "."))

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
                    alternation   if a == "|" else
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
            elif a[0] == "{":
                (nfa1, q01, f1) = self.nfas.pop()
                (m, n) = parse_repetition(a)
                (nfa1, q01, f1) = repetition_range(nfa1, q01, f1, m, n)
            elif a[0] == "[":
                chars = parse_bracket(a, whole_alphabet)
                (nfa1, q01, f1) = bracket(chars)
            elif a[0] == "\\":
                chars = parse_escaped(a, whole_alphabet)
                (nfa1, q01, f1) = bracket(chars)
            else:
                (nfa1, q01, f1) = literal(a)
            self.nfas.append((nfa1, q01, f1))

    vis = ThompsonShuntingYardVisitor()
    shunting_yard_postfix(expression, map_operators=MAP_OPERATORS_RE, vis=vis)
    assert len(vis.nfas) == 1
    (nfa, q0, f) = vis.nfas.pop()
    return (nfa, q0, f)
