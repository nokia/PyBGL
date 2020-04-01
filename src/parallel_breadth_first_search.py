#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from collections            import defaultdict, deque
from pybgl.automaton        import BOTTOM, Automaton, EdgeDescriptor, delta, initial, sigma
from pybgl.graph_traversal  import WHITE, GRAY, BLACK
from pybgl.property_map     import ReadWritePropertyMap, make_assoc_property_map

class ParallelBreadthFirstSearchVisitor:
    def start_vertex   (self, s1 :int, g1 :Automaton, s2 :int, g2 :Automaton): pass
    def examine_vertex (self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton): pass
    def discover_vertex(self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton): pass
    def finish_vertex  (self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton): pass
    def examine_symbol (self, q1 :int, g1 :Automaton, q2 :int, g2 :Automaton, a :chr): pass
    def examine_edge   (self, e1 :EdgeDescriptor, g1 :Automaton, e2 :EdgeDescriptor, g2 :Automaton, a :chr): pass
    def tree_edge      (self, e1 :EdgeDescriptor, g1 :Automaton, e2 :EdgeDescriptor, g2 :Automaton, a :chr): pass
    def gray_target    (self, e1 :EdgeDescriptor, g1 :Automaton, e2 :EdgeDescriptor, g2 :Automaton, a :chr): pass
    def black_target   (self, e1 :EdgeDescriptor, g1 :Automaton, e2 :EdgeDescriptor, g2 :Automaton, a :chr): pass

def parallel_breadth_first_search(
    g1 :Automaton,
    g2 :Automaton,
    source_pairs = None,
    pmap_vcolor :ReadWritePropertyMap = None,
    vis = ParallelBreadthFirstSearchVisitor(),
    if_push = None,
    delta = delta
):
    def get_edge(q, r, a, g):
        assert q is not None
        # It may be useful to consider (q, BOTTOM, a), see parallel_walk algorithm and tree_edge
        #assert r is not None
        return EdgeDescriptor(q, r, a) if q is not None and r == delta(q, a, g) else \
               EdgeDescriptor(q, BOTTOM, a)

    stack = deque()

    if source_pairs == None:
        q01 = initial(g1)
        q02 = initial(g2)
        stack.appendleft((q01, q02))
        vis.start_vertex(q01, g1, q02, g2)
    else:
        for (s1, s2) in source_pairs:
            stack.appendleft((s1, s2))
            vis.start_vertex(s1, g1, s2, g2)

    if not pmap_vcolor:
        map_vcolor = defaultdict(int)
        pmap_vcolor = make_assoc_property_map(map_vcolor)

    if not if_push:
        if_push = (lambda e1, g1, e2, g2: True)

    while stack:
        (q1, q2) = stack.pop()
        vis.examine_vertex(q1, g1, q2, g2)
        for a in sigma(q1, g1) | sigma(q2, g2):
            (r1, r2) = (delta(q1, a, g1), delta(q2, a, g2))
            vis.examine_symbol(q1, g1, q2, g2, a)
            e1 = get_edge(q1, r1, a, g1) if q1 is not BOTTOM else None
            e2 = get_edge(q2, r2, a, g2) if q2 is not BOTTOM else None
            vis.examine_edge(e1, g1, e2, g2, a)
            color = pmap_vcolor[(r1, r2)]
            if color == WHITE:
                vis.tree_edge(e1, g1, e2, g2, a)
                pmap_vcolor[(r1, r2)] = GRAY
                vis.discover_vertex(r1, g1, r2, g2)
                if if_push(e1, g1, e2, g2):
                    stack.appendleft((r1, r2))
            elif color == GRAY:
                vis.gray_target(e1, g1, e2, g2, a)
            else:
                vis.black_target(e1, g1, e2, g2, a)
        pmap_vcolor[(q1, q2)] = BLACK
        vis.finish_vertex(q1, g2, q2, g2)
