#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from pybgl.graph                import DirectedGraph, Graph, EdgeDescriptor, add_edge
from pybgl.depth_first_search   import DefaultDepthFirstSearchVisitor, depth_first_search
from pybgl.property_map         import make_assoc_property_map

class MyDepthFirstSearchVisitor(DefaultDepthFirstSearchVisitor):
    def discover_vertex(self, u :int, g :Graph):
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

vis = MyDepthFirstSearchVisitor()

for (i, g) in enumerate([g1, g2]):
    print("Processing G%s" % i)
    map_color = dict()
    depth_first_search(0, g, make_assoc_property_map(map_color), vis)

