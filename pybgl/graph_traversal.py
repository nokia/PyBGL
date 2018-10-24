#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from collections    import deque
from .graph         import Graph, EdgeDescriptor, out_edges, target
from .property_map  import ReadWritePropertyMap

WHITE = 0 # If you use AssociativePropertyMap you are encouraged to wrap a defaultdict(int)
GRAY  = 1
BLACK = 2

class DefaultTreeTraversalVisitor:
    def __init__(self): pass
    def discover_vertex(self, u :int, g :Graph): pass
    def examine_edge(self, e :EdgeDescriptor, g :Graph): pass
    def start_vertex(self, s :int, g :Graph): pass
    def if_push(self, e :EdgeDescriptor, g :Graph) -> bool: return True
    def finish_vertex(self, u :int, g :Graph): pass

def dfs_tree(root, g :Graph, vis = DefaultTreeTraversalVisitor()):
    vis.start_vertex(root, g)
    stack = deque([root])
    while stack:
        u = stack.pop()
        vis.discover_vertex(u, g)
        for e in out_edges(u, g):
            vis.examine_edge(e, g)
            v = target(e, g)
            if vis.if_push(e, g) == True:
                stack.append(v)
        vis.finish_vertex(u, g)

def bfs_tree(root, g :Graph, vis = DefaultTreeTraversalVisitor()):
    vis.start_vertex(root, g)
    stack = deque([root])
    while stack:
        u = stack.pop()
        vis.discover_vertex(u, g)
        for e in out_edges(u, g):
            vis.examine_edge(e, g)
            v = target(e, g)
            if vis.if_push(e, g) == True:
                stack.appendleft(v)
        vis.finish_vertex(u, g)
