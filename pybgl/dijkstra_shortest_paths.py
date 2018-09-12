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
from pybgl.graph           import Graph, edges, target, out_edges, vertices
from pybgl.graph_traversal import DefaultBFSVisitor, WHITE, GRAY, BLACK
from pybgl.property_map    import ReadPropertyMap, ReadWritePropertyMap, get, make_assoc_property_map, put

# TODO should be based on pybgl.breadth_first_search

class DijkstraVisitor(DefaultBFSVisitor):
    pass

def dijkstra_shortest_paths(
    g           :Graph,
    s           :int,
    vis         :DijkstraVisitor,
    pmap_weight :ReadPropertyMap,
    pmap_pred   :ReadWritePropertyMap,
    pmap_dist   :ReadWritePropertyMap,
    zero        = 0,
    infty       = sys.maxsize
):
    color = dict()
    pmap_color = make_assoc_property_map(color) # WHITE: not yet processed, GRAY: under process, BLACK: processed.

    for u in vertices(g):
        put(pmap_dist, u, zero if u == s else infty)
        put(pmap_pred, u, set())
        put(pmap_color, u, GRAY if u == s else WHITE)

    stack = set([s])
    while stack:
        u = min(stack, key = lambda u : get(pmap_dist, u))
        stack.remove(u)
        w_su = get(pmap_dist, u)

        # Update weight and predecessors of each successor of u
        for e in out_edges(u, g):
            v = target(e, g)
            w_sv = get(pmap_dist, v)
            w_uv = get(pmap_weight, e)
            if w_su + w_uv < w_sv: # Traversing u is worth!
                put(pmap_dist, v, w_su + w_uv)
                put(pmap_pred, v, {e})
                if get(pmap_color, v) == WHITE:
                    put(pmap_color, v, GRAY)
                    stack.add(v)
            elif w_su + w_uv == w_sv:
                pred_v = get(pmap_pred, v)
                pred_v.add(e)
                put(pmap_pred, v, pred_v)
        put(pmap_color, u, BLACK)

