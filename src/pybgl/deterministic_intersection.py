#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .automaton import BOTTOM, Automaton, EdgeDescriptor
from .parallel_breadth_first_search import (
    ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search
)
from .product_mixin import ProductMixin

class DeterministicIntersectionVisitor(ParallelBreadthFirstSearchVisitor, ProductMixin):
    """
    The :py:class:`DeterministicIntersectionVisitor` class is used
    to implement the :py:func:`deterministic_intersection` function.
    """
    def __init__(self, g12 :Automaton):
        """
        Constructor.

        Args:
            g12 (Automaton): Pass an empty automaton, that will contain
                in the end the intersection automaton.
        """
        super().__init__(g12, lambda a, b: a and b)

    def examine_edge(
        self,
        e1: EdgeDescriptor,
        g1: Automaton,
        e2: EdgeDescriptor,
        g2: Automaton,
        a: str
    ):
        """
        Method invoked when examining a pair of transitions for the first time.

        Args:
            e1 (int): A transition of ``g1``.
            g1 (Automaton): The automaton corresponding to left operand of the intersection.
            e2 (int): A transition of ``g2``.
            g2 (Automaton): The automaton corresponding to right operand of the intersection.
            a (str): The symbol that labels ``e1`` and ``e2``.
        """
        if g1.target(e1) is not BOTTOM and g2.target(e2) is not BOTTOM:
            self.add_product_edge(e1, g1, e2, g2)

def deterministic_intersection(
    g1: Automaton,
    g2: Automaton,
    g12: Automaton = None,
    vis: DeterministicIntersectionVisitor = None
):
    """
    Computes the deterministic intersection of two deterministic finite automata.

    Args:
        g1 (Automaton): The left operand of the deterministic intersection.
        g1 (Automaton): The right operand of the deterministic intersection.
        g12 (Automaton): The output automata. Pass an empty automaton.
            In the end, it will be the intersection automaton.
        vis (DeterministicIntersectionVisitor): An optional visitor.
    """
    if not g12:
        g12 = Automaton()
    if not vis:
        vis = DeterministicIntersectionVisitor(g12)
    parallel_breadth_first_search(
        g1, g2, vis = vis,
        if_push = lambda e1, g1, e2, g2: (
            e1 is not None and g1.target(e1) and
            e2 is not None and g2.target(e2)
        )
    )
    return g12


