#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict, deque
from .automaton import BOTTOM, Automaton, EdgeDescriptor
from .graph_traversal import WHITE, GRAY, BLACK
from .property_map import ReadWritePropertyMap, make_assoc_property_map

class ParallelBreadthFirstSearchVisitor:
    """
    The :py:class:`ParallelBreadthFirstSearchVisitor` class is the base class
    for any visitor that can be passed to the
    :py:func:`parallel_breadth_first_search` function.
    """

    def start_vertex(self, s1: int, g1: Automaton, s2: int, g2: Automaton):
        """
        Method invoked when the pair of initial states is pushed to the queue.

        Args:
            q1 (int): The vertex descriptor of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            q2 (int): The vertex descriptor of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
        """

        pass

    def examine_vertex(self, q1: int, g1: Automaton, q2: int, g2: Automaton):
        """
        Method invoked for each pair of vertices as it is removed from the queue.

        Args:
            q1 (int): The vertex descriptor of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            q2 (int): The vertex descriptor of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
        """
        pass

    def discover_vertex(self, q1: int, g1: Automaton, q2: int, g2: Automaton):
        """
        Method invoked the first time the algorithm encounters ``(q1, q2)`` pair.

        Args:
            q1 (int): The vertex descriptor of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            q2 (int): The vertex descriptor of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
        """
        pass

    def finish_vertex(self, q1: int, g1: Automaton, q2: int, g2: Automaton):
        """
        Method invoked after all of the out-transitions of ``q1`` and ``q2`` have been
        examined and all of the adjacent vertices have been discovered.

        Args:
            q1 (int): The vertex descriptor of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            q2 (int): The vertex descriptor of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
        """
        pass

    def examine_symbol(self, q1: int, g1: Automaton, q2: int, g2: Automaton, a: str):
        """
        Method invoked when discovering a symbol ``a`` when examining
        the ``(q1, q2)`` pair.

        Args:
            q1 (int): The vertex descriptor of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            q2 (int): The vertex descriptor of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
        """

        pass

    def examine_edge(
        self,
        e1: EdgeDescriptor,
        g1: Automaton,
        e2: EdgeDescriptor,
        g2: Automaton,
        a: str
    ):
        """
        Method invoked invoked on every out-edge of each pair of states
        immediately after the vertex is removed from the queue.

        Args:
            e1 (int): The processed transition of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            e2 (int): The processed transition of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
            a (str): The label of ``e1`` (if not ``None``) and ``e2``
                (if not ``None``).
        """
        pass

    def tree_edge(
        self,
        e1: EdgeDescriptor,
        g1: Automaton,
        e2: EdgeDescriptor,
        g2: Automaton,
        a: str
    ):
        """
        Method invoked to (in addition to
        :py:meth:`ParallelBreadthFirstSearchVisitor.tree_edge`)
        if ``(e1, e2)`` is a tree edge of the product automaton ``(g1, g2)``.
        The ``(r1, r2)`` target vertex of edge the ``a``-transition
        is discovered at this time.

        Args:
            e1 (int): The processed transition of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            e2 (int): The processed transition of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
            a (str): The label of ``e1`` (if not ``None``) and ``e2``
                (if not ``None``).
        """
        pass

    def gray_target(
        self,
        e1: EdgeDescriptor,
        g1: Automaton,
        e2: EdgeDescriptor,
        g2: Automaton,
        a: str
    ):
        """
        Method invoked
        if the target vertex is colored :py:data:`GRAY` at the time
        of examination. The color :py:data:`GRAY` indicates
        that the vertex is currently in the queue.

        Args:
            e1 (int): The processed transition of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            e2 (int): The processed transition of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
            a (str): The label of ``e1`` (if not ``None``) and ``e2``
                (if not ``None``).
        """
        pass

    def black_target(
        self,
        e1: EdgeDescriptor,
        g1: Automaton,
        e2: EdgeDescriptor,
        g2: Automaton,
        a: str
    ):
        """
        Method invoked (in addition to
        :py:meth:`DefaultBreadthFirstSearchVisitor.non_tree_edge`)
        if the target vertex is colored :py:data:`BLACK` at the time
        of examination. The color :py:data:`BLACK` indicates that
        the vertex is no longer in the queue.

        Args:
            e1 (int): The processed transition of ``g1`` if any,
                ``None`` otherwise .
            g1 (Automaton): The first automaton.
            e2 (int): The processed transition of ``g2`` if any,
                ``None`` otherwise .
            g2 (Automaton): The second automaton.
            a (str): The label of ``e1`` (if not ``None``) and ``e2``
                (if not ``None``).
        """
        pass

