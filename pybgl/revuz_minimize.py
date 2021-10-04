#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob, Achille Salaün, Anne Bouillard"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"


from collections import defaultdict
from pybgl.incidence_automaton      import IncidenceAutomaton, label
from pybgl.property_map             import \
    ReadPropertyMap, ReadWritePropertyMap, \
    make_assoc_property_map, make_func_property_map
from pybgl.incidence_node_automaton import \
    IncidenceNodeAutomaton, EdgeDescriptor, \
    delta, in_edges, is_final, out_degree, out_edges, \
    remove_edge, remove_vertex, source, symbol, target, vertices

class DefaultRevuzMinimizeVisitor:
    def __init__(self): pass
    def start(self, g :IncidenceNodeAutomaton): pass
    def merging_states(self, q1 :int, q2 :int, g :IncidenceNodeAutomaton): pass
    def move_transition(self, e_old :EdgeDescriptor, e_new :EdgeDescriptor, g :IncidenceNodeAutomaton): pass
#    def merge_transitions(self, e_old :EdgeDescriptor, e_merge :EdgeDescriptor, g :IncidenceNodeAutomaton): pass
    def remove_vertex(self, u :int, g :IncidenceNodeAutomaton): pass
    def states_merged(self, q1 :int, q2 :int, g :IncidenceNodeAutomaton): pass

class DebugRevuzMinimizeVisitor(DefaultRevuzMinimizeVisitor):
    def __init__(self):
        super().__init__()
    def start(self, g :IncidenceNodeAutomaton):
        print("start()")
    def merging_states(self, q1 :int, q2 :int, g :IncidenceNodeAutomaton):
        print("merging_states(%s, %s)" % (q1, q2))
#    def merge_transitions(self, e_old :EdgeDescriptor, e_merge :EdgeDescriptor, g :IncidenceNodeAutomaton):
#        print("merge_transitions(%s, %s)" % (e_old, e_merge))
    def move_transition(self, e_old :EdgeDescriptor, e_new :EdgeDescriptor, g :IncidenceNodeAutomaton):
        print("move_transition(%s, %s)" % (e_old, e_new))
    def remove_vertex(self, u :int, g :IncidenceNodeAutomaton):
        print("remove_vertex(%s)" % (u))
    def states_merged(self, q1 :int, q2 :int, g :IncidenceNodeAutomaton):
        print("states_merged(%s, %s)" % (q1, q2))

def revuz_height(g :IncidenceNodeAutomaton, pmap_vheight :ReadWritePropertyMap, leaves = None) -> int:
    """
    Compute the height of each vertex starting from its leaves. Leaves have height equal to 0.
    Args:
        g: The input IncidenceNodeAutomaton. The graph MUST be acyclic.
        pmap_vheight: A ReadWritePropertyMap{VertexDescriptor : int} which maps
            each vertex with its height.
        leaves: The leaves of the IncidenceNodeAutomaton. Pass None to compute this set automatically.
    Returns:
        The max height.
    """
    h = 0
    vertices_to_process = leaves if leaves else {q for q in vertices(g) if out_degree(q, g) == 0}

    while vertices_to_process:
        next_vertices_to_process = set()
        for v in vertices_to_process:
            # pmap_vheight[v] = max(pmap_vheight[v], h). Note that max is not needed
            # according to the traversal order.
            pmap_vheight[v] = h
            for e in in_edges(v, g):
                u = source(e, g)
                next_vertices_to_process.add(u)
        vertices_to_process = next_vertices_to_process
        h += 1
    return h - 1

def revuz_minimize(
    g            :IncidenceNodeAutomaton,
    pmap_vlabel  :ReadPropertyMap             = None,
    pmap_elabel  :ReadPropertyMap             = None,
    leaves       :set                         = None,
    vis          :DefaultRevuzMinimizeVisitor = None
):
    """
    Compute the height of each vertex starting from its leaves. Leaves have height equal to 0.
    Args:
        g: The input IncidenceNodeAutomaton or IncidenceAutomaton. The graph MUST be acyclic.
        pmap_vlabel: A ReadWritePropertyMap{int : Symbol}.
            If labeling is purely edge-based, pass None.
            If g is an IncidenceNodeAutomaton or an IncidenceAutomaton, you may pass None.
        pmap_elabel: A ReadWritePropertyMap{EdgeDescriptor : Label}.
            If labeling is purely node-based, pass None.
            If g is an IncidenceNodeAutomaton or an IncidenceAutomaton, you may pass None.
        pmap_vheight: Optional ReadWritePropertyMap{VertexDescriptor : int} which maps
            each vertex with its height.
        leaves: The leaves of the IncidenceNodeAutomaton.
            Pass None to compute this set automatically.
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
        pmap_vlabel = make_func_property_map(lambda q: symbol(q, g))
    if not pmap_elabel:
        if isinstance(g, IncidenceAutomaton):
            pmap_elabel = make_func_property_map(lambda e: label(e, g))
        elif isinstance(g, IncidenceNodeAutomaton):
            pmap_elabel = make_func_property_map(lambda e: pmap_vlabel[target(e, g)])
    assert pmap_vlabel or pmap_elabel

    # Internals
    if isinstance(g, IncidenceAutomaton):
        from pybgl.incidence_automaton import add_edge
    else:
        from pybgl.incidence_node_automaton import add_edge

    def _make_signature(q :int) -> tuple:
        return (
            is_final(q, g),
            pmap_vlabel[q] if pmap_vlabel else None,
            frozenset({
                (
                    pmap_elabel[e] if pmap_elabel else None,
                    target(e, g)
                ) for e in out_edges(q, g)
            })
        )

    def _move_edge(e_old :EdgeDescriptor, q :int, r :int):
        a = pmap_elabel[e_old] if pmap_elabel else None
        remove_edge(e_old, g)
        e_merge = None
# Due to determinism, merging parents transitions should never be required.
#
#        for e in out_edges(q, g):
#            a_cur = pmap_elabel[e] if pmap_elabel else None
#            if a == a_cur: #vlabels always match (see signature)
#                e_merge = e
#                break
#
#        if e_merge:
#            vis.merge_transitions(e_old, e_merge, g)
#        else:
#            if isinstance(g, IncidenceNodeAutomaton):
#                (e_new, _) = add_edge(q, r, g)
#            else:
#                (e_new, _) = add_edge(q, r, a, g)
#            vis.move_transition(e_old, e_new, g)
        if isinstance(g, IncidenceNodeAutomaton):
            (e_new, _) = add_edge(q, r, g)
        else:
            (e_new, _) = add_edge(q, r, a, g)
        vis.move_transition(e_old, e_new, g)

    # Initialization
    h = 0
    to_process = leaves if leaves else {q for q in vertices(g) if out_degree(q, g) == 0}
    vis.start(g)

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
                for e2 in {e for e in in_edges(q2, g)}:
                    p = source(e2, g)
                    _move_edge(e2, p, q1)

                # Remove q2, which is now isolated
                vis.remove_vertex(q2, g)
                remove_vertex(q2, g)
                vis.states_merged(q1, q2, g)

        to_process = set.union(*[{
            source(e, g)
            for q in to_process
            for e in in_edges(q, g)
            if pmap_vheight[source(e, g)] == h + 1
        }])
        h += 1
    return h - 1
