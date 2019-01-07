#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>
#   Maxime Raynal     <maxime.raynal@nokia.com>

from pybgl.graph           import DirectedGraph, Graph, add_edge
from pybgl.graph_dp        import GraphDp
from pybgl.graph_traversal import DefaultTreeTraversalVisitor, dfs_tree, bfs_tree
from pybgl.property_map    import ReadWritePropertyMap, make_assoc_property_map

# This visitor marks for each visited vertex how many vertices have been seen so far.
class MyVisitor(DefaultTreeTraversalVisitor):
    def __init__(self, pmap_order :ReadWritePropertyMap):
        super(MyVisitor, self).__init__()
        self.m_last_index = 0
        self.m_pmap_order = pmap_order

    def discover_vertex(self, u :int, g :Graph):
        print("discover_vertex %s" % u)
        self.m_pmap_order[u] = self.m_last_index
        self.m_last_index += 1

def make_binary_tree(n = 10):
    g = DirectedGraph(n)
    for u in range(n - 1):
        add_edge(int(u / 2), u + 1, g)
    return g

def test_bfs_tree():
    map_order = dict()
    pmap_order = make_assoc_property_map(map_order)
    g = make_binary_tree(10)
    vis = MyVisitor(pmap_order)
    bfs_tree(0, g, vis)
    assert map_order == {
        0 : 0,
        1 : 1,
        2 : 2,
        3 : 3,
        4 : 4,
        5 : 5,
        6 : 6,
        7 : 7,
        8 : 8,
        9 : 9,
    }

def test_dfs_tree():
    map_order = dict()
    pmap_order = make_assoc_property_map(map_order)
    g = make_binary_tree(10)
    vis = MyVisitor(pmap_order)
    dfs_tree(0, g, vis)
    assert map_order == {
        0 : 0,
        1 : 4,
        2 : 1,
        3 : 7,
        4 : 5,
        5 : 3,
        6 : 2,
        7 : 9,
        8 : 8,
        9 : 6,
    }


