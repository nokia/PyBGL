#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from collections import defaultdict

# NB: pybgl.graph.edge and pybgl.graph.add_edge are not imported because their signature is different
from pybgl.graph import (
    DirectedGraph, EdgeDescriptor,
    add_edge, add_vertex, default_graphviz_style, edge, edges, num_edges, num_vertices,
    out_degree, out_edges,
    remove_vertex, remove_edge, source, target, vertices
)
from pybgl.graph        import graphviz_arc, graphviz_type, vertices
from pybgl.property_map import ReadPropertyMap, make_assoc_property_map

BOTTOM = None

class Automaton(DirectedGraph):
    # Convention: EdgeDescriptor(q, r, a)
    # Convention: self.m_adjacencies[q][a] == r
    def __init__(self, num_vertices :int = 0, q0 :int = 0, pmap_final = None):
        super().__init__(num_vertices)
        self.m_q0 = q0
        if not pmap_final:
            self.m_map_final = defaultdict(bool)
            self.m_pmap_final = make_assoc_property_map(self.m_map_final)
        else:
            self.m_pmap_final = pmap_final

    def delta(self, q :int, a :chr) -> int:
        return self.m_adjacencies.get(q, dict()).get(a, BOTTOM)

    def add_edge(self, q :int, r :int, a :chr) -> tuple:
        assert q is not None
        assert r is not None
        if self.delta(q, a):
            return (None, False)
        self.m_adjacencies[q][a] = r
        return (EdgeDescriptor(q, r, a), True)

    def edge(self, q :int, r :int, a :chr) -> tuple:
        assert q is not BOTTOM
        return (EdgeDescriptor(q, r, a), True) if q is not None and r == self.delta(q, a) else (None, False)

    def in_edges(self, q :int):
        raise Exception("Nope.")

    def out_edges(self, q :int):
        return (
            EdgeDescriptor(q, r, a) \
            for (a, r) in self.m_adjacencies.get(q, dict()).items()
        )

    def remove_edge(self, e :EdgeDescriptor):
        q = source(e, self)
        a = label(e, self)
        adj_q = self.m_adjacencies.get(q)
        if adj_q:
            if a in adj_q.keys():
                del adj_q[a]

    def sigma(self, q :int) -> set:
        return {a for a in self.m_adjacencies.get(q, dict()).keys()} if q is not None else set()

    def alphabet(self) -> set:
        return {a for q in vertices(self) for a in self.m_adjacencies.get(q, dict()).keys()}

    def edges(self):
        return (
            EdgeDescriptor(q, r, a) \
            for (q, adj_q) in self.m_adjacencies.items()
            for (a, r) in adj_q.items()
        )

    def set_initial(self, q :int, is_initial :bool = True):
        if is_initial:
            self.m_q0 = q
        elif self.m_q0 == q:
            self.m_q0 = None

    def initial(self) -> int:
        return self.m_q0

    def is_initial(self, q :int) -> bool:
        return self.m_q0 == q

    def label(self, e :EdgeDescriptor) -> chr:
        return e.m_distinguisher

    def set_final(self, q :int, is_final :bool = True):
        self.m_pmap_final[q] = is_final

    def is_final(self, q :int) -> bool:
        return self.m_pmap_final[q]

    def vertex_to_graphviz(self, u :int) -> str:
        return "%s [shape=\"%s\"]" % (
            u,
            "doublecircle" if self.is_final(u) else "circle"
        )

    def edge_to_graphviz(self, e :EdgeDescriptor) -> str:
        return "%s %s %s [label=\"%s\"]" % (
            source(e, self),
            graphviz_arc(self),
            target(e, self),
            label(e, self)
        )

    def to_dot(self, graphviz_style :str = None) -> str:
        if graphviz_style == None:
            graphviz_style = default_graphviz_style()
        return "%(type)s G {  %(style)s  %(vertices)s%(sep1)s  %(edges)s%(sep2)s\n}" % {
            "style"    : graphviz_style,
            "type"     : graphviz_type(self),
            "vertices" : ";\n  ".join(["  %s" % self.vertex_to_graphviz(u) for u in vertices(self)]),
            "sep1"     : ";" if num_vertices(self) else "",
            "edges"    : ";\n  ".join(["  %s" % self.edge_to_graphviz(e)   for e in edges(self)]),
            "sep2"     : ";" if num_edges(self) else "",
        }

