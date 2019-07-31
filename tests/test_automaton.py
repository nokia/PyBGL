#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.automaton import Automaton, accepts, add_edge, alphabet, delta, edge, \
    final, initial, is_complete, is_deterministic, is_final, is_finite, is_initial, \
    is_minimal, label, make_automaton, set_final, sigma

G1 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 2, 'a'), (1, 1, 'b'),
        (2, 1, 'a'), (2, 1, 'b'),
    ], 0, {1}
)

G2 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ], 0, {1}
)

G3 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
    ], 0, {}
)

G4 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ], 0, {1}
)

G5 = make_automaton(
    [
        (0, 0, 'a'), (0, 1, 'b'),
        (1, 1, 'b'), (1, 0, 'a')
    ], 0, {}
)

def test_initial():
    assert initial(G1) == 0

def test_final():
    assert final(G1) == {1}

def test_alphabet():
    assert alphabet(G1) == {"a", "b"}

def test_is_deterministic():
    assert is_deterministic(G1) == True

def test_is_finite():
    assert is_finite(G1) == True

def test_is_complete():
    assert is_complete(G1) == True
    assert is_complete(G2) == False
    assert is_complete(G3) == False
    assert is_complete(G4) == True
    assert is_complete(G5) == True

def test_accepts():
    assert accepts("", G1) == False
    assert accepts("aaab", G1) == True
    assert accepts("aaaba", G1) == False
    assert accepts("aaabaa", G1) == True
    assert accepts("aaabaabb", G1) == True
