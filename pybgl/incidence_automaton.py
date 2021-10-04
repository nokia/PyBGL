#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"


from pybgl.automaton import (
    BOTTOM, Automaton, EdgeDescriptor,
    accepts, accepts_debug, add_edge, add_vertex, add_edge, alphabet, delta, edge, edges,
    finals, initial, is_complete, is_deterministic, is_initial, is_final,
    is_finite, is_minimal, label,
    num_edges, num_vertices, out_degree, out_edges, set_final,
    remove_vertex, remove_edge, source, sigma, target, vertices,
    make_automaton
)
from pybgl.property_map import ReadPropertyMap

class IncidenceAutomaton(Automaton):
    def __init__(self, *args):
        self.m_in_adjacencies = dict() # in_adjacency[r][q] = {a}
        super().__init__(*args)

    @property
    def in_adjacencies(self) -> dict:
        return self.m_in_adjacencies

    def add_vertex(self) -> int:
        q = super().add_vertex()
        self.in_adjacencies[q] = dict()
        return q

    def add_edge(self, q :int, r :int, a :chr) -> tuple: # (EdgeDescriptor, bool)
        (e, added) = super().add_edge(q, r, a)
        if added:
            r_in_adjs = self.in_adjacencies[r]
            is_new = q not in r_in_adjs
            if is_new:
                r_in_adjs[q] = {a}
            else:
                r_in_adjs[q].add(a)
        return (e, added)

    def remove_vertex(self, q :int):
        # Note: we could rely on remove_edge for each in/out-edge, but the
        # following implementation is faster.

        # In-edges: (p, q) edges
        if q in self.in_adjacencies.keys():
            for e in in_edges(q, self):
                p = source(e, self)
                a = label(e, self)
                del self.adjacencies[p][a]
            del self.in_adjacencies[q]

        # Out-edges: (q, r) edges
        if q in self.adjacencies.keys():
            for e in out_edges(q, self):
                r = target(e, self)
                if q in self.in_adjacencies[r].keys():
                    # This test is required to cope with parallel (q, r) edges.
                    del self.in_adjacencies[r][q]
            del self.adjacencies[q]

    def remove_edge(self, e :EdgeDescriptor):
        # Clean self.adjacencies
        super().remove_edge(e)

        # Clean self.in_adjacencies
        q = source(e, self)
        r = target(e, self)
        a = label(e, self)
        in_adjs_r = self.in_adjacencies[r]
        s = in_adjs_r[q]
        if a in s:
            s.remove(a)
            if s == set():
                del in_adjs_r[q]
                # We keep the empty dictionary to allow to create out-arcs for q.

    def in_edges(self, r :int):
        return (
            EdgeDescriptor(q, r, a)
            for (q, s) in self.in_adjacencies.get(r, dict()).items()
            for a in s
        )

    def in_degree(self, q :int) -> int:
        return len([e for e in in_edges(q, self)])

def in_edges(q :int, g :IncidenceAutomaton):
    return g.in_edges(q)

def in_degree(q :int, g :IncidenceAutomaton) -> int:
    return g.in_degree(q)

def make_incidence_automaton(
    transitions :list,
    q0n :int = 0,
    pmap_vfinal :ReadPropertyMap = None
):
    return make_automaton(
        transitions, q0n, pmap_vfinal,
        AutomatonClass = IncidenceAutomaton
    )
