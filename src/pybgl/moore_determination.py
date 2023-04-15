#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .automaton import Automaton, alphabet, add_vertex, add_edge, delta, set_final
from .nfa import Nfa, initials, is_final, sigma

def moore_determination(nfa: Nfa, dfa: Automaton = None, complete: bool = True) -> Automaton:
    """
    Converts the input NFA into a DFA.
    The output DFA has a state for every *reachable* subset of states in the input NFA.
    In the worst case, there will be an exponential increase in the number of states.
    Adapted from `this script <https://viterbi-web.usc.edu/~breichar/teaching/2011cs360/NFAtoDFA.py>`.

    Args:
        nfa (Nfa): An `Nfa` instance.
        dfa (Automaton): Pass `None` or a reference to an empty
            :py:class:`Automaton` instance.
        complete (bool): Pass `True` to build the complete automaton (original algorithm).
          Pass `False` to build a smaller automaton (this save the "trash" state
          and its corresponding input transitions).

    Returns:
        The corresponding :py:class:`Automaton` instance.
    """
    def dfa_add_state(qs):
        q = map_qs_q[qs] = add_vertex(dfa)
        if any(is_final(_, nfa) for _ in qs):
            set_final(q, dfa)
        return q

    full_sigma = alphabet(nfa)
    if dfa is None:
        dfa = Automaton()
    map_qs_q = dict() # Maps subset of states of nfa with the corresponding dfa state.

    q0s = frozenset(nfa.delta_epsilon(initials(nfa)))
    unprocessed_qs = set() # Keeps track of qs for which delta is not yet installed in dfa
    unprocessed_qs.add(q0s)
    q0 = dfa_add_state(q0s)

    while unprocessed_qs:
        qs = unprocessed_qs.pop()
        q = map_qs_q[qs]
        sigma_ = (
            full_sigma if complete
            else set.union(*[sigma(q, nfa) for q in qs]) if qs
            else set()
        )
        for a in sigma_:
            rs = (
                frozenset(set.union(*[delta(q, a, nfa) for q in qs])) if qs
                else frozenset()
            )
            r = map_qs_q.get(rs)
            if r is None:
                r = dfa_add_state(rs)
                unprocessed_qs.add(rs)
            add_edge(q, r, a, dfa)
    return dfa