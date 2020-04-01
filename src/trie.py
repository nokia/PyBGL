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

from pybgl.automaton import \
    BOTTOM, Automaton, DirectedGraph, EdgeDescriptor, \
    accepts, add_edge, add_vertex, add_edge, alphabet, delta, edge, edges, \
    is_initial, initial, is_final, is_finite, final, \
    num_edges, num_vertices, out_degree, out_edges, set_final, \
    remove_vertex, remove_edge, source, sigma, label, target, vertices
from pybgl.incidence_node_automaton import IncidenceNodeAutomaton
from pybgl.parallel_breadth_first_search import \
    WHITE, ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search
from pybgl.property_map import make_constant_property_map

class Trie(Automaton):
    def __init__(self, *args):
        super().__init__(num_vertices = 1, *args)

    def insert(self, x):
        # Optimization
        #if isinstance(x, str):
        #    from pybgl.digital_sequence import DigitalSequence
        #    x = DigitalSequence(x)
        if isinstance(x, str):
            trie_insert_string(self, x)
        else:
            trie_deterministic_fusion(self, x)

    def num_edges(self) -> int:
        # Optimization
        n = num_vertices(self)
        return n - 1 if n else 0

def delta_best_effort(g :Automaton, w :str) -> tuple:
    q = initial(g)
    if not w:
        return (q, 0)
    for (i, a) in enumerate(w):
        r = delta(q, a, g)
        if r is BOTTOM:
            return (q, i)
        q = r
    return (q, i + 1)

def trie_insert_string(g :Trie, w :str):
    (q, i) = delta_best_effort(g, w)
    for a in w[i:]:
        r = add_vertex(g)
        add_edge(q, r, a, g)
        q = r
    set_final(q, g)

class TrieDeterministicFusion(ParallelBreadthFirstSearchVisitor):
    def __init__(self):
        self.map_q2_q1 = dict()

    def start_vertex(self, q01 :int, g1 :Trie, q02 :int, g2 :Trie):
        self.map_q2_q1[q02] = q01
        if is_final(q02, g2):
            set_final(q01, g1)

    def examine_edge(self, e1 :EdgeDescriptor, g1 :Trie, e2 :EdgeDescriptor, g2 :Trie, a :chr):
        r2 = target(e2, g2) if e2 else BOTTOM
        if e1 is None or target(e1, g1) is BOTTOM:
            if e1 is None: # new arc, disconnect from the original g1
                q1 = self.map_q2_q1[source(e2, g2)]
            elif target(e1, g1) is BOTTOM: # new arc, connected to the original g1
                q1 = source(e1, g1)
            r1 = add_vertex(g1)
            self.map_q2_q1[r2] = r1
            add_edge(q1, r1, a, g1)
        else:
            r1 = target(e1, g1)
        if r2 is not BOTTOM and is_final(r2, g2):
            set_final(r1, g1)

def trie_deterministic_fusion(g1 :Trie, g2 :Trie):
    parallel_breadth_first_search(
        g1, g2,
        vis = TrieDeterministicFusion(),
        if_push = lambda e1, g1, e2, g2: e2 is not None,
        pmap_vcolor = make_constant_property_map(WHITE)
    )

def incidence_node_automaton_insert_string(
        g: IncidenceNodeAutomaton, w: str
) -> int:
    if num_vertices(g) == 0:
        g.add_vertex(None)
    (q, i) = delta_best_effort(g, w)
    for a in w[i:]:
        r = g.add_vertex(a)
        g.add_edge(q, r)
        q = r
    set_final(q, g)
    return q
