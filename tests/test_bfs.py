#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>
#   Maxime Raynal     <maxime.raynal@nokia.com>

from collections           import deque
from pybgl.graph           import EdgeDescriptor, DirectedGraph, out_edges, target, Graph, add_edge, vertices
from pybgl.graph_traversal import DefaultBFSVisitor, bfs, init_pmap_color
from pybgl.property_map    import ReadWritePropertyMap, get, make_assoc_property_map, put

class MyBFSVisitor(DefaultBFSVisitor):
    def __init__(self, pmap_order :ReadWritePropertyMap):
        super(MyBFSVisitor, self).__init__()
        self.m_last_index = 0
        self.m_pmap_order = pmap_order

    def visit_node(self, u :int, g :Graph):
        put(self.m_pmap_order, u, self.m_last_index)
        self.m_last_index += 1


# Build a binary tree of 10 nodes
n = 10
g = DirectedGraph(n)
for u in range(n-1):
    add_edge(int(u / 2), u + 1, g)
    if u % 3 == 0:
        add_edge(u, u, g)
    if u % 4 == 0 and u >= 4:
        add_edge(u, u - 4, g)

# Prepare pmap
dorder = dict()
dcolor = dict()
pmap_color = make_assoc_property_map(dcolor)
pmap_order = make_assoc_property_map(dorder)

init_pmap_color(pmap_color, g)
bfs(0, g, pmap_color, MyBFSVisitor(pmap_order))
print(type(pmap_order))
for u in vertices(g):
    print("Vertex %s : labeled %s with BFS" % (u, pmap_order.get(u)))
