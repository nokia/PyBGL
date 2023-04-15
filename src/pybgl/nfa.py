#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.automaton import *
from pybgl.property_map import ReadWritePropertyMap

EPSILON = "\u03b5"

class Nfa(DirectedGraph):
    def __init__(
        self,
        num_vertices :int = 0,
        initials     :set = None,
        pmap_final   :ReadWritePropertyMap = None,
        epsilon      :str = EPSILON
    ):
        super().__init__(num_vertices)
        self.initials = initials if initials else {0}
        if not pmap_final:
            self.map_final = defaultdict(bool)
            self.pmap_final = make_assoc_property_map(self.map_final)
        else:
            self.pmap_final = pmap_final
        self.epsilon = epsilon

    def delta_one_step(self, qs, a) -> set:
        sets = [set(self.adjacencies.get(q, dict()).get(a, dict()).keys()) for q in qs]
        return set.union(*sets) if sets else set()

    def delta_epsilon(self, qs) -> set:
        ret = set()
        qs_new = set(qs)
        while qs_new:
            ret |= qs_new
            qs_new = self.delta_one_step(qs_new, self.epsilon)
            qs_new -= ret
        return ret

    def delta(self, q :int, a :chr) -> set:
        qs = self.delta_epsilon({q})
        qs = self.delta_one_step(qs, a)
        qs = self.delta_epsilon(qs)
        return qs

    def sigma(self, q :int) -> set:
        qs = self.delta_epsilon({q})
        return (
            set() if q is BOTTOM else
            {
                a
                for q in qs
                for a in self.adjacencies.get(q, dict()).keys()
                if a != self.epsilon
            }
        )

    def add_edge(self, q :int, r :int, a :chr) -> tuple:
        arn = self.adjacencies.get(q)
        if arn is None:
            arn = self.m_adjacencies[q] = dict()
        rn = arn.get(a)
        if rn is None:
            rn = self.m_adjacencies[q][a] = dict()
        s = rn.get(r)
        if s is None:
            s = rn[r] = set()
        n = len(s) + 1
        s.add(n)
        return (EdgeDescriptor(q, r, (a, n)), True)

    def remove_edge(self, e :EdgeDescriptor):
        q = source(e, self)
        r = target(e, self)
        (a, n) = e.m_distinguisher
        try:
            del self.m_adjacencies[q][a][r]
        except KeyError:
            pass

    def out_edges(self, q :int):
        return (
            EdgeDescriptor(q, r, (a, n))
            for (a, rn) in self.adjacencies.get(q, dict()).items()
            for (r, n) in rn.items()
        )

    def edges(self):
        return (
            EdgeDescriptor(q, r, (a, n))
            for (q, arn) in self.adjacencies.items()
            for (a, rn) in arn.items()
            for (r, n) in rn.items()
        )

    def alphabet(self) -> set:
        return {
            a
            for (q, arn) in self.adjacencies.items()
            for a in arn.keys()
            if a != self.epsilon
        }

    def set_initial(self, q :int, is_initial :bool = True):
        if is_initial:
            self.initials.add(q)
        elif q in self.initials:
            self.initials.remove(q)

    def initials(self) -> set:
        return self.initials

    def is_initial(self, q :int) -> bool:
        return q in self.initials

    def set_initial(self, q :int, is_initial :bool = True):
        if is_initial:
            self.initials.add(q)
        else:
            self.initials.discard(q)

    def set_initials(self, q0s :set):
        self.initials = {q0 for q0 in q0s}

    def label(self, e :EdgeDescriptor) -> chr:
        (a, n) = e.m_distinguisher
        return a

    def set_final(self, q :int, is_final :bool = True):
        self.pmap_final[q] = is_final

    def is_final(self, q :int) -> bool:
        return self.pmap_final[q]

    def to_dot(self, **kwargs):
        dpv = {
            "shape" : make_func_property_map(
                lambda u: "doublecircle" if self.is_final(u) else "circle"
            ),
        }
        dpe = {
            "label" : make_func_property_map(
                lambda e: (
                    "<i>\u03b5</i>" if self.label(e) == self.epsilon
                    else self.label(e)
                )
            )
        }
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        kwargs = enrich_kwargs(dpe, "dpe", **kwargs)
        return super().to_dot(**kwargs)

    def accepts(self, w) -> True:
        return any(is_final(q, self) for q in delta_word(w, self))

    def delta_word(self, w) -> set:
        qs = set(initials(self))
        qs = self.delta_epsilon(qs)
        for a in w:
            if not qs: break
            qs = set.union(*[delta(q, a, self) for q in qs])
        return qs

    def finals(self):
        return (q for q in vertices(self) if is_final(q, self))

def epsilon(nfa :Nfa) -> chr:
    return nfa.epsilon

def is_epsilon_transition(e :EdgeDescriptor, nfa :Nfa) -> bool:
    return label(e, nfa) == epsilon(nfa)

def initials(nfa :Nfa):
    return (q for q in nfa.initials)

def set_initials(q0s, nfa :Nfa):
    nfa.set_initials(q0s)

def delta_word(w, nfa) -> set: # Overloads Automaton.delta_word
    return nfa.delta_word(w)
