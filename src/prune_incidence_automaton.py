#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob, Maxime Raynal"
__maintainer__ = "Marc-Olivier Buob, Maxime Raynal"
__email__      = "{marc-olivier.buob,maxime.raynal}@nokia.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from collections               import defaultdict

from pybgl.graph               import Graph
from pybgl.incidence_automaton import (
    IncidenceAutomaton, finals, initial, remove_vertex, vertices
)
from pybgl.depth_first_search  import depth_first_search_graph
from pybgl.property_map        import make_assoc_property_map
from pybgl.reverse             import reverse_graph

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
    from the intial state, or that cannot reach a final state.
    Args:
        g: IncidenceAutomaton, an instance of IncidenceAutomaton
    """
    to_keep = find_reachable_vertices(g, {initial(g)})
    reverse_graph(g)
    to_keep &= find_reachable_vertices(g, finals(g))
    reverse_graph(g)
    to_remove = set(vertices(g)) - to_keep
    for q in to_remove:
        remove_vertex(q, g)
