#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import deque, defaultdict
from .graph import Graph, EdgeDescriptor
from .graph_traversal import WHITE, GRAY, BLACK
from .property_map import ReadWritePropertyMap, make_assoc_property_map


class DefaultDepthFirstSearchVisitor:
    """
    The :py:class:`DefaultDepthFirstSearchVisitor` class is the base class
    for any visitor that can be passed to the
    :py:func:`depth_first_search` and
    :py:func:`depth_first_search_graph` functions.
    """
    def initialize_vertex(self, u: int, g: Graph):
        """
        Method invoked on every vertex before the start of the search

        Args:
            u (int): The vertex being initialized.
            g (Graph): The considered graph.
        """
        pass

    def start_vertex(self, s: int, g: Graph):
        """
        Method invoked on the source vertex once before the start of
        the search.

        Args:
            s (int): The source vertex.
            g (Graph): The considered graph.
        """
        pass

    def discover_vertex(self, u: int, g: Graph):
        """
        Method invoked when a vertex is encountered for the first time.

        Args:
            u (int): The vertex being discovered.
            g (Graph): The considered graph.
        """
        pass

    def examine_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked on every out-edge of each vertex after it is discovered.

        Args:
            e (EdgeDescriptor): The edge being examined.
            g (Graph): The considered graph.
        """
        pass

    def tree_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked on each edge as it becomes a member of the edges that
        form the search tree. If you wish to record predecessors, do so at this
        event point.

        Args:
            e (EdgeDescriptor): The considered tree edge.
            g (Graph): The considered graph.
        """
        pass

    def back_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked on the back edges in the graph.

        Args:
            e (EdgeDescriptor): The considered back edge.
            g (Graph): The considered graph.
        """
        pass

    def forward_or_cross_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked on forward or cross edges in the graph.
        In an undirected graph this method is never called.

        Args:
            e (EdgeDescriptor): The considered edge.
            g (Graph): The considered graph.
        """
        pass

    def finish_vertex(self, u: int, g: Graph):
        """
        Method invoked on a vertex after all of its out edges have been
        added to the search tree and all of the adjacent vertices have
        been discovered (but before their out-edges have been examined).

        Args:
            u (int): The vertex being finished.
            g (Graph): The considered graph.
        """
        pass


def depth_first_search(
    s: int,
    g: Graph,
    pmap_vcolor: ReadWritePropertyMap = None,
    vis: DefaultDepthFirstSearchVisitor = None,
    # N.B: The following parameters does not exist in libboost:
    if_push: callable = None
):
    """
    Non-recursive implementation of the
    `Depth First Search <https://en.wikipedia.org/wiki/Depth-first_search>`__
    algorithm, from a single source.

    Based on `depth_first_search.hpp
    <https://www.boost.org/doc/libs/1_67_0/libs/graph/doc/depth_first_search.html>`__,
    by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek

    Args:
        s (int): The vertex descriptor of the source vertex.
        g (Graph): The graph being explored.
        pmap_vcolor (ReadWritePropertyMap): A property map that maps each
            vertex with its current color (:py:data:`WHITE`, :py:data:`GRAY`
            or :py:data:`BLACK`)
        vis (DefaultBreadthFirstSearchVisitor): An optional visitor.
        if_push (callable): A `callback(e, g) -> bool` where ``e`` is
            an arc of ``g`` that returns ``True`` if and only if the arc
            ``e`` is relevant.
            This is a legacy parameter. You should rather consider
            to filter the irrelevant arcs using the :py:class:`GraphView`
            class.
    """
    if pmap_vcolor is None:
        map_vcolor = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(map_vcolor)
    if vis is None:
        vis = DefaultDepthFirstSearchVisitor()
    if if_push is None:
        if_push = (lambda e, g: True)

    vis.start_vertex(s, g)
    pmap_vcolor[s] = GRAY
    vis.discover_vertex(s, g)
    u_edges = [e for e in g.out_edges(s) if if_push(e, g)]
    stack = deque([(s, 0, len(u_edges))])

    while stack:
        # Pop the current vertex u. Its (i-1)-th first out-edges have already
        # been visited. The out-degree of u is equal to n.
        (u, i, n) = stack.pop()
        u_edges = [e for e in g.out_edges(u) if if_push(e, g)]

        while i != n:
            # e is the current edge.
            e = u_edges[i]
            v = g.target(e)
            vis.examine_edge(e, g)
            color_v = pmap_vcolor[v]

            # (color[v] == WHITE) means that v has not yet been visited.
            if color_v == WHITE:
                # u must be re-examined later, its i-th out-edge
                # has been visited.
                vis.tree_edge(e, g)
                i += 1
                stack.append((u, i, n))

                # v becomes the new current vertex
                u = v
                pmap_vcolor[u] = GRAY
                vis.discover_vertex(u, g)
                u_edges = [e for e in g.out_edges(u) if if_push(e, g)]
                i = 0
                n = len(u_edges)
            else:
                if color_v == GRAY:
                    vis.back_edge(e, g)
                else:
                    vis.forward_or_cross_edge(e, g)
                i += 1

        # u and all the vertices reachable from u have been visited.
        pmap_vcolor[u] = BLACK
        vis.finish_vertex(u, g)


# N.B: The following function is also named depth_first_search in boost.
def depth_first_search_graph(
    g: Graph,
    sources: iter = None,
    pmap_vcolor: ReadWritePropertyMap = None,
    vis: DefaultDepthFirstSearchVisitor = None,
    if_push: bool = None
):
    """
    Non-recursive implementation of the
    `Depth First Search <https://en.wikipedia.org/wiki/Depth-first_search>`__
    algorithm, from multiple sources.

    Based on `depth_first_search.hpp
    <https://www.boost.org/doc/libs/1_67_0/libs/graph/doc/depth_first_search.html>`__,
    by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek

    Args:
        g (Graph): The graph being explored.
        sources (iter): An iterable over the sources, e.g., ``g.vertices()``.
        pmap_vcolor (ReadWritePropertyMap): A property map that maps
            each vertex with its current color (:py:data:`WHITE`,
            :py:data:`GRAY` or :py:data:`BLACK`)
        vis (DefaultBreadthFirstSearchVisitor): An optional visitor.
        if_push (callable): A `callback(e, g) -> bool` where ``e`` is the
            an arc of ``g`` that returns ``True`` if and only if the arc
            ``e`` is relevant.
            This is a legacy parameter. You should rather consider
            to filter the irrelevant arcs using the :py:class:`GraphView`
            class.
    """
    if pmap_vcolor is None:
        map_vcolor = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(map_vcolor)
    for u in (sources if sources else g.vertices()):
        if pmap_vcolor[u] == WHITE:
            depth_first_search(u, g, pmap_vcolor, vis, if_push)
