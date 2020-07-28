#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Class allowing to aggregate a list of compatible visitors
# into a single visitor.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from collections                import defaultdict
from pybgl.breadth_first_search import DefaultBreadthFirstSearchVisitor, breadth_first_search_graph
from pybgl.depth_first_search   import DefaultDepthFirstSearchVisitor, depth_first_search_graph
from pybgl.property_map         import make_assoc_property_map
from pybgl.graph                import DirectedGraph, EdgeDescriptor, source, target

class CutMixin:
    """
    Mixin used to find the cut in a acyclic Graph.
    The cut is characterized by the `if_push` parameter of the graph traversal algorithm.
    See `pybgl.breadth_first_search` or `pybgl.depth_first_search`.
    """
    def __init__(self, roots :list):
        """
        Constructor.
        Args:
            roots: `list` of roots of the graph.
        """
        self.cut = {u for u in roots}

    def examine_edge(self, e :EdgeDescriptor, g :DirectedGraph):
        """
        Examine edge event.
        Args:
            e: `EdgeDescriptor` instance corresponding to the current edge.
            g: `DirectedGraph` instance corresponding to considered graph.
        """
        u = source(e, g)
        v = target(e, g)
        if u in self.cut:
            self.cut.remove(u)
        self.cut.add(v)

class BfsCutVisitor(CutMixin, DefaultBreadthFirstSearchVisitor):
    def __init__(self, roots :list):
        super().__init__(roots)

class DfsCutVisitor(CutMixin, DefaultDepthFirstSearchVisitor):
    def __init__(self, roots :list):
        super().__init__(roots)

def bfs_cut(g :DirectedGraph, sources :set, if_push) -> set:
    """
    Search a cut in a acyclic Graph.
    Args:
        sources: `Iterable(int)` gathering sources of the graph where to start the BFS traversal.
        if_push: `Callback(EdgeDescriptor, DirectedGraph) -> bool` indicating
            whether a edge is relevant in the considered graph.
        g: `DirectedGraph` instance corresponding to considered dendrogram.
    Returns:
        The `set(int)` of gathering the vertices involved in the cut.
    """
    vis = BfsCutVisitor(sources)
    breadth_first_search_graph(
        g,
        sources,
        vis = vis,
        if_push = if_push
    )
    return vis.cut

def dfs_cut(g :DirectedGraph, sources :set, if_push) -> set:
    """
    Search a cut in a acyclic Graph.
    Args:
        sources: `Iterable(int)` gathering sources of the graph where to start the DFS traversal.
        if_push: `Callback(EdgeDescriptor, DirectedGraph) -> bool` indicating
            whether a edge is relevant in the considered graph.
        g: `DirectedGraph` instance corresponding to considered dendrogram.
    Returns:
        The `set(int)` of gathering the vertices involved in the cut.
    """
    vis = DfsCutVisitor(sources)
    depth_first_search_graph(
        g,
        sources,
        vis = vis,
        if_push = if_push
    )
    return vis.cut
