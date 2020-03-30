#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Incidence graph implements in_edge and in_degree primitives.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.graph    import DirectedGraph, \
    EdgeDescriptor, source, target, \
    add_vertex, vertices, num_vertices, remove_vertex, \
    add_edge, edge, edges, num_edges, remove_edge, \
    out_degree, out_edges

class IncidenceGraph(DirectedGraph):
    def __init__(self, num_vertices :int = 0):
        self.m_in_adjacencies = dict()
        super().__init__(num_vertices)

    @property
    def in_adjacencies(self) -> dict:
        return self.m_in_adjacencies

    def add_vertex(self) -> int:
        u = super().add_vertex()
        self.in_adjacencies[u] = dict()
        return u

    def add_edge(self, u :int, v :int) -> tuple: # (EdgeDescriptor, bool)
        (e, added) = super().add_edge(u, v)
        if added:
            v_in_adjs = self.in_adjacencies[v]
            is_new = u not in v_in_adjs
            n = e.m_distinguisher
            if is_new:
                v_in_adjs[u] = {n}
            else:
                v_in_adjs[u].add(n)
        return (e, added)

    def remove_vertex(self, u :int):
        for e in [e for e in in_edges(u, self)]:
            remove_edge(e, self)
        for e in [e for e in out_edges(u, self)]:
            remove_edge(e, self)
        del self.adjacencies[u]
        del self.in_adjacencies[u]

    def remove_edge(self, e :EdgeDescriptor):
        super().remove_edge(e)
        u = e.m_source
        v = e.m_target
        n = e.m_distinguisher
        in_adjs_v = self.in_adjacencies[v]
        s = in_adjs_v[u]
        if n in s:
            s.remove(n)
            if s == set():
                del in_adjs_v[u]
                # We keep the empty dictionary to allow to create out-arcs for u.

    def in_edges(self, v :int):
        return (EdgeDescriptor(u, v, n) for u, s in self.in_adjacencies.get(v, dict()).items() for n in s)

def in_edges(v :int, g :IncidenceGraph):
    return g.in_edges(v)

def in_degree(v :int, g :IncidenceGraph) -> int:
    return len([e for e in in_edges(v, g)])
