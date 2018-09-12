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

from .graph         import Graph, vertices, EdgeDescriptor, out_edges, target
from .property_map  import ReadWritePropertyMap, put, get

WHITE = None # Hence my_dict.get(u) returns WHITE if u has not been visited.
GRAY  = 1
BLACK = 2

def init_pmap_color(pmap_vcolor :ReadWritePropertyMap, g :Graph):
    for u in vertices(g):
        pmap_vcolor[u] = WHITE

class DefaultTreeTraversalVisitor:
    def __init__(self): pass
    def visit_node(self, u :int, g :Graph): pass # TODO should be renamed discover_vertex
    def examine_edge(self, e :EdgeDescriptor, g :Graph): pass
    def start_vertex(self, s :int, g :Graph): pass
    def if_push(self, e :EdgeDescriptor, g :Graph) -> bool: return True # This callback is now a parameter of pybgl.depth_first_search
    def finish_vertex(self, u :int, g :Graph): pass

class DefaultDFSVisitor(DefaultTreeTraversalVisitor):
    def __init__(self): super(DefaultDFSVisitor, self).__init__()
    def tree_edge(self, e :EdgeDescriptor, g :Graph): pass
    def back_edge(self, e :EdgeDescriptor, g :Graph): pass
    def forward_or_cross_edge(self, e :EdgeDescriptor, g :Graph): pass

def dfs(s :int, g :Graph, pmap_color :ReadWritePropertyMap, vis = DefaultDFSVisitor(), out_edges = out_edges, target = target, init_pmap = True):
    print("Obsolete, use pybgl.depth_first_search instead")
# The following do not really behaves like a normal DFS
#OBSOLETE|    if init_pmap == True:
#OBSOLETE|        init_pmap_color(pmap_color, g)
#OBSOLETE|    vis.start_vertex(s, g)
#OBSOLETE|    stack = deque([s])
#OBSOLETE|    while stack:
#OBSOLETE|        u = stack.pop()
#OBSOLETE|        pmap_color[u] = GRAY
#OBSOLETE|        vis.visit_node(u, g)
#OBSOLETE|        for e in out_edges(u, g):
#OBSOLETE|            v = target(e, g)
#OBSOLETE|            vis.examine_edge(e, g)
#OBSOLETE|            color_v = get(pmap_color, v)
#OBSOLETE|            if color_v == WHITE:
#OBSOLETE|                vis.tree_edge(e, g)
#OBSOLETE|                if vis.if_push(e, g) == True:
#OBSOLETE|                    stack.append(v)
#OBSOLETE|            elif color_v == GRAY:
#OBSOLETE|                vis.back_edge(e, g)
#OBSOLETE|            elif color_v == BLACK:
#OBSOLETE|                vis.forward_or_cross_edge(e, g)
#OBSOLETE|        pmap_color[u] = BLACK
#OBSOLETE|        vis.finish_vertex(u, g)

def dfs_tree(root, g :Graph, vis = DefaultTreeTraversalVisitor(), out_edges = out_edges, target = target):
    vis.start_vertex(root, g)
    stack = deque([root])
    while stack:
        u = stack.pop()
        vis.visit_node(u, g)
        for e in out_edges(u, g):
            vis.examine_edge(e, g)
            v = target(e, g)
            if vis.if_push(e, g) == True:
                stack.append(v)
        vis.finish_vertex(u, g)

# Used by pyfolcsr
class DefaultBFSVisitor(DefaultTreeTraversalVisitor):
    def __init__(self): super(DefaultBFSVisitor, self).__init__()
    def tree_edge(self, e :EdgeDescriptor, g :Graph): pass
    def gray_target(self, e :EdgeDescriptor, g :Graph): pass
    def black_target(self, e :EdgeDescriptor, g :Graph): pass
    def forward_or_cross_edge(self, e :EdgeDescriptor, g :Graph): pass

# Used by pyfolcsr (requires if_push)
def bfs(s :int, g :Graph, pmap_color :ReadWritePropertyMap, vis = DefaultBFSVisitor(), out_edges = out_edges, target = target, init_pmap = True):
    if init_pmap == True: init_pmap_color(pmap_color, g)
    vis.start_vertex(s, g)
    stack = deque([s])
    while stack:
        u = stack.pop()
        pmap_color[u] = GRAY
        vis.visit_node(u, g)
        for e in out_edges(u, g):
            v = target(e, g)
            vis.examine_edge(e, g)
            color_v = pmap_color[v]
            if color_v == WHITE: # v has not been visited yet
                vis.tree_edge(e, g)
                if vis.if_push(e, g) == True: # This test is the only difference with pybgl.breadth_first_search
                    stack.append(v)
            elif color_v == GRAY: # v == u
                vis.gray_target(e, g)
            elif color_v == BLACK: # v has already been visited
                vis.black_target(e, g)
        pmap_color[u] = BLACK
        vis.finish_vertex(u, g)

def bfs_tree(root, g :Graph, vis = DefaultTreeTraversalVisitor(), out_edges = out_edges, target = target):
    vis.start_vertex(root, g)
    stack = deque([root])
    while stack:
        u = stack.pop()
        vis.visit_node(u, g)
        for e in out_edges(u, g):
            vis.examine_edge(e, g)
            v = target(e, g)
            if vis.if_push(e, g) == True:
                stack.append(v)
        vis.finish_vertex(u, g)
