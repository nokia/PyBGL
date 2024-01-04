#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .automaton import *
# from .automaton import (
#     BOTTOM,
#     Automaton,
#     EdgeDescriptor,
#     automaton_insert_string,
# )
from .parallel_breadth_first_search import (
    ParallelBreadthFirstSearchVisitor,
    parallel_breadth_first_search
)
from .property_map import make_assoc_property_map


class Trie(Automaton):
    """
    A `trie <https://en.wikipedia.org/wiki/Trie>`__ is, also called
    digital tree or prefix tree, is a type of k-ary search tree, a
    tree data structure used for locating specific keys from within a set.

    The :py:class:`Trie` specializes the :py:class:`Automaton` class for trees.
    """
    def __init__(self, *args, **kwargs):
        # Overloaded constructor
        num_vertices = kwargs.pop("num_vertices", 1)
        super().__init__(*args, num_vertices=num_vertices, **kwargs)

    def insert(self, x: object):
        """
        Args:
            x (str or Trie): A :py:class:`str` or a :py:class:`Trie` instance,
                inserted in this :py:class:`Trie` instance.
        """
        if isinstance(x, str):
            automaton_insert_string(self, x)
        else:
            trie_deterministic_fusion(self, x)

    def num_edges(self) -> int:
        # Overloaded method
        # Optimization
        n = self.num_vertices()
        return n - 1 if n else 0


class TrieDeterministicFusion(ParallelBreadthFirstSearchVisitor):
    """
    The :py:class:`TrieDeterministicFusion` is used to implement
    the :py:func:`trie_deterministic_fusion` function.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.map_q2_q1 = dict()

    def start_vertex(self, q01: int, g1: Trie, q02: int, g2: Trie):
        # Overloaded method
        self.map_q2_q1[q02] = q01
        if g2.is_final(q02):
            g1.set_final(q01)

    def examine_edge(
        self,
        e1: EdgeDescriptor,
        g1: Trie,
        e2: EdgeDescriptor,
        g2: Trie,
        a: str
    ):
        # Overloaded method
        r2 = g2.target(e2) if e2 else BOTTOM
        if e1 is None or g1.target(e1) is BOTTOM:
            q1 = None
            if e1 is None:
                # New arc, disconnected from the original g1
                q1 = self.map_q2_q1[g2.source(e2)]
            elif g1.target(e1) is BOTTOM:
                # New arc, connected to the original g1
                q1 = g1.source(e1)
            assert q1 is not None
            r1 = g1.add_vertex()
            self.map_q2_q1[r2] = r1
            g1.add_edge(q1, r1, a)
        else:
            r1 = g1.target(e1)
        if r2 is not BOTTOM and g2.is_final(r2):
            g1.set_final(r1)


def trie_deterministic_fusion(g1: Trie, g2: Trie):
    """
    Merges two :py:class:`Trie` instance. The first instance is
    updated in place.

    Args:
        g1 (Trie): The first :py:class:`Trie` instance, modified
            in place.
        g2 (Trie): The second :py:class:`Trie` instance (unmodified).
    """
    parallel_breadth_first_search(
        g1, g2,
        vis=TrieDeterministicFusion(),
        if_push=lambda e1, g1, e2, g2: e2 is not None,
        pmap_vcolor=make_assoc_property_map(defaultdict(int))
    )
