#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict, deque
from .algebra import INFINITY
from .depth_first_search import (
    DefaultDepthFirstSearchVisitor,
    depth_first_search_graph,
)
from .graph import DirectedGraph
from .property_map import (
    ReadWritePropertyMap,
    make_assoc_property_map,
)


class TarjanVisitor(DefaultDepthFirstSearchVisitor):
    def __init__(
        self,
        pmap_component: ReadWritePropertyMap,
        pmap_root: ReadWritePropertyMap,
        pmap_discover_time: ReadWritePropertyMap,
        stack: deque
    ):
        """
        Constructor.

        Args:
            pmap_component (ReadWritePropertyMap):
                Map vertex with its component id
                Pass an empty property map.
            pmap_root (ReadWritePropertyMap):
                Map vertex with its root vertex
                Pass an empty property map.
            pmap_discover_time (ReadWritePropertyMap):
                Map vertex with its iteration number
                Pass an empty property map.
            stack (deque): Stack of visited vertices.
                Pass an empty stack.
        """
        # Number of strongly connected components
        self.total = 0
        self.pmap_component = pmap_component
        self.pmap_root = pmap_root
        self.pmap_discover_time = pmap_discover_time
        self.stack = stack
        # Iteration number
        self.dfs_time = 0

    def discover_vertex(self, u: int, g: DirectedGraph):
        # Overloaded method
        self.pmap_root[u] = u
        self.pmap_component[u] = INFINITY
        self.pmap_discover_time[u] = self.dfs_time
        self.dfs_time += 1
        self.stack.appendleft(u)

    def discover_min(self, u: int, v: int) -> int:
        """
        Determines which vertex has been discovered first.

        Args:
            u (int): A vertex descriptor.
            v (int): A vertex descriptor.

        Returns:
            ``u`` if ``u`` has been discovered before ``v``,
            ``v`` otherwise.
        """
        return (
            u if self.pmap_discover_time[u] < self.pmap_discover_time[v]
            else v
        )

    def finish_vertex(self, u: int, g: DirectedGraph):
        # Overloaded method
        for e in g.out_edges(u):
            v = g.target(e)
            if self.pmap_component[v] == INFINITY:
                # u is attached to the "lowest" root among the root of u and v
                self.pmap_root[u] = self.discover_min(
                    self.pmap_root[u],
                    self.pmap_root[v]
                )

        if self.pmap_root[u] == u:
            # The vertices stacked since u belong to the same component of u.
            while True:
                v = self.stack.popleft()
                self.pmap_component[v] = self.total
                self.pmap_root[v] = u
                if u == v:
                    break
            self.total += 1


def strong_components(
    g: DirectedGraph,
    pmap_component: ReadWritePropertyMap
) -> int:
    """
    Tarjan algorithm, used to discover in ``O(|V|+|E|)`` strongly connected
    component in an arbitrary directed graph.

    Based on the `boost implementation
    <http://www.boost.org/doc/libs/1_64_0/boost/graph/strong_components.hpp>`__
    by Andrew Lumsdaine, Lie-Quan Lee, Jeremy G. Siek

    Key ideas: Consider an arbitrary directed graph:

    - If each strongly connected component is collapsed in a single vertex, the
      graph is a lattice. It is thus possible to assign a component ID to each
      vertex such as this lattice orders the component ID.
    - If the graph is traversed using a DFS, once a vertex is finished, we can
      assign to it a component.
    - The ID assigned to a vertex is the number of strongly connected
      components discovered so far.
    - The deeper is a component, the higher will be its identifier. The lattice
      orders the component IDs according to ``>=``.

    Args:
        g (DirectedGraph): The input graph.
        pmap_component (ReadWritePropertyMap): The output property map that
            maps each vertex with its component ID (the vertices having the
            same component ID fall in the same strongly connected component).
    """
    map_vcolor = defaultdict(int)
    map_root = defaultdict(int)
    map_discover_time = defaultdict(int)

    pmap_vcolor = make_assoc_property_map(map_vcolor)
    pmap_root = make_assoc_property_map(map_root)
    pmap_discover_time = make_assoc_property_map(map_discover_time)

    stack = deque()
    vis = TarjanVisitor(
        pmap_component,
        pmap_root,
        pmap_discover_time,
        stack
    )

    depth_first_search_graph(g, g.vertices(), pmap_vcolor, vis, None)
    return vis.total
