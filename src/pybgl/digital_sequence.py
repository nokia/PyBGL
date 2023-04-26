#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .graph import in_degree, in_edges
from .trie import (
    BOTTOM, EdgeDescriptor, Trie,
    accepts, alphabet, delta, edge, edges,
    is_initial, initial, is_final, is_finite, finals,
    num_edges, num_vertices, out_degree, out_edges, set_final,
    sigma, source, label, target, vertices
)

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
        self.m_directed = True
        self.w = w

    def alphabet(self) -> set:
        """
        See the overloaded :py:meth:`Trie.alphabet` method.
        """
        return {a for a in self.w}

    def delta(self, q: int, a: str):
        """
        See the overloaded :py:meth:`Automaton.delta` method.
        """
        return (
            q + 1 if q is not BOTTOM and not is_final(q, self) and self.w[q] == a
            else BOTTOM
        )

    def add_edge(self, *args):
        """
        See the overloaded :py:meth:`Automaton.add_edge` method.

        Raises:
            :py:class:`RuntimeError` as a string is immutable.
        """
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def add_vertex(self, *args):
        """
        See the overloaded :py:meth:`Automaton.add_vertex` method.

        Raises:
            :py:class:`RuntimeError` as a string is immutable.
        """
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def in_edges(self, q: int) -> iter:
        """
        Returns an iterator over the input transition of a given state.

        Args:
            q (int): A state of this :py:class:`DigitalSequence` corresponding
                to a valid index of the wrapped string.

        Returns:
            The corresponding iterator.
        """
        return (
            set() if self.is_initial(q)
            else {EdgeDescriptor(q - 1, q, self.w[q - 1])}
        )

    def out_edges(self, q: int) -> iter:
        """
        See the overloaded :py:meth:`Automaton.out_edges` method.
        """
        return (
            set() if self.is_final(q)
            else {EdgeDescriptor(q, q + 1, self.w[q])}
        )

    def remove_edge(self, *args):
        """
        See the overloaded :py:meth:`Automaton.remove_edge` method.

        Raises:
            :py:class:`RuntimeError` as a string is immutable.
        """
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def remove_vertex(self, *args):
        """
        See the overloaded :py:meth:`Automaton.remove_vertex` method.

        Raises:
            :py:class:`RuntimeError` as a string is immutable.
        """
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def sigma(self, q: int) -> iter:
        """
        See the overloaded :py:meth:`Automaton.sigma` method.
        """
        return set() if q is BOTTOM or self.is_final(q) else {self.w[q]}

    def edges(self) -> iter:
        """
        See the overloaded :py:meth:`Automaton.edges` method.
        """
        return (EdgeDescriptor(q, q + 1, self.w[q]) for q in range(len(self.w)))

    def vertices(self) -> iter:
        """
        See the overloaded :py:meth:`Automaton.vertices` method.
        """
        return range(len(self.w) + 1)

    def num_vertices(self) -> int:
        """
        See the overloaded :py:meth:`Automaton.num_vertices` method.
        """
        return len(self.w) + 1

    def num_edges(self) -> int:
        return len(self.w)

    def set_initial(self):
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def initial(self) -> int:
        return 0

    def is_initial(self, q) -> bool:
        return q == 0

    def set_final(self):
        raise RuntimeError(ERR_STRING_IMMUTABLE)

    def is_final(self, q: int) -> bool:
        return q == len(self.w)

    def insert(self, w: str):
        raise RuntimeError(ERR_STRING_IMMUTABLE)
