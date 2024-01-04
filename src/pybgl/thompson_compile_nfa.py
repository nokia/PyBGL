#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

import copy
import re
import string
from collections import deque
from .nfa import *
# from .nfa import Nfa
from .shunting_yard_postfix import (
    MAP_OPERATORS_RE, DefaultShuntingYardVisitor,
    shunting_yard_postfix, tokenizer_re
)


DEFAULT_ALPHABET = string.printable


# -------------------------------------------------------------
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
# -------------------------------------------------------------

def literal(a: str) -> Nfa:
    """
    Builds a NFA that recognizes a single symbol.

    Args:
        a (str): The considered symbol.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state
        that recognizes the language {a};
        ``q0`` is its initial state;
        ``f`` is its initial state;
    """
    nfa = Nfa(2)
    nfa.add_edge(0, 1, a)
    nfa.set_final(1)
    return (nfa, 0, 1)


def insert_automaton(g1: Nfa, g2: Nfa, map21: dict = None) -> dict:
    """
    Inserts an NFA in another NFA.
    In the end, in the first automaton (modified in place),
    there are two disconnected automata.
    The states of the second NFA are reindexed to not collide
    with those already used in the first NFA.

    Args:
        g1 (Nfa): The first NFA, modified in place.
        g2 (Nfa): The second NFA, not modified.

    Returns:
        A dictionary precising how the state of ``g2`` have
        been reindexed once inserted in ``g1``.
    """
    if not map21:
        map21 = dict()
    for q2 in g2.vertices():
        if q2 in map21.keys():
            continue
        q1 = g1.add_vertex()
        if g2.is_final(q2):
            g1.set_final(q1)
        map21[q2] = q1
    for e2 in g2.edges():
        q2 = g2.source(e2)
        r2 = g2.target(e2)
        a = g2.label(e2)
        q1 = map21[q2]
        r1 = map21[r2]
        g1.add_edge(q1, r1, a)
    return map21


def concatenation(
    nfa1: Nfa,
    q01: int,
    f1: int,
    nfa2: Nfa,
    q02: int,
    f2: int
) -> tuple:
    """
    Builds a NFA obtained by concatenating two NFAs.

    Args:
        g1 (Nfa): The first NFA made of single initial state and a
            single final state.
        q01 (int): The initial state of ``g1``.
        f1 (int): The initial state of ``g1``.
        g2 (Nfa): The second NFA made of single initial state and a
            single final state.
        q02 (int): The initial state of ``g2``.
        f2 (int): The initial state of ``g2``.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state
        that recognizes the language
        ``{s1 + s2 for s1 in L(g1) for s2 in L(g2)}``
        where ``L`` returns the language of an automaton;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    map21 = insert_automaton(nfa1, nfa2)
    nfa1.add_edge(f1, map21[q02], nfa1.epsilon)
    nfa1.set_initials({q01})
    nfa1.set_final(f1, False)
    return (nfa1, q01, map21[f2])


def alternation(
    nfa1: Nfa,
    q01: int,
    f1: int,
    nfa2: Nfa,
    q02: int,
    f2: int
) -> tuple:
    """
    Builds a NFA that implements the ``|`` regular expression operator.

    Args:
        g1 (Nfa): The first NFA made of single initial state and a
            single final state.
        q01 (int): The initial state of ``g1``.
        f1 (int): The initial state of ``g1``.
        g2 (Nfa): The second NFA made of single initial state and a
            single final state.
        q02 (int): The initial state of ``g2``.
        f2 (int): The initial state of ``g2``.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state
        that recognizes the language ``L(g1) | L(g2)``;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    eps1 = nfa1.epsilon
    map21 = insert_automaton(nfa1, nfa2)
    q0 = nfa1.add_vertex()
    nfa1.add_edge(q0, q01, eps1)
    nfa1.add_edge(q0, map21[q02], eps1)
    nfa1.set_initials({q0})
    f = nfa1.add_vertex()
    nfa1.add_edge(f1, f, eps1)
    nfa1.add_edge(map21[f2], f, eps1)
    nfa1.set_final(f1, False)
    nfa1.set_final(map21[f2], False)
    nfa1.set_final(f, True)
    return (nfa1, q0, f)


