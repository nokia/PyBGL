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


from collections            import defaultdict
from pybgl.automaton        import \
    BOTTOM, Automaton, EdgeDescriptor, accepts, add_vertex, alphabet, \
    delta, edges, graphviz_arc, initial, is_initial, is_final, is_finite, \
    final, label, num_edges, num_vertices, out_degree, out_edges, set_final, \
    remove_vertex, remove_edge, set_initial, set_final, source, sigma, target, vertices
from pybgl.graph            import add_edge, edge
from pybgl.property_map     import ReadWritePropertyMap, make_assoc_property_map

class NodeAutomaton(Automaton):
    def __init__(
        self,
        num_vertices :int = 0,
        q0 :int = 0,
        pmap_final = None,
        pmap_vsymbol :ReadWritePropertyMap = None
    ):
        # Convention: self.adjacencies[q][a] = r
        super().__init__(num_vertices, q0, pmap_final)
        if pmap_vsymbol is None:
            map_vsymbol = defaultdict(lambda: None)
            pmap_vsymbol = make_assoc_property_map(map_vsymbol)
        self.pmap_vsymbol = pmap_vsymbol

    def add_vertex(self, a :chr = None) -> int:
        u = super().add_vertex()
        if a is not None:
            self.pmap_vsymbol[u] = a
        return u

    def delta(self, q :int, a :chr) -> int:
        return self.adjacencies[q].get(a, BOTTOM)

    def add_edge(self, q :int, r :int) -> tuple:
        assert q is not None
        assert r is not None
        a = symbol(r, self)
        adj_q = self.adjacencies[q]
        if a in adj_q.keys(): return (None, False)
        self.adjacencies[q][a] = r
        return (EdgeDescriptor(q, r, a), True)

    def edge(self, q :int, r :int) -> tuple:
        adj_q = self.adjacencies.get(q)
        (e, found) = (None, False)
        if adj_q:
            for (a, r_) in adj_q.items():
                if r == r_:
                    e = EdgeDescriptor(q, r, a)
                    found = True
                    break
        return (e, found)

    def symbol(self, q :int) -> chr:
        return self.pmap_vsymbol[q]

    def out_edges(self, q :int):
        return (EdgeDescriptor(q, r, a) for (a, r) in self.adjacencies[q].items())

    def remove_edge(self, e :EdgeDescriptor):
        q = source(e, self)
        r = target(e, self)
        a = symbol(r, self)
        adj_q = self.m_adjacencies.get(q)
        if adj_q:
            if a in adj_q:
                del adj_q[a]

    def sigma(self, q :int) -> set:
        return set(self.adjacencies.get(q, dict()).keys()) if q is not BOTTOM \
          else set()

    def alphabet(self) -> set:
        return {symbol(q, self) for q in vertices(self) if not is_initial(q, self)}

    def edges(self):
        return (
            EdgeDescriptor(q, r, a) \
            for (q, adj_q) in self.adjacencies.items()
            for (a, r) in adj_q.items()
        )

    def label(self, e :EdgeDescriptor) -> chr:
        return symbol(target(e, self), self)

    def vertex_to_graphviz(self, q :int) -> chr:
        return "%s [shape=\"%s\" label=<%s>]" % (
            q,
            "doublecircle" if self.is_final(q) else "circle",
            symbol(q, self) if not is_initial(q, self) else "^"
        )

    def edge_to_graphviz(self, e :EdgeDescriptor) -> str:
        return "%s %s %s" % (
            source(e, self),
            graphviz_arc(self),
            target(e, self)
        )

def add_vertex(a :chr, g :NodeAutomaton) -> int:
    return g.add_vertex(a)

def symbol(q :int, g :NodeAutomaton) -> chr:
    return g.symbol(q)

