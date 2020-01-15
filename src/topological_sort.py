#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl
#
# Based on
# https://www.boost.org/doc/libs/1_72_0/boost/graph/topological_sort.hpp

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from collections              import defaultdict, deque
from pybgl.graph              import DirectedGraph, EdgeDescriptor, add_edge
from pybgl.depth_first_search import DefaultDepthFirstSearchVisitor, depth_first_search_graph
from pybgl.property_map       import make_assoc_property_map

class TopoSortVisitor(DefaultDepthFirstSearchVisitor):
    def __init__(self, stack):
        self.stack = stack
    def back_edge(self, e :EdgeDescriptor, g :DirectedGraph):
        raise RuntimeError("Not a DAG")
    def finish_vertex(self, u :int, g :DirectedGraph):
        self.stack.appendleft(u)

def topological_sort(g :DirectedGraph, stack :deque = None) -> deque:
    stack = stack if stack else deque()
    depth_first_search_graph(
        g,
        pmap_vcolor = make_assoc_property_map(defaultdict(int)),
        vis = TopoSortVisitor(stack)
    )
    return stack
