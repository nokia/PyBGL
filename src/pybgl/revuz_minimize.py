#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .incidence_automaton import IncidenceAutomaton
from .property_map import (
    ReadPropertyMap, ReadWritePropertyMap,
    make_assoc_property_map, make_func_property_map
)
from .incidence_node_automaton import (
    IncidenceNodeAutomaton, EdgeDescriptor
)

class DefaultRevuzMinimizeVisitor:
    def merging_states(
        self,
        q1: int,
        q2: int,
        g: IncidenceNodeAutomaton
    ):
        """
        Method invoked when two states are about to be merged.

        Args:
            q1 (int): The first merged state (about to become the merged state).
            q2 (int): The second merged state (about to be removed).
            g (IncidenceNodeAutomaton): The processed automaton.
        """
        pass

    def move_transition(
        self,
        e_old: EdgeDescriptor,
        e_new: EdgeDescriptor,
        g: IncidenceNodeAutomaton
    ):
        """
        Method invoked when a transition has just been moved.

        Args:
            e_old (EdgeDescriptor): The transition before being moved.
            e_new (EdgeDescriptor): The transition after being moved.
            g (IncidenceNodeAutomaton): The processed automaton.
        """
        pass

    def remove_vertex(self, u: int, g: IncidenceNodeAutomaton):
        """
        Method invoked when a state is about to be removed.

        Args:
            u (int): The state being removed.
            g (IncidenceNodeAutomaton): The processed automaton.
        """
        pass

    def states_merged(self, q1: int, q2: int, g: IncidenceNodeAutomaton):
        """
        Method invoked when two states have just been merged as well as
        their transitions.

        Args:
            q1 (int): The first merged state (about to become the merged state).
            q2 (int): The second merged state (about to be removed).
            g (IncidenceNodeAutomaton): The processed automaton.
        """
        pass

def revuz_height(
    g,
    pmap_vheight: ReadWritePropertyMap,
    leaves: set = None
) -> int:
    """
    Computes the height of each vertex starting from its leaves.
    The leaves have a height equal to ``0``.

    Args:
        g (IncidenceNodeAutomaton): The input automaton. It MUST be acyclic.
        pmap_vheight (ReadWritePropertyMap): A
            ``ReadWritePropertyMap{VertexDescriptor: int}`` which maps
            each vertex with its height.
        leaves (set): The leaves of the ``g``.
            Pass ``None`` to compute this set automatically.

    Returns:
        The maximum height.
    """
    h = 0
    vertices_to_process = leaves if leaves else {
        q
        for q in g.vertices()
        if g.out_degree(q) == 0
    }

    while vertices_to_process:
        next_vertices_to_process = set()
        for v in vertices_to_process:
            # pmap_vheight[v] = max(pmap_vheight[v], h). Note that max is not needed
            # according to the traversal order.
            pmap_vheight[v] = h
            for e in g.in_edges(v):
                u = g.source(e)
                next_vertices_to_process.add(u)
        vertices_to_process = next_vertices_to_process
        h += 1
    return h - 1

def revuz_minimize(
    g,
    pmap_vlabel: ReadPropertyMap = None,
    pmap_elabel: ReadPropertyMap = None,
    leaves: set = None,
    vis: DefaultRevuzMinimizeVisitor = None
) -> int:
    """
    Minimizes an acyclic automaton using the `Revuz algorithm <https://www.sciencedirect.com/science/article/pii/0304397592901423>`.

    Args:
        g (NodeAutomaton or Automaton): The automaton. It MUST be acyclic.
        pmap_vlabel (ReadPropertyMap): A ``ReadWritePropertyMap{int:  Symbol}``
            that maps each vertex with its symbol.
            If labeling is purely edge-based, pass ``None``.
            If ``g`` is an :py:class:`Automaton`, you may pass ``None``.
        pmap_elabel (ReadPropertyMap): A ``ReadWritePropertyMap{EdgeDescriptor:  Label}``.
            If labeling is purely vertex-based, pass ``None``.
            If g is a :py:class:`NodeAutomaton`, you may pass ``None``.
        leaves: The leaves of the IncidenceNodeAutomaton.
            Pass ``None`` to compute this set automatically.

    Returns:
        The height of g.
    """
    if not vis:
        vis = DefaultRevuzMinimizeVisitor()

    # Height are pre-computed to guarantee that a state is pushed in to_process
    # iff all its successors have already been processed.
    map_vheight = defaultdict(int)
    pmap_vheight = make_assoc_property_map(map_vheight)
    hmax = revuz_height(g, pmap_vheight)

    # Mappings
    if not pmap_vlabel and isinstance(g, IncidenceNodeAutomaton):
        pmap_vlabel = make_func_property_map(g.symbol)
    if not pmap_elabel:
        if isinstance(g, IncidenceAutomaton):
            pmap_elabel = make_func_property_map(g.label)
        elif isinstance(g, IncidenceNodeAutomaton):
            pmap_elabel = make_func_property_map(lambda e: pmap_vlabel[g.target(e)])
    assert pmap_vlabel or pmap_elabel

    def _make_signature(q: int) -> tuple:
        return (
            g.is_final(q),
            pmap_vlabel[q] if pmap_vlabel else None,
            frozenset({
                (
                    pmap_elabel[e] if pmap_elabel else None,
                    g.target(e)
                ) for e in g.out_edges(q)
            })
        )

    def _move_edge(e_old: EdgeDescriptor, q: int, r: int):
        a = pmap_elabel[e_old] if pmap_elabel else None
        g.remove_edge(e_old)
        e_merge = None
# Due to determinism, merging parents transitions should never be required.
#
#        for e in g.out_edges(q):
#            a_cur = pmap_elabel[e] if pmap_elabel else None
#            if a == a_cur: #vlabels always match (see signature)
#                e_merge = e
#                break
#
#        if e_merge:
#            vis.merge_transitions(e_old, e_merge, g)
#        else:
#            if isinstance(g, IncidenceNodeAutomaton):
#                (e_new, _) = g.add_edge(q, r)
#            else:
#                (e_new, _) = g.add_edge(q, r, a)
#            vis.move_transition(e_old, e_new, g)
        if isinstance(g, IncidenceNodeAutomaton):
            (e_new, _) = g.add_edge(q, r)
        else:
            (e_new, _) = g.add_edge(q, r, a)
        vis.move_transition(e_old, e_new, g)

    # Initialization
    h = 0
    to_process = leaves if leaves else {
        q
        for q in g.vertices()
        if g.out_degree(q) == 0
    }

    # Iteration
    while to_process:
        # Find aggregates
        map_aggregates = dict()
        for q in to_process:
            s = _make_signature(q)
            if s not in map_aggregates.keys():
                map_aggregates[s] = set()
            map_aggregates[s].add(q)

        # Merge aggregates
        for mergeable_states in map_aggregates.values():
            if len(mergeable_states) < 2:
                continue
            mergeable_states = sorted(mergeable_states) # Sort to get deterministic behavior
            q1 = mergeable_states[0]
            for q2 in mergeable_states[1:]:
                vis.merging_states(q1, q2, g)

                # Move each input transition (p -> q2) to (p -> q1)
                for e2 in {e for e in g.in_edges(q2)}:
                    p = g.source(e2)
                    _move_edge(e2, p, q1)

                # Remove q2, which is now isolated
                vis.remove_vertex(q2, g)
                g.remove_vertex(q2)
                vis.states_merged(q1, q2, g)

        to_process = set.union(*[{
            g.source(e)
            for q in to_process
            for e in g.in_edges(q)
            if pmap_vheight[g.source(e)] == h + 1
        }])
        h += 1
    return h - 1
