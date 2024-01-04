#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import deque
from .graph import Graph, EdgeDescriptor


# If you use AssociativePropertyMap you are encouraged to wrap
# a defaultdict(int)
WHITE = 0
GRAY = 1
BLACK = 2


class DefaultTreeTraversalVisitor:
    def discover_vertex(self, u: int, g: Graph):
        """
        Method invoked when a vertex is encountered for the first time.

        Args:
            u (int): The vertex being discovered.
            g (Graph): The considered tree.
        """
        pass

    def examine_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked on every out-edge of each vertex after it is discovered.

        Args:
            e (EdgeDescriptor): The edge being examined.
            g (Graph): The considered tree.
        """
        pass

    def start_vertex(self, s: int, g: Graph):
        """
        Method invoked on the source vertex once before the start of
        the search.

        Args:
            s (int): The source vertex.
            g (Graph): The considered tree.
        """
        pass

    def finish_vertex(self, u: int, g: Graph):
        """
        Method invoked on a vertex after all of its out edges have been
        added to the search tree and all of the adjacent vertices have
        been discovered (but before their out-edges have been examined).

        Args:
            u (int): The vertex being finished.
            g (Graph): The considered tree.
        """
        pass


def dfs_tree(
    s: int,
    g: Graph,
    vis: DefaultTreeTraversalVisitor = None
):
    """
    Simplified implementation Depth First Search algorithm for trees
    See also :py:func:`depth_first_search`.

    Args:
        s (int): The vertex descriptor of the source.
        g (Graph): The graph being explored.
        vis (DefaultTreeTraversalVisitor): An optional visitor.
    """
    if vis is None:
        vis = DefaultTreeTraversalVisitor()
    vis.start_vertex(s, g)
    stack = deque([s])
    while stack:
        u = stack.pop()
        vis.discover_vertex(u, g)
        for e in g.out_edges(u):
            vis.examine_edge(e, g)
            v = g.target(e)
            stack.append(v)
        vis.finish_vertex(u, g)


def bfs_tree(
    s: int,
    g: Graph,
    vis: DefaultTreeTraversalVisitor = None
):
    """
    Simplified implementation Breadth First Search algorithm for trees
    See also :py:func:`breadth_first_search`.

    Args:
        s (int): The vertex descriptor of the source.
        g (Graph): The graph being explored.
        vis (DefaultTreeTraversalVisitor): An optional visitor.
    """
    if vis is None:
        vis = DefaultTreeTraversalVisitor()
    vis.start_vertex(s, g)
    stack = deque([s])
    while stack:
        u = stack.pop()
        vis.discover_vertex(u, g)
        for e in g.out_edges(u):
            vis.examine_edge(e, g)
            v = g.target(e)
            stack.appendleft(v)
        vis.finish_vertex(u, g)
