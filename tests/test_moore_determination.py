#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    in_ipynb,
    ipynb_display_graph,
    moore_determination,
    thompson_compile_nfa,
)


def make_nfa():
    (nfa, q0, f) = thompson_compile_nfa("(a?b)*?c+d")
    return nfa


def make_second_nfa():
    (nfa, q0, f) = thompson_compile_nfa("d?")
    return nfa


def test_moore_determination():
    nfa = make_nfa()
    w = "babbbababcccccd"
    assert nfa.accepts(w)

    for complete in [True, False]:
        dfa = moore_determination(nfa, complete=complete)
        if in_ipynb():
            ipynb_display_graph(dfa)
        assert dfa.accepts(w), f"dfa.accepts({w}) = {dfa.accepts(w)}"

    nfa = make_second_nfa()
    w = ""
    assert nfa.accepts(w)

    for complete in [True, False]:
        dfa = moore_determination(nfa, complete=complete)
        if in_ipynb():
            ipynb_display_graph(dfa)
        assert dfa.accepts(w), f"dfa.accepts({w}) = {dfa.accepts(w)}"
