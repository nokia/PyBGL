#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>
#   Maxime Raynal     <maxime.raynal@nokia.com>

from collections           import deque
from pybgl.graph           import EdgeDescriptor, DirectedGraph, out_edges, target, Graph, add_edge, vertices
from pybgl.graph_dp        import GraphDp
from pybgl.graph_traversal import DefaultTreeTraversalVisitor, dfs_tree, bfs_tree
from pybgl.property_map    import ReadWritePropertyMap, get, make_assoc_property_map, put

# Use it in a jupyter console or notebook to see the output (though graphviz)

# Build a binary tree of 10 nodes
n = 10
g = DirectedGraph(n)
for u in range(n-1):
    add_edge(int(u / 2), u + 1, g)

# This visitor marks for each visited vertex how many vertices have been seen so far.
class MyVisitor(DefaultTreeTraversalVisitor):
    def __init__(self, pmap_order :ReadWritePropertyMap):
        super(MyVisitor, self).__init__()
        self.m_last_index = 0
        self.m_pmap_order = pmap_order

    def visit_node(self, u :int, g :Graph):
        put(self.m_pmap_order, u, self.m_last_index)
        self.m_last_index += 1

# Call the traversal algorithms
dorder = dict()
pmap_order = make_assoc_property_map(dorder)

for (alg_name, alg) in [("BFS", bfs_tree), ("DFS", dfs_tree)]:
    vis = MyVisitor(pmap_order)
    alg(0, g, vis)
    gdp = GraphDp(g, {"label" : pmap_order}, {}, {"label" : alg_name})
    print(gdp.to_dot())
