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
from pybgl.graph                import Graph, EdgeDescriptor, source, target
from pybgl.depth_first_search   import WHITE, DefaultDepthFirstSearchVisitor, depth_first_search
from pybgl.property_map         import make_assoc_property_map

def cut(s :int, g :Graph, in_cut) -> set:
    """
    Find a vertex cut given an edge cut.
    Args:
        g: A `Graph` instance corresponding to an acyclic graph.
        s: The `VertexDescriptor` corresponding to the source vertex.
        in_cut: `Callback(EdgeDescriptor, Graph) -> bool` indicating whether an
            edge belong to the considered cut.
    """
    class LeavesVisitor(DefaultDepthFirstSearchVisitor):
        def __init__(self, leaves :set):
            self.leaves = leaves
        def examine_edge(self, e :EdgeDescriptor, g :Graph):
            u = source(e, g)
            self.leaves.discard(u)
        def discover_vertex(self, u :int, g :Graph):
            self.leaves.add(u)

    class IfPush:
        def __init__(self, in_cut, cutting_edges :set):
            self.in_cut = in_cut
            self.cutting_edges = cutting_edges
        def __call__(self, e :EdgeDescriptor, g :Graph) -> bool:
            is_cutting_edge = self.in_cut(e, g)
            if is_cutting_edge:
                self.cutting_edges.add(e)
            return not is_cutting_edge

    leaves = set()
    cutting_edges = set()
    map_vcolor = defaultdict(int)
    depth_first_search(
        s, g,
        pmap_vcolor = make_assoc_property_map(map_vcolor),
        vis = LeavesVisitor(leaves),
        if_push = IfPush(in_cut, cutting_edges)
    )
    return {target(e, g) for e in cutting_edges} | {u for u in leaves} - {source(e, g) for e in cutting_edges}

