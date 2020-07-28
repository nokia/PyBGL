#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Tarjan algorithm, used to discover in O(|V|+|E|) strongly connected
# component in an arbitrary directed graph.
#
# Based on http://www.boost.org/doc/libs/1_64_0/boost/graph/strong_components.hpp
# by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"


import sys
from collections                import defaultdict, deque

from pybgl.depth_first_search   import DefaultDepthFirstSearchVisitor, depth_first_search_graph
from pybgl.graph                import DirectedGraph, out_edges, target, vertices
from pybgl.graph_traversal      import WHITE
from pybgl.property_map         import ReadWritePropertyMap, make_assoc_property_map

INFINITY = sys.maxsize

# Key ideas: Consider an arbitrary directed graph.
# - If each strongly connected component is collapsed in a single vertex, the
#   graph is a lattice. It is thus possible to assign a component ID to each
#   vertex such as this lattice orders the component ID.
# - If the graph is traversed using a DFS, once a vertex is finished, we can
#   assign to it a component.
# - In Tarjan algorithm,
#    - the ID assigned to a vertex is the number of strongly connected components
#      discovered so far.
#    - the deeper is a component, the higher will be its identifier. The lattice
#      orders the component IDs according to >=.

class TarjanVisitor(DefaultDepthFirstSearchVisitor):
    def __init__(self,
        pmap_component,
        pmap_root,
        pmap_discover_time,
        stack
    ):
        self.m_total              = 0                  # Number of strongly connected components
        self.m_pmap_component     = pmap_component     # Map vertex with its component id
        self.m_pmap_root          = pmap_root          # Map vertex with its root vertex
        self.m_pmap_discover_time = pmap_discover_time # Map vertex with its iteration number
        self.m_stack              = stack              # Stack of visited vertices
        self.m_dfs_time           = 0                  # Iteration number

    @property
    def total(self) -> int:
        return self.m_total

    def discover_vertex(self, u :int, g :DirectedGraph):
        self.m_pmap_root[u] = u
        self.m_pmap_component[u] = INFINITY
        self.m_pmap_discover_time[u] = self.m_dfs_time
        self.m_dfs_time += 1
        self.m_stack.appendleft(u)

    def discover_min(self, u :int, v :int) -> int:
        return u if self.m_pmap_discover_time[u] < self.m_pmap_discover_time[v] else v

    def finish_vertex(self, u :int, g :DirectedGraph):
        for e in out_edges(u, g):
            v = target(e, g)
            if self.m_pmap_component[v] == INFINITY:
                # u is attached to the "lowest" root among the root of u and v
                self.m_pmap_root[u] = self.discover_min(
                    self.m_pmap_root[u],
                    self.m_pmap_root[v]
                )

        if self.m_pmap_root[u] == u:
            # The vertices stacked since u belong to the same component of u.
            while True:
                v = self.m_stack.popleft()
                self.m_pmap_component[v] = self.total
                self.m_pmap_root[v] = u
                if u == v: break
            self.m_total += 1

def strong_components(
    g :DirectedGraph,
    pmap_component :ReadWritePropertyMap
) -> int:
    map_vcolor        = defaultdict(int)
    map_root          = defaultdict(int)
    map_discover_time = defaultdict(int)

    pmap_vcolor        = make_assoc_property_map(map_vcolor)
    pmap_root          = make_assoc_property_map(map_root)
    pmap_discover_time = make_assoc_property_map(map_discover_time)

    stack = deque()
    vis = TarjanVisitor(
        pmap_component,
        pmap_root,
        pmap_discover_time,
        stack
    )

    depth_first_search_graph(g, vertices(g), pmap_vcolor, vis, None)
    return vis.total
