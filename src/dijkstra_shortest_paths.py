#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

import sys
from collections                import defaultdict
from pybgl.algebra              import BinaryFunction, BinaryPredicate, Less, ClosedPlus
from pybgl.breadth_first_search import DefaultBreadthFirstSearchVisitor
from pybgl.graph                import DirectedGraph, edges, target, out_edges, vertices
from pybgl.graph_traversal      import WHITE, GRAY, BLACK
from pybgl.property_map         import ReadPropertyMap, ReadWritePropertyMap, identity_property_map, get, make_assoc_property_map, put

class DijkstraVisitor(DefaultBreadthFirstSearchVisitor):
    # TODO: adapt this visitor to conform to BGL dijkstra_shortest_paths default visitor.
    pass

# Remark:
# Contrary to BGL implementation, we map each vertex with its incident arc*s*
# in the shortest path "tree". This allows to manage parallel arcs and equally
# cost shortest path.

def dijkstra_shortest_paths(
    g            :DirectedGraph,
    s            :int,
    pmap_eweight :ReadPropertyMap,
    pmap_vpreds  :ReadWritePropertyMap,
    pmap_vdist   :ReadWritePropertyMap,
    compare      :BinaryPredicate = Less(),
    combine      :BinaryFunction  = ClosedPlus(),
    zero         :int = 0,
    infty        :int = sys.maxsize,
    vis          :DijkstraVisitor = DijkstraVisitor()
):
    """
    Compute the shortest path in a graph from a given source node.
    Args:
        g: A DirectedGraph instance.
        s: The vertex descriptor of the source node.
        pmap_eweight: A ReadPropertyMap{EdgeDescriptor : Distance}
            which map each edge with its weight.
        pmap_vpreds: A ReadWritePropertyMap{VertexDescriptor : EdgeDescriptor}
            which will map each vertex with its incident arcs in the shortest
            path Directed Acyclic Graph.
        pmap_vdist: A ReadWritePropertyMap{VertexDescriptor : Distance}
            which will map each vertex with the weight of its shortest path(s)
            from s.
        zero: The null Distance (e.g. 0).
        infty: The infinite Distance (e.g. sys.maxsize).
        vis: A DijkstraVisitor instance.

    Example:
        g = DirectedGraph(2)
        e, _ = add_edge(0, 1, g)
        map_eweight[e] = 10
        map_vpreds = defaultdict(set)
        map_vdist = dict()
        dijkstra_shortest_paths(
            g, u,
            make_assoc_property_map(map_eweight),
            make_assoc_property_map(map_vpreds),
            make_assoc_property_map(map_vdist)
        )
    """
    # WHITE: not yet processed, GRAY: under process, BLACK: processed.
    color = defaultdict(int)
    pmap_vcolor = make_assoc_property_map(color)
    pmap_vcolor[s] = WHITE

    for u in vertices(g):
        pmap_vdist[u]   = zero if u == s else infty
        #pmap_vpreds[u] = set()
        #pmap_vcolor[u]  = GRAY if u == s else WHITE

    stack = {s}
    while stack:
        u = min(stack, key = lambda u : pmap_vdist[u]) # TODO use compare
        stack.remove(u)
        w_su = pmap_vdist[u]

        # Update weight and predecessors of each successor of u
        for e in out_edges(u, g):
            v = target(e, g)
            w_sv = pmap_vdist[v]
            w_uv = pmap_eweight[e]
            w = combine(w_su, w_uv)
            if compare(w, w_sv): # Traversing u is worth!
                pmap_vdist[v] = w
                pmap_vpreds[v] = {e}
                if pmap_vcolor[v] == WHITE:
                    pmap_vcolor[v] = GRAY
                    stack.add(v)
            elif w == w_sv: # Hence we discover equally-cost shortest paths
                preds_v = pmap_vpreds[v]
                preds_v.add(e)
                pmap_vpreds[v] = preds_v
        pmap_vcolor[u] = BLACK

