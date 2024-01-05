#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .automaton import *
# from .automaton import Automaton, EdgeDescriptor, make_automaton
from .property_map import ReadPropertyMap


class IncidenceAutomaton(Automaton):
    """
    The :py:class:`IncidenceAutomaton` extends the :py:class:`Automaton`
    so that the :py:meth:`IncidenceAutomaton.in_edges` and the
    :py:meth:`IncidenceAutomaton.in_degree` are well-defined.
    This is done by mapping each state with its input transitions.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.

        Args:
            See :py:meth:`Automaton.__init__`.
        """
        self.in_adjacencies = dict()  # in_adjacency[r][q] = {a}
        super().__init__(*args, **kwargs)

    def add_vertex(self) -> int:
        # Overloaded method
        q = super().add_vertex()
        self.in_adjacencies[q] = dict()
        return q

    def add_edge(self, q: int, r: int, a: str) -> tuple:
        # Overloaded method
        (e, added) = super().add_edge(q, r, a)
        if added:
            r_in_adjs = self.in_adjacencies[r]
            is_new = q not in r_in_adjs
            if is_new:
                r_in_adjs[q] = {a}
            else:
                r_in_adjs[q].add(a)
        return (e, added)

    def remove_vertex(self, q: int):
        # Overloaded method
        # Note: we could rely on remove_edge for each in/out-edge, but the
        # following implementation is faster.

        # In-edges: (p, q) edges
        if q in self.in_adjacencies.keys():
            for e in self.in_edges(q):
                p = self.source(e)
                a = self.label(e)
                del self.adjacencies[p][a]
            del self.in_adjacencies[q]

        # Out-edges: (q, r) edges
        if q in self.adjacencies.keys():
            for e in self.out_edges(q):
                r = self.target(e)
                if q in self.in_adjacencies[r].keys():
                    # This test is required to cope with parallel (q, r) edges.
                    del self.in_adjacencies[r][q]
            del self.adjacencies[q]

    def remove_edge(self, e: EdgeDescriptor):
        # Overloaded method
        # Clean self.adjacencies
        super().remove_edge(e)

        # Clean self.in_adjacencies
        q = self.source(e)
        r = self.target(e)
        a = self.label(e)
        in_adjs_r = self.in_adjacencies[r]
        s = in_adjs_r[q]
        if a in s:
            s.remove(a)
            if s == set():
                del in_adjs_r[q]
                # We keep the empty dictionary to allow to create
                # out-arcs for q.

    def in_edges(self, r: int):
        # Overloaded method
        return (
            EdgeDescriptor(q, r, a)
            for (q, s) in self.in_adjacencies.get(r, dict()).items()
            for a in s
        )


def make_incidence_automaton(
    transitions: list,
    q0n: int = 0,
    pmap_vfinal: ReadPropertyMap = None
) -> IncidenceAutomaton:
    """
    Builds an :py:class:`IncidenceAutomaton` instance according to a set
    of edges, by specializing :py:func:`make_automaton`.

    See :py:func:`make_automaton` for additional details.

    Returns:
        The corresponding :py:class:`IncidenceAutomaton` instance.
    """
    return make_automaton(
        transitions, q0n, pmap_vfinal,
        Constructor=IncidenceAutomaton
    )
