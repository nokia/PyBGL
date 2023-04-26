#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .graph import Graph, EdgeDescriptor
from .depth_first_search import WHITE, DefaultDepthFirstSearchVisitor, depth_first_search
from .property_map import make_assoc_property_map

def cut(s: int, g: Graph, in_cut: callable) -> set:
    """
    Finds a vertex cut given an edge cut.

    Args:
        s (int): The `VertexDescriptor` corresponding to the source vertex.
        g (Graph): An acyclic graph.
        in_cut (callable): A ``Callback(EdgeDescriptor, Graph) -> bool``,
            indicating whether an edge belong to the considered cut.

    Returns:
        The set of vertices that are in the vertex cut.
    """
    class LeavesVisitor(DefaultDepthFirstSearchVisitor):
        def __init__(self, leaves: set):
            self.leaves = leaves
        def examine_edge(self, e: EdgeDescriptor, g: Graph):
            u = g.source(e)
            self.leaves.discard(u)
        def discover_vertex(self, u: int, g: Graph):
            self.leaves.add(u)

    class IfPush:
        def __init__(self, in_cut, cutting_edges: set):
            self.in_cut = in_cut
            self.cutting_edges = cutting_edges
        def __call__(self, e: EdgeDescriptor, g: Graph) -> bool:
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
    return {
        g.target(e)
        for e in cutting_edges
    } | {
        u for u in leaves
    } - {
        g.source(e)
        for e in cutting_edges
    }
