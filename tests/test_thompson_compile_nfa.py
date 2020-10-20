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
    alternation, catify, concatenation, literal,
    zero_or_one, zero_or_more, one_or_more,
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

def test_catify():
    assert "".join(catify("123?(4|5)*67")) == "1.2.3?.(4|5)*.6.7"
    assert "".join(catify("(1?2)*?3+5")) == "(1?.2)*?.3+.5"

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
    (nfa1, q01, f1) = nfa_to_triple(make_nfa1())
    (nfa1, q01, f1) = zero_or_one(nfa1, q01, f1)
    assert accepts("", nfa1) == True
    assert accepts("x", nfa1) == True
    assert accepts("xx", nfa1) == False
    assert accepts("a", nfa1) == False

def test_zero_or_more():
    (nfa1, q01, f1) = nfa_to_triple(make_nfa1())
    (nfa1, q01, f1) = zero_or_more(nfa1, q01, f1)
    assert accepts("", nfa1) == True
    assert accepts("x", nfa1) == True
    assert accepts("xx", nfa1) == True
    assert accepts("a", nfa1) == False

def test_one_or_more():
    (nfa1, q01, f1) = nfa_to_triple(make_nfa1())
    (nfa1, q01, f1) = one_or_more(nfa1, q01, f1)
    assert accepts("", nfa1) == False
    assert accepts("x", nfa1) == True
    assert accepts("xx", nfa1) == True
    assert accepts("a", nfa1) == False

def test_thompson_compile_nfa():
    (nfa, q0, f) = thompson_compile_nfa("(a?b)*?c+d")
    if in_ipynb():
        ipynb_display_graph(nfa)
    w = "babbbababcccccd"
    assert accepts(w, nfa) == True
    print(f"accepts({w}, nfa) = {accepts(w, nfa)}")

