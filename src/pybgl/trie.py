#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .automaton import *
from .parallel_breadth_first_search import WHITE, ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search
from .property_map import make_assoc_property_map

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

    def start_vertex(self, q01: int, g1: Trie, q02: int, g2: Trie):
        self.map_q2_q1[q02] = q01
        if is_final(q02, g2):
            set_final(q01, g1)

    def examine_edge(self, e1: EdgeDescriptor, g1: Trie, e2: EdgeDescriptor, g2: Trie, a: chr):
        r2 = target(e2, g2) if e2 else BOTTOM
        if e1 is None or target(e1, g1) is BOTTOM:
            q1 = None
            if e1 is None: # new arc, disconnect from the original g1
                q1 = self.map_q2_q1[source(e2, g2)]
            elif target(e1, g1) is BOTTOM: # new arc, connected to the original g1
                q1 = source(e1, g1)
            assert q1 is not None
            r1 = add_vertex(g1)
            self.map_q2_q1[r2] = r1
            add_edge(q1, r1, a, g1)
        else:
            r1 = target(e1, g1)
        if r2 is not BOTTOM and is_final(r2, g2):
            set_final(r1, g1)

def trie_deterministic_fusion(g1: Trie, g2: Trie):
    parallel_breadth_first_search(
        g1, g2,
        vis = TrieDeterministicFusion(),
        if_push = lambda e1, g1, e2, g2: e2 is not None,
        pmap_vcolor = make_assoc_property_map(defaultdict(int))
    )
