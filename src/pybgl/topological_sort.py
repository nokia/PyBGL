#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict, deque
from .graph import DirectedGraph, EdgeDescriptor
from .depth_first_search import (
    DefaultDepthFirstSearchVisitor,
    depth_first_search_graph,
)
from .property_map import make_assoc_property_map


class TopologicalSortVisitor(DefaultDepthFirstSearchVisitor):
    def __init__(self, stack):
        """
        Constructor.

        Args:
            stack (deque): The stack used to compute the topological sorting.
        """
        super().__init__()
        self.stack = stack

    def back_edge(self, e: EdgeDescriptor, g: DirectedGraph):
        raise RuntimeError("Not a DAG")

    def finish_vertex(self, u: int, g: DirectedGraph):
        self.stack.appendleft(u)


def topological_sort(g: DirectedGraph, stack: deque = None) -> deque:
    """
    Computes a
    `topological sorting <https://en.wikipedia.org/wiki/Topological_sorting>`__
    of a graph.
    The implementation is based on
    `boost/graph/topological_sort.hpp
    <https://www.boost.org/doc/libs/1_72_0/boost/graph/topological_sort.hpp>`__.

    Args:
        g (DirectedGraph): The input graph. It must be a
            `DAG <https://en.wikipedia.org/wiki/Directed_acyclic_graph>`.
        stack (deque): The stack used to store the topological sort,
            updated in place.
            You may pass ``None`` to use the default stack.

    Returns:
        The stack containing the vertices, sorted by topological order.
    """
    stack = stack if stack else deque()
    depth_first_search_graph(
        g,
        pmap_vcolor=make_assoc_property_map(defaultdict(int)),
        vis=TopologicalSortVisitor(stack)
    )
    return stack
