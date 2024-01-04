#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .automaton import Automaton, EdgeDescriptor
from .parallel_breadth_first_search import (
    ParallelBreadthFirstSearchVisitor,
    parallel_breadth_first_search,
)
from .product_mixin import ProductMixin


class DeterministicUnionVisitor(
    ParallelBreadthFirstSearchVisitor,
    ProductMixin
):
    """
    The :py:class:`DeterministicUnionVisitor` class is used
    to implement the :py:func:`deterministic_union` function.
    """
    def __init__(self, g12: Automaton):
        """
        Constructor.

        Args:
            g12 (Automaton): Pass an empty automaton, that will contain
                in the end the union automaton.
        """
        super().__init__(g12, lambda a, b: a or b)

    def examine_edge(
        self,
        e1: EdgeDescriptor,
        g1: Automaton,
        e2: EdgeDescriptor,
        g2: Automaton,
        a: str
    ):
        """
        Method invoked when examining a pair of transitions for
        the first time.

        Args:
            e1 (int): A transition of ``g1``.
            g1 (Automaton): The automaton corresponding to left operand
                of the union.
            e2 (int): A transition of ``g2``.
            g2 (Automaton): The automaton corresponding to right operand
                of the union.
            a (str): The symbol that labels ``e1`` and ``e2``.
        """
        self.add_product_edge(e1, g1, e2, g2)


def deterministic_union(
    g1: Automaton,
    g2: Automaton,
    g12: Automaton = None,
    vis: DeterministicUnionVisitor = None
):
    """
    Computes the deterministic union of two deterministic finite automata.

    Args:
        g1 (Automaton): The left operand of the deterministic union.
        g1 (Automaton): The right operand of the deterministic union.
        g12 (Automaton): The output automata. Pass an empty automaton.
            In the end, it will be the union automaton.
        vis (DeterministicUnionVisitor): An optional visitor.
    """

    if not g12:
        g12 = Automaton()
    if not vis:
        vis = DeterministicUnionVisitor(g12)
    parallel_breadth_first_search(g1, g2, vis=vis)
    return g12
