#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from pybgl.automaton import BOTTOM, Automaton, EdgeDescriptor


class ProductMixin:
    """
    The :py:class:`ProductMixin` is used to factorize the code
    in any binary set operation involving two automata.

    See also:

    - the :py:class:`DeterministicIntersectionVisitor` class;
    - the :py:class:`DeterministicUnionVisitor` class.
    """
    def __init__(self, g12: Automaton, operator):
        """
        Constructor.

        Args:
            g12 (Automaton): The output automaton.
            operator: The considered operator.
        """
        self.map_product_vertices = dict()
        self.g12 = g12
        self.operator = operator

    def add_product_vertex(
        self,
        q1: int,
        g1: Automaton,
        q2: int,
        g2: Automaton
    ) -> int:
        """
        Creates (and keeps track of) a state in the product
        automaton.
        ``q1`` and ``q2`` should never be simultaneously ``None``.

        Args:
            q1 (int): A state in ``g1`` or ``None``.
            g1 (Automaton): The left operand.
            q2 (int): A state in ``g2`` or ``None``.
            g1 (Automaton): The right operand.

        Returns:
            The newly created state in the product automaton,
            i.e. ``self.g12``.
        """
        q12 = self.g12.add_vertex()
        if self.operator(g1.is_initial(q1), g2.is_initial(q2)):
            self.g12.set_initial(q12)
        if self.operator(g1.is_final(q1), g2.is_final(q2)):
            self.g12.set_final(q12)
        self.map_product_vertices[(q1, q2)] = q12
        return q12

    def add_product_edge(
        self,
        e1: EdgeDescriptor,
        g1: Automaton,
        e2: EdgeDescriptor,
        g2: Automaton
    ):
        """
        Creates (and keeps track of) a transition in the product
        automaton.

        Args:
            e1 (EdgeDescriptor): A transition in ``g1`` or ``None``.
            g1 (Automaton): The left operand.
            e2 (EdgeDescriptor): A transition in ``g2`` or ``None``.
            g1 (Automaton): The right operand.

        Returns:
            The newly created state in the product automaton,
            i.e. ``self.g12``.
        """
        if e1:
            q1 = g1.source(e1)
            r1 = g1.target(e1)
            a = g1.label(e1)
        else:
            q1 = r1 = BOTTOM

        if e2:
            q2 = g2.source(e2)
            r2 = g2.target(e2)
            a = g2.label(e2)
        else:
            q2 = r2 = BOTTOM

        q12 = self.get_or_create_product_vertex(q1, g1, q2, g2)
        r12 = self.get_or_create_product_vertex(r1, g1, r2, g2)
        return self.g12.add_edge(q12, r12, a)

    def get_product_vertex(self, q1: int, q2: int) -> int:
        """
        Retrieves a vertex in the product automaton according
        to two (optional) states involved in the left and right
        operands.

        Args:
            q1 (int): A state of the left operand or ``None``.
            q2 (int): A state of the right operand or ``None``.

        Returns:
            The corresponding state in ``self.g12`` if any,
            ``None`` otherwise.
        """
        return self.map_product_vertices.get((q1, q2))

    def get_or_create_product_vertex(
        self,
        q1: int,
        g1: Automaton,
        q2: int,
        g2: Automaton
    ) -> int:
        """
        Creates (and keeps track of) a state in the product
        automaton, if needed.

        Args:
            e1 (EdgeDescriptor): A transition in ``g1`` or ``None``.
            g1 (Automaton): The left operand.
            e2 (EdgeDescriptor): A transition in ``g2`` or ``None``.
            g1 (Automaton): The right operand.

        Returns:
            The newly created state in the product automaton,
            i.e. ``self.g12``.
        """
        if q1 is BOTTOM and q2 is BOTTOM:
            raise RuntimeError("Tried to create (BOTTOM, BOTTOM) state.")
        q12 = self.get_product_vertex(q1, q2)
        if q12 is None:
            q12 = self.add_product_vertex(q1, g1, q2, g2)
        return q12
