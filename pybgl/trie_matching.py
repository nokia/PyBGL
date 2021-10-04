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

from pybgl.trie import Trie, is_final
from pybgl.parallel_breadth_first_search import \
    ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search

class TrieMatchingVisitor(ParallelBreadthFirstSearchVisitor):
    def __init__(self):
        self.counters = [0, 0, 0, 0]
    def update(self, q1 :int, g1 :Trie, q2 :int, g2 :Trie):
        i = 1 * int(is_final(q1, g1)) + 2 * int(is_final(q2, g2))
        self.counters[i] += 1
    def start_vertex(self, s1 :int, g1 :Trie, s2 :int, g2 :Trie):
        self.update(s1, g1, s2, g2)
    def discover_vertex(self, s1 :int, g1 :Trie, s2 :int, g2 :Trie):
        self.update(s1, g1, s2, g2)

def trie_matching(
    g1 :Trie,
    g2 :Trie,
    if_push = lambda e1, g1, e2, g2: True,
    vis :TrieMatchingVisitor= None
) -> list:
    if vis is None: vis = TrieMatchingVisitor()
    parallel_breadth_first_search(g1, g2, vis = vis, if_push = if_push)
    return vis.counters
