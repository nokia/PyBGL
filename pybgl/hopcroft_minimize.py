#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Maxime Raynal"
__maintainer__ = "Maxime Raynal"
__email__      = "maxime.raynal@nokia.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from collections import defaultdict
from functools import reduce
from pybgl.property_map import make_assoc_property_map
from pybgl.incidence_automaton import (
    IncidenceAutomaton, alphabet, add_edge, is_final, label,
    source, target, in_edges, is_initial,
    make_incidence_automaton, out_edges, num_vertices, vertices
)

def is_empty(g) -> bool:
    for u in vertices(g):
        return False
    return True

def hopcroft_agglomerate_states(g: IncidenceAutomaton) -> set:
    """Agglomerates the states of an automaton
    Args:
        g: IncidenceAutomaton
    Returns:
        aggregated_states: a set of frozensets, which represents
                    the agglomerated states
    """
    def union(sets) -> set:
        return reduce(lambda a, b: a | b, sets)

    g_alphabet = alphabet(g)
    final_states = {q for q in vertices(g) if is_final(q, g)}
    aggregated_states = {
        frozenset(final_states), frozenset(vertices(g)) - final_states
    }
    waiting_states = {
        frozenset(final_states), frozenset(vertices(g)) - final_states
    }
    while waiting_states != set():
        current_states = waiting_states.pop()
        for a in g_alphabet:
            x = union(
                frozenset(
                    source(e, g) for e in in_edges(r, g) if label(e, g) == a
                ) for r in current_states
            )
            new_aggregated_states = set(aggregated_states)
            for y in aggregated_states:
                if len(x & y) > 0 and len(y - x) > 0:
                    new_aggregated_states.remove(y)
                    new_aggregated_states |= {x & y, y - x}
                    if y in waiting_states:
                        waiting_states.remove(y)
                        waiting_states |= {x & y, y - x}
                    elif len(x & y) <= len(y - x):
                        waiting_states.add(x & y)
                    else:
                        waiting_states.add(y - x)
            aggregated_states = new_aggregated_states
    return aggregated_states


def hopcroft_minimize(g :IncidenceAutomaton) -> IncidenceAutomaton:
    if is_empty(g):
        return g
    aggregated_states = list(hopcroft_agglomerate_states(g))
    # Make sure that the initial state in the minimized automaton will be 0
    for idx, qs in enumerate(aggregated_states):
        if any(is_initial(q, g) for q in qs):
            q0_new = idx
            break
    tmp = aggregated_states[0]
    aggregated_states[0] = aggregated_states[q0_new]
    aggregated_states[q0_new] = tmp
    q0_new = 0
    # Assign an index to each state in the new automaton
    map_set_idx = {qs: idx for idx, qs in enumerate(list(aggregated_states))}
    # Build the set of final states in the new automaton
    final_states_new = defaultdict(
        bool,
        {
            map_set_idx[qs]: True if any(is_final(q, g) for q in qs) else False
            for qs in aggregated_states
        }
    )
    # Build the minimized automaton
    min_g = IncidenceAutomaton(
        len(aggregated_states),
        q0_new,
        make_assoc_property_map(final_states_new)
    )
    for qs in aggregated_states:
        for q in qs:
            for e in out_edges(q, g):
                r = target(e, g)
                a = label(e, g)
                rs = None
                for rs in aggregated_states:
                    if r in rs:
                        break
                add_edge(map_set_idx[qs], map_set_idx[rs], a, min_g)
    return min_g
