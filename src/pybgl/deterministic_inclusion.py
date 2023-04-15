#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the PyBGL project.
# https://github.com/nokia/pybgl

from pybgl.automaton import Automaton, is_final
from pybgl.parallel_breadth_first_search import (
    ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search
)
from pybgl.suffix_trie import make_suffix_trie

class ContradictionException(Exception):
    pass

class DeterministicInclusionVisitor(ParallelBreadthFirstSearchVisitor):
    def __init__(self):
        self.ret = 0

    def update(self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton):
        f1 = is_final(q1, g1)
        f2 = is_final(q2, g2)
        if f1 ^ f2:
            ret = 1 if f2 else -1
            if self.ret == 0:
                self.ret = ret
            elif self.ret != ret:
                raise ContradictionException()

    def start_vertex(self, s1 :int, g1 :Automaton, s2 :int, g2 :Automaton):
        self.update(s1, g1, s2, g2)

    def discover_vertex(self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton):
        self.update(q1, g1, q2, g2)

def deterministic_inclusion(
    g1: Automaton,
    g2: Automaton,
    vis: DeterministicInclusionVisitor = None
) -> int:
    """
    Tests whether the language of a deterministic automaton is
    included in the language of another deterministic automaton.

    Args:
        g1 (Automaton): The left operand.
        g2 (Automaton): The right operand.
        vis: A :py:class:`DeterministicInclusionVisitor` instance or ``None``.

    Returns:
        - ``1`` if L(g1) c L(g2)
        - ``0`` if L(g1) = L(g2)
        - ``-1`` if L(g2) c L(g1)
        - ``None`` otherwise (i.e. L(g1) - L(g2) and L(g2) - L(g1) are
            not empty.
    """
    if vis is None:
        vis = DeterministicInclusionVisitor()
    try:
        parallel_breadth_first_search(g1, g2, vis = vis)
    except ContradictionException:
        return None
    return vis.ret
