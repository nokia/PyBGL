#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2021, Nokia"
__license__    = "BSD-3"


import sys
from collections import defaultdict, deque
from pybgl.automaton import *

INFINITY = sys.maxsize

def levenshtein_distance(x :str, y :str) -> int:
    x_1 = x[1:]
    y_1 = y[1:]
    return (
        len(x) if not y else
        len(y) if not x else
        levenshtein_distance(x_1, y_1) if x[0] == y[0] else
        1 + min(
            levenshtein_distance(x_1, y),
            levenshtein_distance(x, y_1),
            levenshtein_distance(x_1, y_1),
        )
    )

class BKTree(Automaton):
    """
    A BK-tree is a metric tree suggested by Walter Austin Burkhard and Robert M. Keller specifically adapted to discrete metric spaces.
    For simplicity, consider integer discrete metric d(x,y).
    Then, BK-tree is defined as follows. An arbitrary element 𝑎 is selected as root node.
    The root node may have zero or more subtrees. The 𝑘-th subtree is recursively built of all elements 𝑏 such that d(a,b)=k.
    BK-trees can be used for approximate string matching in a dictionary.
    """
    def __init__(self, distance :callable):
        super().__init__()
        self.distance = distance
        self.map_velement = dict()
        self.root = None

    def add_vertex(self, w :object) -> int:
        u = super().add_vertex()
        self.map_velement[u] = w
        return u

    def element(self, u :int) -> object:
        return self.map_velement[u]

    def insert(self, w :object, u :int = None) -> int:
        if self.root is None:
            # The tree is empty
            self.root = self.add_vertex(w)
            return self.root

        if u is None:
            # Search from the root node.
            u = self.root

        while u is not BOTTOM:
            w_u = self.element(u)
            d = self.distance(w, w_u)
            if d == 0:
                return u
            v = delta(u, d, self)
            if v is BOTTOM:
                v = self.add_vertex(w)
                add_edge(u, v, d, self)
                return v
            u = v

    def search(self, w :object, d_max = INFINITY, r :int = None) -> tuple:
        if self.root is None:
            return None
        if r is None:
            r = self.root
        to_process = deque([r])
        (w_best, d_best) = (None, d_max)
        while to_process:
            u = to_process.pop()
            w_u = self.element(u)
            d_u = self.distance(w, w_u)
            if d_u <= d_best:
                (w_best, d_best) = (w_u, d_u)
            for e in self.out_edges(u):
                d_uv = label(e, self)
                if abs(d_uv - d_u) <= d_best: # Cut-off criterion
                    v = target(e, self)
                    to_process.appendleft(v)
        return (w_best, d_best) if w_best is not None else None

    def to_dot(self, **kwargs) -> str:
        dpv = {"label" : make_assoc_property_map(self.map_velement)}
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        return super().to_dot(**kwargs)

def add_vertex(x, t :BKTree) -> int:
    return t.add_vertex(x)

def bk_tree_insert(w :object, t :BKTree, u = None) -> int:
    return t.insert(w, u)

def make_bk_tree(elements :iter, distance :callable = None) -> BKTree:
    if distance is None:
        distance = levenshtein_distance
    t = BKTree(distance)
    for x in elements:
        t.insert(x)
    return t

