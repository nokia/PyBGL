#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Non-recursive implementation of Depth First Search algorithm.
#
# Based on http://www.boost.org/doc/libs/1_61_0/boost/graph/depth_first_search.hpp by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from collections           import deque, defaultdict
from pybgl.graph           import Graph, EdgeDescriptor, out_edges, target, vertices
from pybgl.graph_traversal import WHITE, GRAY, BLACK
from pybgl.property_map    import ReadWritePropertyMap, make_assoc_property_map

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# /!\ DO NOT MODIFY THIS FILE
# It conforms to http://www.boost.org/doc/libs/1_61_0/libs/graph/doc/depth_first_search.html
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class DefaultDepthFirstSearchVisitor():
    def __init__(self): super().__init__()
    def start_vertex(self, s :int, g :Graph): pass
    def discover_vertex(self, u :int, g :Graph): pass
    def examine_edge(self, e :EdgeDescriptor, g :Graph): pass
    def tree_edge(self, e :EdgeDescriptor, g :Graph): pass
    def back_edge(self, e :EdgeDescriptor, g :Graph): pass
    def forward_or_cross_edge(self, e :EdgeDescriptor, g :Graph): pass
    def finish_vertex(self, u :int, g :Graph): pass

def depth_first_search(
    s :int,
    g :Graph,
    pmap_vcolor :ReadWritePropertyMap = None,
    vis         :DefaultDepthFirstSearchVisitor = None,
    # N.B: The following parameters does not exist in libboost:
    if_push     = None # if_push(e :EdgeDecriptor, g :Graph) -> bool returns True iff e is relevant
):
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
    u_edges = [e for e in out_edges(s, g) if if_push(e, g)]
    stack = deque([(s, 0, len(u_edges))])

    while stack:
        # Pop the current vertex u. Its (i-1)-th first out-edges have already
        # been visited. The out-degree of u is equal to n.
        (u, i, n) = stack.pop()
        u_edges = [e for e in out_edges(u, g) if if_push(e, g)]

        while i != n:
            # e is the current edge.
            e = u_edges[i]
            v = target(e, g)
            vis.examine_edge(e, g)
            color_v = pmap_vcolor[v]

            # (color[v] == WHITE) means that v has not yet been visited.
            if color_v == WHITE:
                # u must be re-examined later, its i-th out-edge has been visited.
                vis.tree_edge(e, g)
                i += 1
                stack.append((u, i, n))

                # v becomes the new current vertex
                u = v
                pmap_vcolor[u] = GRAY
                vis.discover_vertex(u, g)
                u_edges = [e for e in out_edges(u, g) if if_push(e, g)]
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
    g           :Graph,
    sources     :set = None, # Or a generator e.g. vertices(g)
    pmap_vcolor :ReadWritePropertyMap = None,
    vis         :DefaultDepthFirstSearchVisitor = None,
    if_push     :bool = None # if_push(e :EdgeDecriptor) -> bool
):
    if pmap_vcolor is None:
        map_vcolor = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(map_vcolor)
    for u in (sources if sources else vertices(g)):
        if pmap_vcolor[u] == WHITE:
            depth_first_search(u, g, pmap_vcolor, vis, if_push)

