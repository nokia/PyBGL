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

from pybgl.graph   import in_degree, in_edges
from pybgl.trie    import \
    BOTTOM, EdgeDescriptor, Trie, \
    accepts, alphabet, delta, edge, edges, \
    is_initial, initial, is_final, is_finite, finals, \
    num_edges, num_vertices, out_degree, out_edges, set_final, \
    sigma, source, label, target, vertices

ERR_STRING_IMMUTABLE = "String is immutable"

class DigitalSequence(Trie):
    def __init__(self, w :str):
        self.m_directed = True
        self.w = w
    def alphabet(self) -> set:
        return {a for a in self.w}
    def delta(self, q :int, a :chr):
        return q + 1 if q is not BOTTOM and not is_final(q, self) and self.w[q] == a else BOTTOM
    def add_edge(self, *args):
        raise RuntimeError(ERR_STRING_IMMUTABLE)
    def add_vertex(self, *args):
        raise RuntimeError(ERR_STRING_IMMUTABLE)
    def in_edges(self, q :int):
        return {} if is_initial(q, self) else {EdgeDescriptor(q - 1, q, self.w[q - 1])}
    def out_edges(self, q :int):
        return {} if is_final(q, self) else {EdgeDescriptor(q, q + 1, self.w[q])}
    def remove_edge(self, *args):
        raise RuntimeError(ERR_STRING_IMMUTABLE)
    def remove_vertex(self, *args):
        raise RuntimeError(ERR_STRING_IMMUTABLE)
    def sigma(self, q :int) -> set:
        return set() if q is BOTTOM or is_final(q, self) else {self.w[q]}
    def edges(self):
        return (EdgeDescriptor(q, q + 1, self.w[q]) for q in range(len(self.w)))
    def vertices(self):
        return range(len(self.w) + 1)
    def num_vertices(self) -> int:
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
    def is_final(self, q :int) -> bool:
        return q == len(self.w)
    def insert(self, w :str):
        raise RuntimeError(ERR_STRING_IMMUTABLE)
