#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict

from .automaton import Automaton, EdgeDescriptor
from .depth_first_search import depth_first_search
from .property_map import (
    ReadWritePropertyMap,
    ReadPropertyMap,
    make_assoc_property_map,
    make_func_property_map,
)
from .graph_copy import DepthFirstSearchCopyVisitor


# NOTE: This almost the same than graph_copy, but we have to manage
# here the signature of add_edge, which differs :(

class AutomatonCopyVisitor(DepthFirstSearchCopyVisitor):
    """
    The :py:class:`AutomatonCopyVisitor` is the internal visitor
    used in :py:func:`automaton_copy`.
    """
    def __init__(self, *args):
        """
        Constructor.
        """
        super().__init__(*args)

    def examine_relevant_edge(self, e: EdgeDescriptor, g: Automaton):
        """
        Method triggered when examining a relevant edge.

        Args:
            e (EdgeDescriptor): The examined edge.
            g (Automaton) The processed :py:class:`Automaton` instance.
        """
        u = g.source(e)
        v = g.target(e)
        a = g.label(e)
        u_dup = self.pmap_vertices[u]
        v_dup = (
            self.pmap_vertices[v] if v in self.dup_vertices else
            self.dup_vertex(v, g)
        )
        (e_dup, _) = self.g_dup.add_edge(u_dup, v_dup, a)
        if self.pmap_edges:
            self.pmap_edges[e] = e_dup
        if self.callback_dup_edge:
            self.callback_dup_edge(e, g, e_dup, self.g_dup)


def automaton_copy(
    s: int,
    g: Automaton,
    g_dup: Automaton,
    pmap_vrelevant: ReadPropertyMap = None,
    pmap_erelevant: ReadPropertyMap = None,
    pmap_vertices: ReadWritePropertyMap = None,
    pmap_edges: ReadWritePropertyMap = None,
    callback_dup_vertex: callable = None,
    callback_dup_edge: callable = None
):
    """
    Copies a sub-graph from an Automaton according to an edge-based filtering
    starting from a given source node.

    Args:
        s (int): The VertexDescriptor of the source node.
        g (Automaton): An Automaton instance.
        pmap_vrelevant (ReadPropertyMap):
            A ``ReadPropertyMap{VertexDescriptor : bool}`` which
            maps each vertex whether to a boolean indicating if it must be
            duped or not.
        pmap_erelevant (ReadPropertyMap):
            A ``ReadPropertyMap{EdgeDescriptor : bool}`` which
            maps each edge whether to a boolean indicating if it must be
            duped or not.
        callback_dup_vertex (callable): A Callback(u, g, u_dup, g_dup).
            Pass ``None`` if irrelevant.
        callback_dup_edge (callable): A Callback(e, g, e_dup, g_dup).
            Pass ``None`` if irrelevant.
    """
    # Prepare the needed mappings.
    map_vcolor = defaultdict(int)
    pmap_vcolor = make_assoc_property_map(map_vcolor)

    if not pmap_vrelevant:
        pmap_vrelevant = make_func_property_map(lambda u: True)
    if not pmap_erelevant:
        pmap_erelevant = make_func_property_map(lambda e: True)

    # Prepare the AutomatonCopyVisitor
    if not pmap_vertices:
        map_vertices = dict()
        pmap_vertices = make_assoc_property_map(map_vertices)
    if not pmap_edges:
        map_edges = dict()
        pmap_edges = make_assoc_property_map(map_edges)

    vis = AutomatonCopyVisitor(
        g_dup,
        pmap_vrelevant,
        pmap_erelevant,
        pmap_vertices,
        pmap_edges,
        pmap_vcolor,
        callback_dup_vertex,
        callback_dup_edge
    )

    # Copy g to g_copy according to pmap_erelevant using a DFS from s.
    depth_first_search(
        s, g, pmap_vcolor, vis,
        if_push=lambda e, g: pmap_erelevant[e] and pmap_vrelevant[g.target(e)]
    )
