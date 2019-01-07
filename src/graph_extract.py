#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from collections                import defaultdict

from pybgl.graph                import Graph, EdgeDescriptor, out_edges, target
from pybgl.depth_first_search   import BLACK, DefaultDepthFirstSearchVisitor, depth_first_search
from pybgl.property_map         import ReadWritePropertyMap, ReadPropertyMap, make_assoc_property_map, make_func_property_map

class DepthFirstSearchExtractVisitor(DefaultDepthFirstSearchVisitor):
    """
    This Visitor limits the DFS walk to traverse only relevant arcs.
    """
    def __init__(
        self,
        pmap_vrelevant          :ReadPropertyMap,
        pmap_erelevant          :ReadPropertyMap,
        pmap_vcolor             :ReadWritePropertyMap,
        callback_vertex_extract = None,
        callback_edge_extract   = None
    ):
        """
        Constructor.
        Args:
            pmap_vrelevant: A ReadPropertyMap{VertexDescriptor : bool} which indicates
                for each vertex whether if it must be duped or not.
            pmap_erelevant: A ReadPropertyMap{EdgeDescriptor : bool} which indicates
                for each edge whether it is relevant or not.
            pmap_vcolor: A ReadWritePropertyMap{VertexDescriptor : Color} which maps
                each vertex with its status in the DFS walk. See pybgl.depth_first_search for
                further details.
            callback_vertex_extract:
            callback_edge_extract:
        """
        super().__init__()
        self.m_pmap_vrelevant = pmap_vrelevant
        self.m_pmap_erelevant = pmap_erelevant
        self.m_pmap_vcolor    = pmap_vcolor
        self.m_callback_vertex_extract = callback_vertex_extract
        self.m_callback_edge_extract   = callback_edge_extract

    def discover_vertex(self, u :int, g :Graph):
        """
        Event triggered when the DFS discover a vertex not yet visited.
        Args:
            u: The VertexDescriptor of the discovered vertex.
            g: The Graph.
        """
        if self.m_callback_vertex_extract:
            self.m_callback_vertex_extract(u, g)

    def examine_relevant_edge(self, e :EdgeDescriptor, g :Graph):
        if self.m_callback_edge_extract:
            self.m_callback_edge_extract(e, g)

    def examine_edge(self, e :EdgeDescriptor, g :Graph):
        """
        Event triggered when the DFS discover a vertex not yet visited.
        Args:
            e: The EdgeDescriptor of the discovered vertex.
            g: The Graph.
        """
        if self.m_pmap_erelevant[e] and self.m_pmap_vrelevant[target(e, g)]:
            self.examine_relevant_edge(e, g)

def graph_extract(
    s                       :int,
    g                       :Graph,
    pmap_vrelevant          = None,
    pmap_erelevant          = None,
    callback_vertex_extract = None,
    callback_edge_extract   = None
):
    """
    Extract the edges of a given Graph according to an edge-based filtering starting
    from a given source node.
    Args:
        s: The VertexDescriptor of the source node.
        g: A Graph instance.
        pmap_vrelevant: A ReadPropertyMap{VertexDescriptor : bool} which indicates
            for each vertex whether if it must be duped or not.
        pmap_erelevant: A ReadPropertyMap{EdgeDescriptor : bool} which indicates
            each edge of the Graph with a boolean equal to True iff the edge is relevant.
        callback_vertex_extract:
        callback_edge_extract:
    """
    if not pmap_vrelevant:
        pmap_vrelevant = make_func_property_map(lambda u: True)
    if not pmap_erelevant:
        pmap_erelevant = make_func_property_map(lambda e: True)

    map_vcolor = defaultdict(int)
    pmap_vcolor = make_assoc_property_map(map_vcolor)
    vis = DepthFirstSearchExtractVisitor(
        pmap_vrelevant,
        pmap_erelevant,
        pmap_vcolor,
        callback_vertex_extract,
        callback_edge_extract
    )
    depth_first_search(
        s, g, pmap_vcolor, vis,
        if_push = lambda e, g: pmap_erelevant[e] and pmap_vrelevant[target(e, g)]
    )
