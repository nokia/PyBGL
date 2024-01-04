#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the PyBGL project.
# https://github.com/nokia/pybgl

from .automaton import Automaton
from .parallel_breadth_first_search import (
    ParallelBreadthFirstSearchVisitor,
    parallel_breadth_first_search,
)


class ContradictionException(RuntimeError):
    """
    Exception raised when an automaton cannot be included in another one.
    """
    pass


class DeterministicInclusionVisitor(ParallelBreadthFirstSearchVisitor):
    """
    The :py:class:`DeterministicInclusionVisitor` class is used
    to implement the :py:func:`deterministic_inclusion` function.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.ret = 0  # Status inclusion

    def update(self, q1: int, g1: Automaton, q2: int, g2: Automaton):
        """
        Internal method, invoked when processing a ``(q1, q2)`` pair of states.

        Args:
            q1 (int): A state of ``g1``.
            g1 (Automaton): The automaton corresponding to left operand of
                the inclusion.
            q2 (int): A state of ``g2``.
            g2 (Automaton): The automaton corresponding to right operand of
                the inclusion.
        """
        f1 = g1.is_final(q1)
        f2 = g2.is_final(q2)
        if f1 ^ f2:
            ret = 1 if f2 else -1
            if self.ret == 0:
                self.ret = ret
            elif self.ret != ret:
                raise ContradictionException()

    def start_vertex(self, s1: int, g1: Automaton, s2: int, g2: Automaton):
        """
        Method invoked when processing the initial pair of initial states.

        Args:
            s1 (int): A initial state of ``g1``.
            g1 (Automaton): The automaton corresponding to left operand of
                the inclusion.
            s2 (int): A initial of ``g2``.
            g2 (Automaton): The automaton corresponding to right operand
                of the inclusion.
        """
        self.update(s1, g1, s2, g2)

    def discover_vertex(self, q1: int, g1: Automaton, q2: int, g2: Automaton):
        """
        Method invoked when discovering the first time a ``(q1, q2)``
        pair of states.

        Args:
            q1 (int): A state of ``g1``.
            g1 (Automaton): The automaton corresponding to left operand
                of the inclusion.
            q2 (int): A state of ``g2``.
            g2 (Automaton): The automaton corresponding to right operand
                of the inclusion.
        """
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
        parallel_breadth_first_search(g1, g2, vis=vis)
    except ContradictionException:
        return None
    return vis.ret
