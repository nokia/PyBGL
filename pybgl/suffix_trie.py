#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob, Elie de Panafieu"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "{marc-olivier.buob,elie.de_panafieu}@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from itertools          import chain
from pybgl.property_map import make_func_property_map
from pybgl.trie         import BOTTOM, Trie, add_vertex, add_edge, delta, initial, num_vertices

def slices(n, max_len :int = None):
    return chain(
        ((0, 0), ), # Empty word
        (
            (i, j)
            for i in range(n) \
            for j in range(i + 1, min(n, i + max_len) + 1 if max_len else n + 1)
        )
    )

def factors(s, max_len :int = None):
    n = len(s)
    return (s[i:j] for (i, j) in slices(n, max_len))

def make_suffix_trie(w :str = "", max_len :int = None, g :Trie = None) -> Trie:
    if g is None:
        g = Trie()
    if num_vertices(g) == 0:
        add_vertex(g)
    g.m_pmap_final = make_func_property_map(lambda q: q != BOTTOM)

    # Naive implementation (slow)
    # g.insert("")
    # for factor in factors(w, max_len):
    #     g.insert(factor)

    # Optimized version, designed by Elie.
    n = len(w)
    for i in range(n):
        q = initial(g)
        for j in range(i, min(n, i + max_len) if max_len else n):
            a = w[j]
            r = delta(q, a, g)
            if r is BOTTOM:
                r = add_vertex(g)
                add_edge(q, r, a, g)
            q = r
    return g
