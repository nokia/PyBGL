#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl.automaton import accepts
from pybgl.ipynb import in_ipynb, ipynb_display_graph
from pybgl.moore_determination import moore_determination

def make_nfa():
    from pybgl.thompson_compile_nfa import thompson_compile_nfa
    (nfa, q0, f) = thompson_compile_nfa("(a?b)*?c+d")
    return nfa

def make_second_nfa():
    from pybgl.thompson_compile_nfa import thompson_compile_nfa
    (nfa, q0, f) = thompson_compile_nfa("d?")
    return nfa

def test_moore_determination():
    nfa = make_nfa()
    w = "babbbababcccccd"
    assert accepts(w, nfa)

    for complete in [True, False]:
        dfa = moore_determination(nfa, complete=complete)
        if in_ipynb():
            ipynb_display_graph(dfa)
        assert accepts(w, dfa), f"accepts({w}, dfa) = {accepts(w, dfa)}"

    nfa = make_second_nfa()
    w = ""
    assert accepts(w, nfa)

    for complete in [True, False]:
        dfa = moore_determination(nfa, complete=complete)
        if in_ipynb():
            ipynb_display_graph(dfa)
        assert accepts(w, dfa), f"accepts({w}, dfa) = {accepts(w, dfa)}"
