#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from pybgl.graph                import DirectedGraph, Graph, EdgeDescriptor, add_edge, vertices
from pybgl.breadth_first_search import BLACK, DefaultBreadthFirstSearchVisitor, breadth_first_search
from pybgl.property_map         import make_assoc_property_map

class MyBreadthFirstSearchVisitor(DefaultBreadthFirstSearchVisitor):
    def examine_vertex(self, u :int, g :Graph):
        print("discover %s" % u)
    def examine_edge(self, e :EdgeDescriptor, g :Graph):
        print("examine %s" % e)
    def finish_vertex(self, u :int, g :Graph):
        print("finish %s" % u)

# Graph1
g1 = DirectedGraph(7)
add_edge(0, 1, g1)
add_edge(1, 2, g1)
add_edge(2, 3, g1)
add_edge(3, 1, g1)
add_edge(3, 4, g1)
add_edge(4, 5, g1)
add_edge(5, 6, g1)
add_edge(6, 4, g1)

# Graph2
g2 = DirectedGraph(4)
add_edge(0, 1, g2)
add_edge(1, 2, g2)
add_edge(1, 3, g2)
add_edge(3, 0, g2)
add_edge(3, 2, g2)

vis = MyBreadthFirstSearchVisitor()

for (i, g) in enumerate([g1, g2]):
    print("Processing G%s" % i)
    map_color = dict()
    breadth_first_search(0, g, make_assoc_property_map(map_color), vis)

    # As our graph are connected, the color of each vertices should be BLACK
    for u in vertices(g):
        assert map_color[u] == BLACK
