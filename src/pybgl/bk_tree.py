#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

import sys
from collections import deque
from .automaton import *
from .algebra import INFINITY
from .levenshtein_distance import levenshtein_distance

class BKTree(Automaton):
    """
    A `BK-tree <https://en.wikipedia.org/wiki/BK-tree>` is a
    metric tree suggested by Walter Austin Burkhard and
    Robert M. Keller specifically adapted to discrete metric spaces.

    This implementation is inspired from
    `this link <https://signal-to-noise.xyz/post/bk-tree/>`__.

    We inherit :py:class:`Automaton` because a BK-tree can be seen
    as a deterministic automaton whose alphabet
    it the weight assigned to its edge;
    """
    def __init__(self, distance: callable):
        """
        Constructor.

        Args:
            distance (callable): An arbitrary string distance.
                `Example:` :py:func:`levenshtein_distance`.
        """
        super().__init__()
        self.distance = distance
        self.map_velement = defaultdict()
        self.root = None

    def add_vertex(self, w: str) -> int:
        """
        Adds a vertex to this :py:class:`BKTree` instance.

        Args:
            w (str): The word assigned to the added node.

        Returns:
            The corresponding vertex descriptor.
        """
        u = super().add_vertex()
        self.map_velement[u] = w
        return u

    def element(self, u: int) -> str:
        """
        Retrieves the element assigned to a node of this :py:class:`BKTree` instance.

        Args:
            u (int): The vertex descriptor of the considered node.

        Returns:
            The element assigned to ``u``.
        """
        return self.map_velement[u]

    def insert(self, w: str, u: int = None) -> int:
        """
        Inserts an element in this :py:class:`BKTree` instance from
        a given node.

        Args:
            w (str): The element to be inserted.
            u (int): The vertex descriptor of the considered node.
                You may pass ``None`` to start from the root.

        Returns:
            The vertex descriptor of the word mapped to ``w``.
        """
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
                self.add_edge(u, v, d)
                return v
            u = v

    def search(self, w: str, d_max: int = INFINITY, r: int = None) -> tuple:
        """
        Searches an element in this :py:class:`BKTree` instance from
        a given node, assuming its distance with the element assigned to
        the root does not exceed ``d_max``.

        Args:
            w (object): The element to be inserted.
            d_max (int): The radius search. Defaults to :py:class:`INFINITY`.
            r (int): The vertex descriptor of the considered node.
                You may pass ``None`` to start from the root.

        Returns:
            A pair ``(w_best, d_best)`` where ``w_best`` is the best match
            and ``d_best`` the distance between the root element and ``w_best``
            if found, ``None`` otherwise.
        """
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
                d_uv = self.label(e)
                if abs(d_uv - d_u) <= d_best: # Cut-off criterion
                    v = self.target(e)
                    to_process.appendleft(v)
        return (w_best, d_best) if w_best is not None else None

    def to_dot(self, **kwargs) -> str:
        """
        Exports this :py:class:`Automaton` instance to a Graphviz string.
        See the :py:func:`to_dot` function.

        Returns:
            The corresponding graphviz string.
        """
        dpv = {"label":  make_assoc_property_map(self.map_velement)}
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        return super().to_dot(**kwargs)

def add_vertex(w: str, t: BKTree) -> int:
    """
    Adds a vertex to a :py:class:`BKTree` instance.

    Args:
        w (str): The word assigned to the added node.
        t (BKTree): The considered BK-tree.

    Returns:
        The corresponding vertex descriptor.
    """
    return t.add_vertex(w)

def bk_tree_insert(w: str, t: BKTree, u = None) -> int:
    """
    Inserts an element in a :py:class:`BKTree` instance from
    a given node.

    Args:
        w (str): The element to be inserted.
        t (BKTree) The BK-tree.
        u (int): The vertex descriptor of the considered node.
            You may pass ``None`` to start from the root.

    Returns:
        The vertex descriptor of the word mapped to ``w``.
    """
    return t.insert(w, u)

def make_bk_tree(elements: iter, distance: callable = None) -> BKTree:
    """
    Makes a BK Tree from a list of words.

    Args:
        elements: The list of elements organized in the BK-tree.
        distance (callable): The distance over the set of elements
            used to organize the BK-tree.

    Returns:
        The resulting BK-tree.
    """
    if distance is None:
        distance = levenshtein_distance
    t = BKTree(distance)
    for x in elements:
        t.insert(x)
    return t
