#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.automaton            import Automaton
from pybgl.nfa                  import Nfa
from pybgl.thompson_compile_nfa import thompson_compile_nfa
from pybgl.moore_determination  import moore_determination

def compile_nfa(regexp :str) -> tuple:
    (nfa, q0, f) = thompson_compile_nfa(regexp)
    return nfa

def compile_dfa(regexp :str, complete :bool = False) -> Automaton:
    (nfa, q0, f) = thompson_compile_nfa(regexp)
    dfa = moore_determination(nfa, complete=complete)
    return dfa
