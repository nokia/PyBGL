#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.ipynb import in_ipynb, ipynb_display_graph
from pybgl.nfa import (
    Nfa, accepts, add_edge, initials, finals, delta, set_final
)
from pybgl.thompson_compile_nfa import (
    alternation, concatenation, literal,
    zero_or_one, zero_or_more, one_or_more,
    repetition, repetition_range,
    thompson_compile_nfa
)

def nfa_to_triple(nfa) -> tuple:
    q0s = set(initials(nfa))
    assert len(q0s) == 1
    q0 = q0s.pop()
    fs = set(finals(nfa))
    assert len(fs) == 1
    f = fs.pop()
    return (nfa, q0, f)

def make_nfa1() -> Nfa:
    (nfa, q0, f) = literal("x")
    return nfa

def make_nfa2() -> Nfa:
    g = Nfa(2)
    add_edge(0, 0, "a", g)
    add_edge(0, 1, "b", g)
    set_final(1, g)
    return g

def test_literal():
    (nfa, q0, f) = literal("a")
    assert set(initials(nfa)) == {0}
    assert set(finals(nfa)) == {1}
    assert delta(0, "a", nfa) == {1}

def test_concatenation():
    (nfa1, q01, f1) = nfa_to_triple(make_nfa1())
    (nfa2, q02, f2) = nfa_to_triple(make_nfa2())
    (nfa, q0, f) = concatenation(nfa1, q01, f1, nfa2, q02, f2)
    assert accepts("xaab", nfa) == True
    assert accepts("x", nfa) == False
    assert accepts("aab", nfa) == False

def test_alternation():
    (nfa1, q01, f1) = nfa_to_triple(make_nfa1())
    (nfa2, q02, f2) = nfa_to_triple(make_nfa2())
    (nfa, q0, f) = alternation(nfa1, q01, f1, nfa2, q02, f2)
    assert accepts("xaab", nfa) == False
    assert accepts("x", nfa) == True
    assert accepts("aab", nfa) == True

def test_zero_or_one():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    (nfa, q0, f) = zero_or_one(nfa, q0, f)
    assert accepts("", nfa) == True
    assert accepts("x", nfa) == True
    assert accepts("xx", nfa) == False
    assert accepts("a", nfa) == False

def test_zero_or_more():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    (nfa, q0, f) = zero_or_more(nfa, q0, f)
    assert accepts("", nfa) == True
    assert accepts("x", nfa) == True
    assert accepts("xx", nfa) == True
    assert accepts("a", nfa) == False

def test_one_or_more():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    (nfa, q0, f) = one_or_more(nfa, q0, f)
    assert accepts("", nfa) == False
    assert accepts("x", nfa) == True
    assert accepts("xx", nfa) == True
    assert accepts("a", nfa) == False

def test_repetition_0m():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    m = 4
    (nfa, q0, f) = repetition(nfa, q0, f, m, do_0m = True)
    words = ["x" * i for i in range(10)]
    # Between 0 and m repetition
    for (i, w) in enumerate(words):
        assert accepts(w, nfa) == (i <= m)

def test_repetition_mm():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    m = 4
    (nfa, q0, f) = repetition(nfa, q0, f, m, do_0m = False)
    words = ["x" * i for i in range(10)]
    # Exactly m repetition
    for (i, w) in enumerate(words):
        assert accepts(w, nfa) == (i == m)

def test_repetition_mn():
    (nfa, q0, f) = nfa_to_triple(make_nfa1())
    words = ["x" * i for i in range(10)]
    # Between m and n repetition
    for (m, n) in [(0, 1), (0, None), (1, None), (3, 3), (2, 4), (2, None)]:
        (nfa, q0, f) = literal("x")
        (nfa, q0, f) = repetition_range(nfa, q0, f, m, n)
        for (i, w) in enumerate(words):
            assert accepts(w, nfa) == (i >= m and (n is None or i <= n))

def test_thompson_compile_nfa():
    (nfa, q0, f) = thompson_compile_nfa("(a?b)*?c+d")
    if in_ipynb():
        ipynb_display_graph(nfa)
    w = "babbbababcccccd"
    assert accepts(w, nfa) == True
    print(f"accepts({w}, nfa) = {accepts(w, nfa)}")

