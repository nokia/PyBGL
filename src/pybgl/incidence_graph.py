#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .graph import *
# from .graph import DirectedGraph, EdgeDescriptor


class IncidenceGraph(DirectedGraph):
    """
    The :py:class:`IncidenceGraph` extends the :py:class:`DirectedGraph`
    so that the :py:meth:`IncidenceGraph.in_edges` and the
    :py:meth:`IncidenceGraph.in_degree` are well-defined.
    This is done by mapping each state with its input transitions.
    """
    def __init__(self, num_vertices: int = 0):
        """
        Constructor.

        Args:
            See :py:meth:`Graph.__init__`.
        """
        self.in_adjacencies = dict()
        super().__init__(num_vertices)

    def add_vertex(self) -> int:
        # Overloaded method
        u = super().add_vertex()
        self.in_adjacencies[u] = dict()
        return u

    def add_edge(self, u: int, v: int) -> tuple:
        # Overloaded method
        (e, added) = super().add_edge(u, v)
        if added:
            v_in_adjs = self.in_adjacencies[v]
            is_new = u not in v_in_adjs
            n = e.distinguisher
            if is_new:
                v_in_adjs[u] = {n}
            else:
                v_in_adjs[u].add(n)
        return (e, added)

    def remove_vertex(self, u: int):
        # Overloaded method
        for e in [e for e in self.in_edges(u)]:
            self.remove_edge(e)
        for e in [e for e in self.out_edges(u)]:
            self.remove_edge(e)
        del self.adjacencies[u]
        del self.in_adjacencies[u]

    def remove_edge(self, e: EdgeDescriptor):
        # Overloaded method
        super().remove_edge(e)
        u = e.source
        v = e.target
        n = e.distinguisher
        in_adjs_v = self.in_adjacencies[v]
        s = in_adjs_v[u]
        if n in s:
            s.remove(n)
            if s == set():
                del in_adjs_v[u]
                # We keep the empty dictionary to allow to
                # create out-arcs for u.

    def in_edges(self, v: int):
        # Overloaded method
        return (
            EdgeDescriptor(u, v, n)
            for (u, s) in self.in_adjacencies.get(v, dict()).items()
            for n in s
        )
