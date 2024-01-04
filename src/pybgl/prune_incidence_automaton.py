#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .graph import Graph
from .incidence_automaton import IncidenceAutomaton
from .depth_first_search import depth_first_search_graph
from .property_map import make_assoc_property_map
from .reverse import reverse_graph


def find_reachable_vertices(g: Graph, sources: set) -> set:
    """
    Returns the set of vertices of a graph which are reachable
    from a set of source vertices.
    Args:
        g: Graph, an instance of `Graph`
        sources: set, a set of integers representing the source vertices
    Returns:
        The set of vertices that are reachable from the source vertices
    """
    map_vcolor = defaultdict(int)
    pmap_vcolor = make_assoc_property_map(map_vcolor)
    depth_first_search_graph(g, sources, pmap_vcolor=pmap_vcolor)
    return set(map_vcolor.keys())


def prune_incidence_automaton(g: IncidenceAutomaton):
    """
    Prunes the vertices of an IncidenceAutomaton that cannot be reached
    from the initial state, or that cannot reach a final state.
    Args:
        g: IncidenceAutomaton, an instance of IncidenceAutomaton
    """
    to_keep = find_reachable_vertices(g, {g.initial()})
    reverse_graph(g)
    to_keep &= find_reachable_vertices(g, g.finals())
    reverse_graph(g)
    to_remove = set(g.vertices()) - to_keep
    for q in to_remove:
        g.remove_vertex(q)
