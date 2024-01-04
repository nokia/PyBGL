#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from functools import reduce
from .property_map import make_assoc_property_map
from .incidence_automaton import IncidenceAutomaton


def hopcroft_agglomerate_states(g: IncidenceAutomaton) -> set:
    """
    Initialization step of the
    `Hopcroft minimization algorithm
    <https://fr.wikipedia.org/wiki/Algorithme_de_Hopcroft_de_minimisation_d%27un_automate_fini>`__.

    Args:
        g (IncidenceAutomaton): The input automaton.

    Returns:
        A set of frozensets, where each of them corresponds
        to a group of agglomerated states.
    """
    def union(sets) -> set:
        return reduce(lambda a, b: a | b, sets)

    g_alphabet = g.alphabet()
    final_states = {q for q in g.vertices() if g.is_final(q)}
    aggregated_states = {
        frozenset(final_states),
        frozenset(g.vertices()) - final_states
    }
    waiting_states = {
        frozenset(final_states),
        frozenset(g.vertices()) - final_states
    }
    while waiting_states != set():
        current_states = waiting_states.pop()
        for a in g_alphabet:
            x = union(
                frozenset(
                    g.source(e)
                    for e in g.in_edges(r)
                    if g.label(e) == a
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


def hopcroft_minimize(g: IncidenceAutomaton) -> IncidenceAutomaton:
    """
    Runs the Hopcroft minimization algorithm.

    Args:
        g (IncidenceAutomaton): The input automaton.

    Returns:
        The minimized automaton.
    """
    if not g.has_vertex():
        return g
    aggregated_states = list(hopcroft_agglomerate_states(g))

    # Find the aggregated state corresponding to the initial state
    q0 = None
    for idx, qs in enumerate(aggregated_states):
        if any(g.is_initial(q) for q in qs):
            q0 = idx
            break
    assert q0 is not None

    # Swap q0 and 0 so that the initial state is 0.
    if q0 != 0:
        tmp = aggregated_states[0]
        aggregated_states[0] = aggregated_states[q0]
        aggregated_states[q0] = tmp
    q0 = 0

    # Assign an index to each state in the new automaton
    map_set_idx = {
        qs: idx
        for idx, qs in enumerate(list(aggregated_states))
    }

    # Build the set of final states in the new automaton
    final_states_new = defaultdict(
        bool,
        {
            map_set_idx[qs]: True if any(g.is_final(q) for q in qs) else False
            for qs in aggregated_states
        }
    )
    # Build the minimized automaton
    min_g = IncidenceAutomaton(
        len(aggregated_states),
        q0,
        make_assoc_property_map(final_states_new)
    )
    for qs in aggregated_states:
        for q in qs:
            for e in g.out_edges(q):
                r = g.target(e)
                a = g.label(e)
                rs = None
                for rs in aggregated_states:
                    if r in rs:
                        break
                min_g.add_edge(map_set_idx[qs], map_set_idx[rs], a)
    return min_g