def add_edge(q :int, r :int, a :chr, g :Automaton) -> tuple:
    return g.add_edge(q, r, a)

def edge(q :int, r: int, a :chr, g :Automaton) -> tuple:
    return g.edge(q, r, a)

def sigma(q :int, g :Automaton) -> set:
    return g.sigma(q)

def alphabet(g:Automaton) -> set:
    return g.alphabet()

def is_initial(q :int, g :Automaton) -> bool:
    return g.is_initial(q)

def initial(g :Automaton) -> int:
    return g.initial()

def is_final(q :int, g:Automaton) -> bool:
    return g.is_final(q)

def label(e :EdgeDescriptor, g) -> chr:
    return g.label(e)

def set_initial(q :int, g :Automaton, is_initial :bool = True):
    g.set_initial(q, is_initial)

def set_final(q :int, g :Automaton, is_final :bool = True):
    g.set_final(q, is_final)

def finals(g: Automaton) -> set:
    return {q for q in vertices(g) if is_final(q, g)}

def delta(q :int, a :chr, g :Automaton) -> int:
    return g.delta(q, a)

def accepts(w: str, g :Automaton) -> bool:
    q = initial(g)
    for a in w:
        if q is BOTTOM: return False
        q = delta(q, a, g)
    return is_final(q, g)

def accepts_debug(w: str, g :Automaton) -> bool:
    q = initial(g)
    print(f"w = {w} q0 = {q}")
    for (i, a) in enumerate(w):
        print(f"w[{i}] = {a}, {q} -> {delta(q, a, g)}")
        if q is BOTTOM: return False
        q = delta(q, a, g)
    return is_final(q, g)

def is_finite(g) -> bool:
    return True # By design of Automaton.

def is_deterministic(g) -> bool:
    return True # By design of Automaton.

def is_complete(g) -> bool:
    a = alphabet(g)
    for q in vertices(g):
        if sigma(q, g) != alphabet(g):
            return False
    return True

def is_minimal(g) -> bool:
    return True # Hardcoded, not implemented

def make_automaton(
    transitions  :list,
    q0n          :int = 0,
    pmap_vfinal  :ReadPropertyMap = None,
    AutomatonClass = Automaton
):
    if not pmap_vfinal:
        pmap_vfinal = make_assoc_property_map(defaultdict(bool))
    vertex_names = sorted(list({qn for (qn, rn, a) in transitions} | {rn for (qn, rn, a) in transitions}))
    map_vertices = {qn : q for (q, qn) in enumerate(vertex_names)}
    g = AutomatonClass(len(vertex_names))
    for (qn, rn, a) in transitions:
        q = map_vertices[qn]
        r = map_vertices[rn]
        add_edge(q, r, a, g)
    q0 = map_vertices[q0n]
    g.set_initial(q0)
    for q in vertices(g):
        qn = vertex_names[q]
        if pmap_vfinal[qn]:
            set_final(q, g)
    return g

def delta_best_effort(g :Automaton, w :str) -> tuple:
    q = initial(g)
    if not w:
        return (q, 0)
    for (i, a) in enumerate(w):
        r = delta(q, a, g)
        if r is BOTTOM:
            return (q, i)
        q = r
    return (q, i + 1)

def automaton_insert_string(g :Automaton, w :str):
    (q, i) = delta_best_effort(g, w)
    for a in w[i:]:
        r = add_vertex(g)
        add_edge(q, r, a, g)
        q = r
    set_final(q, g)