def zero_or_one(nfa: Nfa, q0: int, f: int) -> tuple:
    """
    Builds a NFA that implements the ``?`` regular expression operator
    (0 or 1 repetition).

    Args:
        nfa (Nfa): A NFA made of single initial state and a
            single final state.
        q0 (int): The initial state of ``nfa``.
        f1 (int): The initial state of ``nfa``.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state
        that recognizes the language ``L(g1) | set()``
        where ``L`` returns the language of an automaton;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    eps = nfa.epsilon
    nfa.add_edge(q0, f, eps)
    return (nfa, q0, f)


def zero_or_more(nfa: Nfa, q0: int, f: int) -> tuple:
    """
    Builds a NFA that implements the ``*`` regular expression operator
    (0 or more repetitions).

    Args:
        nfa (Nfa): A NFA made of single initial state and a
            single final state.
        q0 (int): The initial state of ``nfa``.
        f1 (int): The initial state of ``nfa``.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    eps = nfa.epsilon
    new_q0 = nfa.add_vertex()
    new_f = nfa.add_vertex()
    nfa.add_edge(new_q0, q0, eps)
    nfa.add_edge(f, new_f, eps)
    nfa.add_edge(new_q0, new_f, eps)
    nfa.add_edge(new_f, new_q0, eps)
    nfa.set_initials({new_q0})
    nfa.set_final(f, False)
    nfa.set_final(new_f, True)
    return (nfa, new_q0, new_f)


def one_or_more(nfa: Nfa, q0: int, f: int) -> tuple:
    """
    Builds a NFA that implements the ``+`` regular expression operator
    (0 or more repetitions).

    Args:
        nfa (Nfa): A NFA made of single initial state and a
            single final state.
        q0 (int): The initial state of ``nfa``.
        f1 (int): The initial state of ``nfa``.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    eps = nfa.epsilon
    new_q0 = nfa.add_vertex()
    new_f = nfa.add_vertex()
    nfa.add_edge(new_q0, q0, eps)
    nfa.add_edge(f, new_f, eps)
    nfa.add_edge(new_f, new_q0, eps)
    nfa.set_initials({new_q0})
    nfa.set_final(f, False)
    nfa.set_final(new_f, True)
    return (nfa, new_q0, new_f)


def repetition(nfa: Nfa, q0: int, f: int, m: int) -> tuple:
    """
    Builds the NFA that implements the ``{m}`` regular expression operator
    (exacly ``m`` repetitions).

    Args:
        nfa (Nfa): A NFA made of single initial state and a
            single final state.
        q0 (int): The initial state of ``nfa``.
        f1 (int): The initial state of ``nfa``.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state
        that recognizes the language ``{s1 * m for s1 in L(nfa)}``
        where L returns the language of an automaton;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    assert m >= 0
    if m == 0:
        nfa = Nfa(1)
        nfa.set_final(0)
        (nfa, q0, f) = (nfa, 0, 0)
    elif m > 1:
        ori = copy.deepcopy(nfa)
        q0_ori = q0
        f_ori = f
        for _ in range(m - 1):
            nfa.set_final(f, False)
            (nfa, q0, f) = concatenation(nfa, q0, f, ori, q0_ori, f_ori)
    return (nfa, q0, f)


