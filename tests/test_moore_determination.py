#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.automaton            import accepts
from pybgl.ipynb                import in_ipynb, ipynb_display_graph
from pybgl.moore_determination  import moore_determination

def make_nfa():
    from pybgl.thompson_compile_nfa import thompson_compile_nfa
    (nfa, q0, f) = thompson_compile_nfa("(a?b)*?c+d")
    return nfa

def test_moore_determination():
    nfa = make_nfa()
    w = "babbbababcccccd"
    assert accepts(w, nfa) == True

    for complete in [True, False]:
        dfa = moore_determination(nfa, complete=complete)
        if in_ipynb():
            ipynb_display_graph(dfa)
        assert accepts(w, dfa) == True
        print(f"accepts({w}, dfa) = {accepts(w, dfa)}")
