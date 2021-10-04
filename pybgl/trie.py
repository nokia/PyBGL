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
    accepts, add_edge, add_vertex, add_edge, alphabet, \
    automaton_insert_string, delta, delta_best_effort, edge, edges, initial, \
    is_initial, initial, is_final, is_finite, finals, \
    num_edges, num_vertices, out_degree, out_edges, set_initial, set_final, \
    remove_vertex, remove_edge, source, sigma, label, target, vertices
from pybgl.parallel_breadth_first_search import \
    WHITE, ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search
from pybgl.property_map import make_constant_property_map

class Trie(Automaton):
    def __init__(self, *args):
        super().__init__(num_vertices = 1, *args)

    def insert(self, x):
        if isinstance(x, str):
            automaton_insert_string(self, x)
        else:
            trie_deterministic_fusion(self, x)

    def num_edges(self) -> int:
        # Optimization
        n = num_vertices(self)
        return n - 1 if n else 0

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
