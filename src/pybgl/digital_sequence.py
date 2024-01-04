#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

# from .graph import in_degree, in_edges
from .trie import *
# from .trie import BOTTOM, EdgeDescriptor, Trie,


ERR_STRING_IMMUTABLE = "A string is immutable"


class DigitalSequence(Trie):
    """
    The :py:class:`DigitalSequence` wraps a string to make it compabible with
    any function of ``pybgl`` that applies to a :py:class:`Trie` instance
    (and hence to a :py:class:`Automaton` instance).
    """
    def __init__(self, w: str):
        """
        Constructor.

        Args:
            w (str): The wrapped string.
        """
        self.directed = True
        self.w = w

    def alphabet(self) -> set:
        # Overloaded method
        return {a for a in self.w}

    def delta(self, q: int, a: str):
        # Overloaded method
        return (
            q + 1 if (
                q is not BOTTOM
                and not is_final(q, self)
                and self.w[q] == a
            )
            else BOTTOM
        )

    def add_edge(self, *args):
        # Overloaded method
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def add_vertex(self, *args):
        # Overloaded method
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def in_edges(self, q: int) -> iter:
        # Overloaded method
        return (
            set() if self.is_initial(q)
            else {EdgeDescriptor(q - 1, q, self.w[q - 1])}
        )

    def out_edges(self, q: int) -> iter:
        # Overloaded
        return (
            set() if self.is_final(q)
            else {EdgeDescriptor(q, q + 1, self.w[q])}
        )

    def remove_edge(self, *args):
        # Overloaded
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def remove_vertex(self, *args):
        # Overloaded
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def sigma(self, q: int) -> iter:
        # Overloaded
        return set() if q is BOTTOM or self.is_final(q) else {self.w[q]}

    def edges(self) -> iter:
        # Overloaded
        return (
            EdgeDescriptor(q, q + 1, self.w[q])
            for q in range(len(self.w))
        )

    def vertices(self) -> iter:
        # Overloaded
        return range(len(self.w) + 1)

    def num_vertices(self) -> int:
        # Overloaded
        return len(self.w) + 1

    def num_edges(self) -> int:
        # Overloaded
        return len(self.w)

    def set_initial(self):
        # Overloaded
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def initial(self) -> int:
        # Overloaded
        return 0

    def is_initial(self, q) -> bool:
        # Overloaded
        return q == 0

    def set_final(self):
        # Overloaded
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def is_final(self, q: int) -> bool:
        # Overloaded
        return q == len(self.w)

    def insert(self, w: str):
        # Overloaded
        raise RuntimeError(ERR_STRING_IMMUTABLE)
