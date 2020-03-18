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
from pybgl.incidence_automaton import IncidenceAutomaton, alphabet, \
    vertices, is_final, label, source, target, in_edges, is_initial, \
    make_incidence_automaton, out_edges, add_edge


def hopcroft_agglomerate_states(g: IncidenceAutomaton) -> set:
    """Agglomerates the states of an automaton
    Args:
        g: IncidenceAutomaton
    Returns:
        agg_states: a set of frozensets, which represents
                    the agglomerated states
    """
    g_alphabet = alphabet(g)
    final_states = {q for q in vertices(g) if is_final(q, g)}
    agg_states = {
        frozenset(final_states), frozenset(vertices(g)) - final_states
    }
    wait_list = {
        frozenset(final_states), frozenset(vertices(g)) - final_states
    }
    while wait_list != set():
        current_states = wait_list.pop()
        for a in g_alphabet:
            print("%s; %s; __" % (current_states, a))
            print("w:%s" % wait_list)
            print("agg: %s" % agg_states)
            x = frozenset(reduce(
                lambda a, b: a | b,
                (
                    {source(e, g) for e in in_edges(r, g) if label(e, g) == a}
                    for r in current_states
                )
            ))
            print("x: %s" % x)
            new_agg_states = set(agg_states)
            for y in agg_states:
                if len(x & y) > 0 and len(y - x) > 0:
                    new_agg_states.remove(y)
                    new_agg_states.add(frozenset(x & y))
                    new_agg_states.add(frozenset(y - x))
                    if y in wait_list:
                        wait_list.remove(y)
                        wait_list.add(frozenset(x & y))
                        wait_list.add(frozenset(y - x))
                    elif len(x & y) <= len(y - x):
                        wait_list.add(frozenset(x & y))
                    else:
                        wait_list.add(frozenset(y - x))
            agg_states = new_agg_states
    return agg_states

def hopcroft_minimize(g: IncidenceAutomaton) -> IncidenceAutomaton:
    agg_states = hopcroft_agglomerate_states(g)
    map_set_idx = {qs: idx for idx, qs in enumerate(list(agg_states))}
    new_q0 = {
        map_set_idx[qs] for qs in agg_states
        if any(is_initial(q, g) for q in qs)
    }.pop()
    new_finals = defaultdict(
        bool,
        {
            map_set_idx[qs]: True if any(is_final(q, g) for q in qs)
            else False
            for qs in agg_states
        }
    )
    min_g = IncidenceAutomaton(
        len(agg_states),
        new_q0,
        make_assoc_property_map(new_finals)
    )
    for qs in agg_states:
        for q in qs:
            for e in out_edges(q, g):
                r, a = target(e, g), label(e, g)
                rs = {_ for _ in agg_states if r in _}.pop()
                add_edge(map_set_idx[qs], map_set_idx[rs], a, min_g)
    return min_g
