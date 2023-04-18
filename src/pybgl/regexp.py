#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .automaton import Automaton
from .nfa import Nfa
from .thompson_compile_nfa import thompson_compile_nfa
from .moore_determination import moore_determination

def compile_nfa(regexp: str) -> Nfa:
    """
    Builds a
    `Non-deterministic Finite Automaton <https://en.wikipedia.org/wiki/Nondeterministic_finite_automaton>`__
    from a
    `regular expression <https://en.wikipedia.org/wiki/Regular_expression>`__.

    Args:
        regexp (str): A regular expression.

    Returns:
        A corresponding NFA.
    """
    (nfa, q0, f) = thompson_compile_nfa(regexp)
    return nfa

def compile_dfa(regexp: str, complete: bool = False) -> Automaton:
    """
    Builds a
    `Deterministic Finite Automaton <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`__.
    from a
    `regular expression <https://en.wikipedia.org/wiki/Regular_expression>`__.

    Args:
        regexp (str): A regular expression.

    Returns:
        A corresponding DFA.
    """
    (nfa, q0, f) = thompson_compile_nfa(regexp)
    dfa = moore_determination(nfa, complete=complete)
    return dfa
