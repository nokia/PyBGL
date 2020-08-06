#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob, Maxime Raynal"
__maintainer__ = "Marc-Olivier Buob, Maxime Raynal"
__email__      = "{marc-olivier.buob,maxime.raynal}@nokia.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from collections              import defaultdict

from pybgl.automaton          import final, initial, remove_vertex, vertices
from pybgl.depth_first_search import depth_first_search_graph, WHITE
from pybgl.property_map       import make_assoc_property_map
from pybgl.reverse            import reverse_graph

def find_reachable_vertices(g, sources):
    map_vcolor = defaultdict(int)
    pmap_vcolor = make_assoc_property_map(map_vcolor)
    depth_first_search_graph(g, sources, pmap_vcolor=pmap_vcolor)
    return set(map_vcolor.keys())

def prune_automaton(g):
    to_keep = find_reachable_vertices(g, {initial(g)})
    reverse_graph(g)
    to_keep &= find_reachable_vertices(g, final(g))
    reverse_graph(g)
    to_remove = set(vertices(g)) - to_keep
    for q in to_remove:
        remove_vertex(q, g)
