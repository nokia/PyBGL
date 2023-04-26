#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .trie import Trie
from .parallel_breadth_first_search import (
    ParallelBreadthFirstSearchVisitor, parallel_breadth_first_search
)

class TrieMatchingVisitor(ParallelBreadthFirstSearchVisitor):
    """
    The :py:class:`TrieMatchingVisitor` is used to implement
    the :py:func:`trie_matching` function.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.counters = [
            0,  # Number of prefixes not recognized by g1 and g2.
            0,  # Number of prefixes recognized by g1, but not g2.
            0,  # Number of prefixes recognized by g2, but not g1.
            0   # Number of prefixes recognized by g1 and g2.
        ]

    def update(self, q1: int, g1: Trie, q2: int, g2: Trie):
        """
        Internal method, used to update :py:attr:`self.counters`.
        """
        i = 1 * int(g1.is_final(q1)) + 2 * int(g2.is_final(q2))
        self.counters[i] += 1

    def start_vertex(self, s1: int, g1: Trie, s2: int, g2: Trie):
        """
        Overloads the
        :py:meth:`ParallelBreadthFirstSearchVisitor.start_vertex` method.
        """
        self.update(s1, g1, s2, g2)

    def discover_vertex(self, s1: int, g1: Trie, s2: int, g2: Trie):
        """
        Overloads the
        :py:meth:`ParallelBreadthFirstSearchVisitor.discover_vertex` method.
        """
        self.update(s1, g1, s2, g2)

def trie_matching(
    g1: Trie,
    g2: Trie,
    vis: TrieMatchingVisitor= None
) -> list:
    """
    Checks how two :py:class:`Trie` instances overlap.
    If you want to restrict which parts of ``g1`` and ``g2`` must be
    explored, see the :py:class:`GraphView` class.

    Args:
        g1 (Trie): The first :py:class:`Trie` instance.
        g2 (Trie): The second :py:class:`Trie` instance.
        vis (TrieMatchingVisitor): An optional visitor
    """
    if vis is None:
        vis = TrieMatchingVisitor()
    parallel_breadth_first_search(g1, g2, vis=vis)
    return vis.counters
