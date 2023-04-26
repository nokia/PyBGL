#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl.graph import (
    DirectedGraph, Graph, EdgeDescriptor, UndirectedGraph,
)
from pybgl.depth_first_search import (
    DefaultDepthFirstSearchVisitor, depth_first_search, BLACK
)
from pybgl.property_map import make_assoc_property_map

class MyDepthFirstSearchVisitor(DefaultDepthFirstSearchVisitor):
    def __init__(self, verbose: bool = False):
        self.num_vertices = 0
        self.num_edges = 0
        self.verbose = verbose

    def discover_vertex(self, u: int, g: Graph):
        if self.verbose: print("discover %s" % u)
        self.num_vertices += 1

    def examine_edge(self, e: EdgeDescriptor, g: Graph):
        if self.verbose: print("examine %s" % e)
        self.num_edges += 1

    def finish_vertex(self, u: int, g: Graph):
        if self.verbose: print("finish %s" % u)

def make_g1(directed: bool) -> Graph:
    g1 = DirectedGraph(7) if directed else UndirectedGraph(7)
    g1.add_edge(0, 1)
    g1.add_edge(1, 2)
    g1.add_edge(2, 3)
    g1.add_edge(3, 1)
    g1.add_edge(3, 4)
    g1.add_edge(4, 5)
    g1.add_edge(5, 6)
    g1.add_edge(6, 4)
    return g1

def make_g2(directed: bool) -> Graph:
    g2 = DirectedGraph(4) if directed else UndirectedGraph(4)
    g2.add_edge(0, 1)
    g2.add_edge(1, 2)
    g2.add_edge(1, 3)
    g2.add_edge(3, 0)
    g2.add_edge(3, 2)
    return g2

def test_all():
    for directed in [True, False]:
        for (i, g) in enumerate([make_g1(directed), make_g2(directed)]):
            print("Processing G%s (directed = %s)" % (i, directed))
            vis = MyDepthFirstSearchVisitor(verbose=False)
            map_color = defaultdict(int)
            depth_first_search(0, g, make_assoc_property_map(map_color), vis)

            n = g.num_vertices()
            m = g.num_edges()
            n_ = vis.num_vertices
            m_ = vis.num_edges

            # Our graph are connected, so these assertion should be verified
            assert n_ == n, "Visited %s/%s vertices" % (n_, n)
            if directed:
                assert m_ == m, "Visited %s/%s edges" % (m_, m)
            else:
                # Undirected edges are visited forward and backward, so they are visited "twice"
                # Not that (u -> u) arc would be only visited once.
                assert m_ == 2 * m, "Visited %s/%s edges" % (m_, m)

            # Finally, all vertices should all be BLACK
            for u in g.vertices():
                assert map_color[u] == BLACK
