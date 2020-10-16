#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"


from collections                import defaultdict
from pybgl.graph                import __len_gen__
from pybgl.property_map         import ReadPropertyMap, make_assoc_property_map
from pybgl.incidence_automaton  import in_degree, in_edges
from pybgl.node_automaton       import (
    BOTTOM, NodeAutomaton, EdgeDescriptor, accepts, accepts_debug, add_edge, add_vertex,
    alphabet, delta, edge, edges, graphviz_arc, initial, is_initial, is_final, is_finite,
    finals, label, num_edges, num_vertices, out_degree, out_edges, set_final, symbol,
    remove_vertex, remove_edge, set_initial, set_final, source, sigma, target, vertices
)

class IncidenceNodeAutomaton(NodeAutomaton):
    def __init__(self, *args, pmap_vsymbol = None):
        self.predecessors = defaultdict(set) # predecessors[r] = {q}
        super().__init__(*args, pmap_vsymbol = pmap_vsymbol) # UGLY

    # TODO: Factorize with IncidenceAutomaton

    def add_edge(self, q :int, r :int) -> tuple: # (EdgeDescriptor, bool)
        (e, added) = super().add_edge(q, r)
        if added:
            self.predecessors[r].add(q)
        return (e, added)

    def in_edges(self, r :int):
        return (
            EdgeDescriptor(q, r, symbol(r, self))
            for q in self.predecessors.get(r, set())
        )

    def in_degree(self, r :int):
        return __len_gen__(in_edges(r, self))

    def remove_vertex(self, q :int):
        # Note: we could rely on remove_edge for each in/out-edge, but the
        # following implementation is faster.

        # In-edges: (p, q) edges
        if q in self.predecessors.keys():
            a = symbol(q, self)
            for e in in_edges(q, self):
                p = source(e, self)
                del self.adjacencies[p][a]
            del self.predecessors[q]

        # Out-edges: (q, r) edges
        if q in self.adjacencies.keys():
            for e in out_edges(q, self):
                r = target(e, self)
                if q in self.predecessors[r]:
                    # This test is required to cope with parallel (q, r) edges.
                    self.predecessors[r].remove(q)
            del self.adjacencies[q]

    def remove_edge(self, e :EdgeDescriptor):
        super().remove_edge(e)
        q = source(e, self)
        r = target(e, self)
        self.predecessors[r].remove(q)

def make_incidence_node_automaton(
    transitions :list,
    pmap_vlabel :ReadPropertyMap,
    q0n :int = 0,
    pmap_vfinal :ReadPropertyMap = None,
    Constructor = IncidenceNodeAutomaton
):
    # Keep vertex order without regard transition ordering.
    transitions = sorted(transitions)

    if not pmap_vfinal:
        pmap_vfinal = make_assoc_property_map(defaultdict(bool))

    # Set initial state
    g = Constructor(1)
    q0 = 0
    g.set_initial(q0)
    map_vertices = {q0n : q0}
    if pmap_vfinal[q0n]:
        set_final(q0, g)

    # Add states
    def _add_state(qn) -> int:
        q = map_vertices.get(qn)
        if q is None:
            a = pmap_vlabel[qn]
            q = add_vertex(a, g)
            map_vertices[qn] = q
            if pmap_vfinal[qn]:
                set_final(q, g)
        return q

    for (qn, rn) in transitions:
        q = _add_state(qn)
        r = _add_state(rn)
        add_edge(q, r, g)
    return g