def parallel_breadth_first_search(
    g1: Automaton,
    g2: Automaton,
    source_pairs = None,
    pmap_vcolor: ReadWritePropertyMap = None,
    vis: ParallelBreadthFirstSearchVisitor = None,
    if_push: callable = None
):
    """
    Non-recursive implementation of Depth First Search algorithm, from multiple sources.
    Based on `Boost breadth_first_search <https://www.boost.org/doc/libs/1_62_0/libs/graph/doc/breadth_first_search.html>`__,
    by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek.

    Args:
        g1 (Automaton): The first automaton.
        g2 (Automaton): The second automaton.
        source_pairs (iter): An iterable over the pairs of source sattes.
            `Example:` ``[(g1.initial(), g2.initial())]``.
        pmap_vcolor (ReadWritePropertyMap): A property map that maps each vertex
            with its current color (:py:data:`WHITE`, :py:data:`GRAY`
            or :py:data:`BLACK`)
        vis (ParallelBreadthFirstSearchVisitor): An optional visitor.
        if_push (callable): A `callback(e1, g1, e2, g2) -> bool` where ``e1`` is
            an arc of ``g`` that returns ``True`` if and only if the pair
            ``(e1, e2)`` is relevant.
    """
    def get_edge(q, r, a, g):
        assert q is not None
        # It may be useful to consider (q, BOTTOM, a), see parallel_walk algorithm and tree_edge
        # assert r is not None
        return (
            EdgeDescriptor(q, r, a) if q is not None and r == g.delta(q, a)
            else EdgeDescriptor(q, BOTTOM, a)
        )

    stack = deque()

    if vis is None:
        vis = ParallelBreadthFirstSearchVisitor()
    if source_pairs is None:
        q01 = g1.initial()
        q02 = g2.initial()
        stack.appendleft((q01, q02))
        vis.start_vertex(q01, g1, q02, g2)
    else:
        for (s1, s2) in source_pairs:
            stack.appendleft((s1, s2))
            vis.start_vertex(s1, g1, s2, g2)

    if not pmap_vcolor:
        map_vcolor = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(map_vcolor)

    if not if_push:
        if_push = (lambda e1, g1, e2, g2: True)

    while stack:
        (q1, q2) = stack.pop()
        vis.examine_vertex(q1, g1, q2, g2)
        for a in g1.sigma(q1) | g2.sigma(q2):
            (r1, r2) = (g1.delta(q1, a), g2.delta(q2, a))
            vis.examine_symbol(q1, g1, q2, g2, a)
            e1 = get_edge(q1, r1, a, g1) if q1 is not BOTTOM else None
            e2 = get_edge(q2, r2, a, g2) if q2 is not BOTTOM else None
            vis.examine_edge(e1, g1, e2, g2, a)
            color = pmap_vcolor[(r1, r2)]
            if color == WHITE:
                vis.tree_edge(e1, g1, e2, g2, a)
                pmap_vcolor[(r1, r2)] = GRAY
                vis.discover_vertex(r1, g1, r2, g2)
                if if_push(e1, g1, e2, g2):
                    stack.appendleft((r1, r2))
            elif color == GRAY:
                vis.gray_target(e1, g1, e2, g2, a)
            else:
                vis.black_target(e1, g1, e2, g2, a)
        pmap_vcolor[(q1, q2)] = BLACK
        vis.finish_vertex(q1, g2, q2, g2)
