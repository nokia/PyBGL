#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import deque, defaultdict
from .graph import Graph, EdgeDescriptor
from .graph_traversal import WHITE, GRAY, BLACK
from .property_map import ReadWritePropertyMap, make_assoc_property_map

class DefaultBreadthFirstSearchVisitor:
    """
    The :py:class:`DefaultBreadthFirstSearchVisitor` class is the base class
    for any visitor that can be passed to the
    :py:func:`breadth_first_search` and
    :py:func:`breadth_first_search_graph` functions.
    """
    def initialize_vertex(self, u: int, g: Graph):
        """
        Method invoked on every vertex before the start of the search

        Args:
            u (int): The vertex being initialized.
            g (Graph): The considered graph.
        """
        pass

    def examine_vertex(self, u: int, g: Graph):
        """
        Method invoked for each vertex as it is removed from the queue.

        Args:
            u (int): The vertex being examined.
            g (Graph): The considered graph.
        """
        pass

    def examine_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked invoked on every out-edge of each vertex
        immediately after the vertex is removed from the queue.

        Args:
            e (EdgeDescriptor): The edge being examined.
            g (Graph): The considered graph.
        """
        pass

    def tree_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked (in addition to
        :py:meth:`DefaultBreadthFirstSearchVisitor.examine_edge`)
        if the edge is a tree edge.
        The target vertex of edge ``e`` is discovered at this time.

        Args:
            e (EdgeDescriptor): The considered tree edge.
            g (Graph): The considered graph.
        """
        pass

    def discover_vertex(self, u: int, g: Graph):
        """
        Method invoked the first time the algorithm encounters vertex ``u``.
        All vertices closer to the source vertex have been discovered,
        and vertices further from the source have not yet been discovered.

        Args:
            u (int): The vertex being discovered.
            g (Graph): The considered graph.
        """
        pass

    def non_tree_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked (in addition to
        py:meth:`DefaultBreadthFirstSearchVisitor.examine_edge`)
        if the edge is not a tree edge.

        Args:
            e (EdgeDescriptor): The considered non-tree edge.
            g (Graph): The considered graph.
        """
        pass

    def gray_target(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked (in addition to
        :py:meth:`DefaultBreadthFirstSearchVisitor.non_tree_edge`)
        if the target vertex is colored :py:data:`GRAY` at the time
        of examination. The color :py:data:`GRAY` indicates
        that the vertex is currently in the queue.

        Args:
            e (EdgeDescriptor): The considered non-tree edge, pointing
                to a :py:data:`GRAY` vertex.
            g (Graph): The considered graph.
        """
        pass

    def black_target(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked (in addition to
        :py:meth:`DefaultBreadthFirstSearchVisitor.non_tree_edge`)
        if the target vertex is colored :py:data:`BLACK` at the time
        of examination. The color :py:data:`BLACK` indicates that
        the vertex is no longer in the queue.

        Args:
            e (EdgeDescriptor): The considered non-tree edge, pointing
                to a :py:data:`BLACK` vertex.
            g (Graph): The considered graph.
        """
        pass

    def finish_vertex(self, u: int, g: Graph):
        """
        Method invoked after all of the out-edges of ``u`` have been
        examined and all of the adjacent vertices have been discovered.

        Args:
            u (int): The vertex being finished.
            g (Graph): The considered graph.
        """
        pass

def breadth_first_search_graph(
    g: Graph,
    sources: iter = None,
    pmap_vcolor: ReadWritePropertyMap = None,
    vis: DefaultBreadthFirstSearchVisitor = None,
    # N.B: The following parameter does not exist in libboost.
    if_push: callable = None
):
    """
    Non-recursive implementation of the
    `Breadth First Search <https://en.wikipedia.org/wiki/Breadth-first_search>`__
    algorithm, from multiple sources.

    Based on `Boost breadth_first_search <https://www.boost.org/doc/libs/1_62_0/libs/graph/doc/breadth_first_search.html>`__,
    by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek.

    Args:
        g (Graph): The graph being explored.
        sources (iter): An iterable over the source vertices.
            `Example:` ``g.vertices()``.
        pmap_vcolor (ReadWritePropertyMap): A property map that maps each vertex
            with its current color (:py:data:`WHITE`, :py:data:`GRAY`
            or :py:data:`BLACK`)
        vis (DefaultBreadthFirstSearchVisitor): An optional visitor.
        if_push (callable): A `callback(e, g) -> bool` where ``e`` is
            an arc of ``g`` that returns ``True`` if and only if the arc
            ``e`` is relevant.
            This is a legacy parameter. You should rather consider
            to filter the irrelevant arcs using the :py:class:`GraphView` class.
    """
    if pmap_vcolor is None:
        map_vcolor = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(map_vcolor)
    if vis is None:
        vis = DefaultBreadthFirstSearchVisitor()
    if not if_push:
        if_push = (lambda e, g: True)

    stack = deque()
    for s in sources:
        pmap_vcolor[s] = GRAY
        vis.discover_vertex(s, g)
        stack.append(s)

    while stack:
        u = stack.pop()
        vis.examine_vertex(u, g)
        for e in g.out_edges(u):
            if not if_push(e, g):
                continue
            v = g.target(e)
            vis.examine_edge(e, g)
            color_v = pmap_vcolor[v]
            if color_v == WHITE:
                vis.tree_edge(e, g)
                pmap_vcolor[v] = GRAY
                vis.discover_vertex(v, g)
                stack.appendleft(v)
            else:
                vis.non_tree_edge(e, g)
                if color_v == GRAY:
                    vis.gray_target(e, g)
                else:
                    vis.black_target(e, g)
        pmap_vcolor[u] = BLACK
        vis.finish_vertex(u, g)

def breadth_first_search(
    s: int,
    g: Graph,
    pmap_vcolor: ReadWritePropertyMap = None,
    vis: DefaultBreadthFirstSearchVisitor = None,
    # N.B: The following parameters doe not exists in libboost:
    if_push: callable = None
):
    """
    Non-recursive implementation of the
    `Breadth First Search <https://en.wikipedia.org/wiki/Breadth-first_search>`__,
    algorithm from a single source.

    Based on `Boost breadth_first_search <https://www.boost.org/doc/libs/1_62_0/libs/graph/doc/breadth_first_search.html>`__
    by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek.

    Args:
        g (Graph): The graph being explored.
        s (int): The vertex descriptor of the source.
        pmap_vcolor (ReadWritePropertyMap): A property map that maps each vertex
            with its current color (:py:data:`WHITE`, :py:data:`GRAY`
            or :py:data:`BLACK`)
        vis (DefaultBreadthFirstSearchVisitor): An optional visitor.
        if_push (callable): A `callback(e, g) -> bool` where ``e`` is the
            an arc of ``g`` that returns ``True`` if and only if the arc
            ``e`` is relevant.
            This is a legacy parameter. You should rather consider
            to filter the irrelevant arcs using the :py:class:`GraphView` class.
    """
    if pmap_vcolor is None:
        map_vcolor = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(map_vcolor)
    for u in g.vertices():
        vis.initialize_vertex(u, g)
        pmap_vcolor[u] = WHITE
    breadth_first_search_graph(g, {s}, pmap_vcolor, vis, if_push)
