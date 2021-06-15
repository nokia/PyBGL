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
from pybgl.automaton        import *
from pybgl.graph            import add_edge, add_vertex, edge
from pybgl.property_map     import (
    ReadWritePropertyMap, make_assoc_property_map, make_func_property_map
)

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

    def to_dot(self, **kwargs) -> str:
        dpv = {
            "shape" : make_func_property_map(
                lambda u: "doublecircle" if self.is_final(u) else "circle"
            ),
            "label" : make_func_property_map(
                lambda u: "^" if self.is_initial(u) else self.symbol(u)
            )
        }
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        return super().to_dot(**kwargs)

def add_vertex(a :chr, g :NodeAutomaton) -> int:
    return g.add_vertex(a)

def symbol(q :int, g :NodeAutomaton) -> chr:
    return g.symbol(q)

