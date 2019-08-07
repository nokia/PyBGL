#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from collections                import defaultdict

from pybgl.automaton            import Automaton, EdgeDescriptor, add_vertex, add_edge, label, out_edges, source, target
from pybgl.depth_first_search   import depth_first_search
from pybgl.property_map         import ReadWritePropertyMap, ReadPropertyMap, make_assoc_property_map, make_func_property_map
from pybgl.graph_copy           import DepthFirstSearchCopyVisitor as DepthFirstSearchCopyVisitor_

# NOTE: This almost the same than graph_copy, but we have to manage here the signature of add_edge, which differs :(

class DepthFirstSearchCopyVisitor(DepthFirstSearchCopyVisitor_):
    def __init__(self, *args):
        super().__init__(*args)

    def examine_relevant_edge(self, e :EdgeDescriptor, g :Automaton):
        u = source(e, g)
        v = target(e, g)
        a = label(e, g)
        u_dup = self.m_pmap_vertices[u]
        v_dup = self.m_pmap_vertices[v] if v in self.m_dup_vertices else self.dup_vertex(v, g)
        (e_dup, _) = add_edge(u_dup, v_dup, a, self.m_g_dup)
        if self.m_pmap_edges:
            self.m_pmap_edges[e] = e_dup
        if self.m_callback_dup_edge:
            self.m_callback_dup_edge(e, g, e_dup, self.m_g_dup)

def automaton_copy(
    s                   :int,
    g                   :Automaton,
    g_dup               :Automaton,
    pmap_vrelevant      :ReadPropertyMap = None,
    pmap_erelevant      :ReadPropertyMap = None,
    pmap_vertices       :ReadWritePropertyMap = None,
    pmap_edges          :ReadWritePropertyMap = None,
    callback_dup_vertex = None,
    callback_dup_edge   = None
):
    """
    Copy a sub-graph from an Automaton according to an edge-based filtering
    starting from a given source node.
    Args:
        s: The VertexDescriptor of the source node.
        g: An Automaton instance.
        pmap_vrelevant: A ReadPropertyMap{VertexDescriptor : bool} which indicates
            for each vertex whether if it must be duped or not.
            Only used if vis == None.
        pmap_erelevant: A ReadPropertyMap{EdgeDescriptor : bool} which indicates
            for each edge whether if it must be duped or not.
            Only used if vis == None.
        callback_dup_vertex: Callback(u, g, u_dup, g_dup).
            Pass None if irrelevant.
        callback_dup_edge: Callback(e, g, e_dup, g_dup).
            Pass None if irrelevant.
        vis: Pass a custom DepthFirstSearchExtractVisitor or None.
            This visitor must overload super()'s methods.
    """
    # Prepare the needed mappings.
    map_vcolor = defaultdict(int)
    pmap_vcolor = make_assoc_property_map(map_vcolor)

    if not pmap_vrelevant:
        pmap_vrelevant = make_func_property_map(lambda u: True)
    if not pmap_erelevant:
        pmap_erelevant = make_func_property_map(lambda e: True)

    # Prepare the DepthFirstSearchCopyVisitor.
    if not pmap_vertices:
        map_vertices = dict()
        pmap_vertices = make_assoc_property_map(map_vertices)
    if not pmap_edges:
        map_edges = dict()
        pmap_edges = make_assoc_property_map(map_edges)

    vis = DepthFirstSearchCopyVisitor(
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
        if_push = lambda e, g: pmap_erelevant[e] and pmap_vrelevant[target(e, g)]
    )

