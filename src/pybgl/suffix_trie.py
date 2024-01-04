#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from itertools import chain
from .property_map import make_func_property_map
from .trie import BOTTOM, Trie


def slices(n, max_len: int = None) -> iter:
    """
    Makes an iterator that lists every possible slices between ``0`` and ``n``
    that covers an interval which length is lower than ``max_len``.

    Example:
        >>> list(slices(4, 2))
        [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]

    Args:
        n (int): The upper bound.
        max_len (int): The maximal length of the ranges.
            Pass ``None`` if not needed.

    Returns:
        The corresponding iterator.
    """
    return chain(
        ((0, 0), ),  # Empty word
        (
            (i, j)
            for i in range(n)
            for j in range(
                i + 1,
                min(n, i + max_len) + 1 if max_len else n + 1
            )
        )
    )


def factors(s: str, max_len: int = None) -> iter:
    """
    Makes an iterator that lists the factors (substring) of a string ``s``
    which length is lower than ``max_len``.

    Example:
        >>> sorted(set(factors("banana", 3)))
        ['', 'a', 'an', 'ana', 'b', 'ba', 'ban', 'n', 'na', 'nan']

    Args:
        s (str): The input string.
        max_len (int): The maximal length of the factors.
            Pass ``None`` if not needed.

    Returns:
        The corresponding iterator.
    """
    n = len(s)
    return (s[i:j] for (i, j) in slices(n, max_len))


def make_suffix_trie(w: str = "", max_len: int = None, g: Trie = None) -> Trie:
    """
    Makes a :py:class:`Trie` instance that gathers all the factors
    of a given word.

    Args:
        w (str): The input word.
        max_len (int): The maximal length of the factors stored in
            the returned :py:class:`Trie` instance.
            Pass ``None`` if not needed.
        g (Trie): A reference output :py:class:`Trie` instance.
            Pass ``None`` if not needed.

    Returns:
        The corresponding trie.
    """
    if g is None:
        g = Trie(pmap_vfinal=make_func_property_map(lambda q: q != BOTTOM))
    if g.num_vertices() == 0:
        g.add_vertex()

    # Naive implementation (slow)
    # g.insert("")
    # for factor in factors(w, max_len):
    #     g.insert(factor)

    # Optimized version, designed by Elie.
    n = len(w)
    for i in range(n):
        q = g.initial()
        for j in range(i, min(n, i + max_len) if max_len else n):
            a = w[j]
            r = g.delta(q, a)
            if r is BOTTOM:
                r = g.add_vertex()
                g.add_edge(q, r, a)
            q = r
    return g