def repetition_range(nfa: Nfa, q0: int, f: int, m: int, n: int) -> tuple:
    """
    Builds a NFA that implements the ``{m, n}`` regular expression operator
    (between ``m`` and ``n`` repetitions).

    Args:
        nfa (Nfa): A NFA made of single initial state and a
            single final state.
        q0 (int): The initial state of ``nfa``.
        f1 (int): The initial state of ``nfa``.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    assert n is None or m <= n, (
        f"The lower bound {m} must be less than the upper bound {n}"
    )
    if (m, n) == (0, 1):
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
        final_states = {f}
        # The m-n following NFA instances are optional. We add them
        # one by one to get their respective final states to build an
        # epsilon-transition toward a same and unique final state.
        for i in range(n - m):
            (nfa, q0, f) = concatenation(nfa, q0, f, ori, q0_ori, f_ori)
            final_states.add(f)
        eps = nfa.epsilon
        for pred_f in final_states:
            if pred_f != f:
                nfa.add_edge(pred_f, f, eps)
        return (nfa, q0, f)


def bracket(chars: iter) -> tuple:
    """
    Builds a NFA that recognizes a set of words made of exactly one
    symbol of the alphabet.

    Args:
        chars (iter): The recognized symbols.

    Returns:
        A ``(nfa, q0, f)`` tuple, where:
        ``nfa`` is a NFA made of single initial state and a single final state;
        ``q0`` is its initial state;
        ``f`` is its initial state.
    """
    nfa = Nfa(2)
    nfa.set_final(1)
    for a in chars:
        nfa.add_edge(0, 1, a)
    return (nfa, 0, 1)


# -------------------------------------------------------------
# Internal parsers
# -------------------------------------------------------------

def parse_repetition(s: str) -> tuple:
    """
    Parses the ``{m}`` and the ``"{m, n}"`` operator involved in a
    regular, where ``m`` and ``n`` are two integers
    such that ``0 <= m <= n``.
    Regarding the ``"{m, n}"`` operator, ``m`` and/or ``n`` may be omitted
    (and respectively defaults to ``0`` and ``None``).

    Args:
        s (str): The parsed regular expression.

    Raises:
        :py:class:`RuntimeError` if the string is not well-formed.
        :py:class:`ValueError` if ``m`` or ``n`` are invalid.

    Returns:
        The corresponding ``(m, n)`` tuple.
    """
    r = re.compile(r"{\s*(\d+)\s*}")
    match = r.match(s)
    if match:
        m = n = int(match.group(1))
    else:
        r = re.compile(r"{\s*(\d*)\s*,\s*(\d*)\s*}")
        match = r.match(s)
        if not match:
            raise RuntimeError(f"Invalid token {s}: Not well-formed")
        m = int(match.group(1)) if match.group(1) else 0
        if not m >= 0:
            raise ValueError(f"Invalid m = {m}")
        n = int(match.group(2)) if match.group(2) else None
        if n is not None and not n >= m:
            raise ValueError(f"Invalid n = {n} (m = {m})")
    return (m, n)


def parse_bracket(s: str, whole_alphabet: iter = None) -> set:
    """
    Parse a ``[...]``-like regular expression (set of symbols).

    This function supports:

    - reversed set of characters (if the first character inside
      the bracket is ``^``), (e.g., ``[^ab]`` means neither ``a`` or
      ``b``);
    - range of characters, (e.g., ``[A-Za-z]`` corresponds to any
      latin letter);
    - escaped characters (see :py:data:`MAP_ESCAPED_BRACKET`` and
      :py:data:`MAP_ESCAPED_SPECIAL``)

    Args:
        s (str): The parsed regular expression.
        whole_alphabet (iter): The whole alphabet (required to
            implement the ``[^...]`` operator.

    Returns:
        The corresponding matched characters.
    """
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
                raise ValueError(
                    f"Invalid end of interval in s = {s} at index m = {m}"
                )
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


MAP_ESCAPED_BRACKET = {
    r"\d":  "[0-9]",
    r"\D":  "[^0-9]",
    r"\s":  "[ \t]",
    r"\S":  "[^ \t]",
    # \w and \W should depend on the locale. Here, we assume ASCII.
    r"\w":  "[0-9A-Za-z]",
    r"\W":  "[^0-9A-Za-z]",
}


MAP_ESCAPED_SPECIAL = {
    r"\a":  "\a",
    r"\b":  "\b",
    r"\f":  "\f",
    r"\n":  "\n",
    r"\r":  "\r",
    r"\t":  "\t",
    r"\v":  "\v",
}


def parse_escaped(s: str, whole_alphabet: iter = None) -> set:
    """
    Parses a regular-expression escaped sequence.

    Args:
        s (str): The parsed regular expression.
        whole_alphabet (iter): The whole alphabet (required to
            implement the ``[^...]`` operator.

    Returns:
        The corresponding characters.
    """
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


# -------------------------------------------------------------
# Thompson algorithm
# -------------------------------------------------------------

def thompson_compile_nfa(expression: str, whole_alphabet: iter = None) -> Nfa:
    """
    Compiles a NFA from a regular expression using the
    `Thompson transformation
    <https://en.wikipedia.org/wiki/Thompson%27s_construction>`__.

    Args:
        expression (str): A regular expression.
        whole_alphabet (iter): The whole alphabet, only needed to
            process the ``[^..]`` operator occurrences.

    Returns:
        The correspoding NFA, made of single initial state and a single
        final state.
    """
    if not expression:
        g = Nfa(1)
        g.set_final(0)
        return (g, 0, 0)
    if whole_alphabet is None:
        whole_alphabet = DEFAULT_ALPHABET
    expression = list(tokenizer_re(expression, cat="."))

    class ThompsonShuntingYardVisitor(DefaultShuntingYardVisitor):
        def __init__(self):
            """
            Constructor.
            """
            self.cur_id = 0
            self.nfas = deque()

        def on_push_output(self, a):
            # Overloaded method
            if a in {".", "|"}:
                (nfa2, q02, f2) = self.nfas.pop()
                (nfa1, q01, f1) = self.nfas.pop()
                f = (
                    concatenation if a == "."
                    else alternation if a == "|"
                    else None
                )
                (nfa1, q01, f1) = f(nfa1, q01, f1, nfa2, q02, f2)
            elif a in {"?", "*", "+"}:
                (nfa1, q01, f1) = self.nfas.pop()
                f = (
                    zero_or_one if a == "?"
                    else zero_or_more if a == "*"
                    else one_or_more if a == "+"
                    else None
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
