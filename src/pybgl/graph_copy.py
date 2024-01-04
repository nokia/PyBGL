#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from collections import defaultdict
from .graph import Graph, EdgeDescriptor
from .depth_first_search import depth_first_search
from .property_map import (
    ReadWritePropertyMap,
    ReadPropertyMap,
    make_assoc_property_map,
    make_func_property_map,
)
from .graph_extract import DepthFirstSearchExtractVisitor


class DepthFirstSearchCopyVisitor(DepthFirstSearchExtractVisitor):
    """
    The :py:class:`DepthFirstSearchCopyVisitor` implements the
    :py:func:`graph_copy` function.
    """
    def __init__(
        self,
        g_dup: Graph,
        pmap_vrelevant: ReadPropertyMap,
        pmap_erelevant: ReadPropertyMap,
        pmap_vertices: ReadWritePropertyMap,
        pmap_edges: ReadWritePropertyMap,
        pmap_vcolor: ReadWritePropertyMap,
        callback_dup_vertex: callable = None,
        callback_dup_edge: callable = None
    ):
        """
        Constructor.

        Args:
            g_dup: Pass an empty graph.
            pmap_vrelevant (ReadPropertyMap):
                A ``ReadPropertyMap{VertexDescriptor:  bool}``
                which indicates for each vertex whether if it must be
                duped or not.
            pmap_erelevant (ReadPropertyMap):
                A ``ReadPropertyMap{EdgeDescriptor:  bool}``
                which indicates for each edge whether it is relevant or not.
            pmap_vertices (ReadWritePropertyMap):
                A ``ReadWritePropertyMap{VertexDescriptor: VertexDescriptor}``
                which maps each vertex of ``g`` to the corresponding vertex in
                ``g_copy``. Pass an empty property map.
            pmap_edges (ReadWritePropertyMap):
                A ``ReadWritePropertyMap{EdgeDescriptor:  EdgeDescriptor}``
                which maps each edge of ``g`` with the corresponding edge in
                ``g_copy``. Pass ``None`` if unused, otherwise, pass an empty
                property map.
            pmap_vcolor (ReadWritePropertyMap):
                A ``ReadWritePropertyMap{VertexDescriptor:  Color}`` which maps
                each vertex with its status in the DFS walk.
                Pass an empty property map.
                See :py:func:`depth_first_search` for further details.
            callback_dup_vertex: A ``Callback(u, g, u_dup, g_dup)`` where:
                ``u`` is the original VertexDescriptor (in ``g``);
                ``g`` is the original DirectedGraph;
                ``u_dup`` is the duplicated VertexDescriptor (in ``g_dup``);
                ``g_dup`` is the duplicated DirectedGraph.;
                Pass ``None`` if unused.
            callback_dup_edge: A ``Callback(e, g, e_dup, g_dup)`` where:
                ``e`` is the original EdgeDescriptor (in ``g``);
                ``g`` is the original DirectedGraph;
                ``e_dup`` is the duplicated EdgeDescriptor (in ``g_dup``);
                ``g_dup`` is the duplicated DirectedGraph.;
                Pass ``None`` if unused.
        """
        super().__init__(pmap_vrelevant, pmap_erelevant, pmap_vcolor)
        self.callback_dup_vertex = callback_dup_vertex
        self.callback_dup_edge = callback_dup_edge
        self.g_dup = g_dup
        self.pmap_vertices = pmap_vertices
        self.pmap_edges = pmap_edges
        self.dup_vertices = set()  # Needed to keep track of pmap_vertices

    def dup_vertex(self, u: int, g: Graph) -> int:
        """
        Implementation method, used to duplicate a vertex.

        Args:
            u (int): The vertex descriptor of the duplicated node.
            g (Graph): The input graph.
        """
        u_dup = self.g_dup.add_vertex()
        self.pmap_vertices[u] = u_dup
        self.dup_vertices.add(u)
        if self.callback_dup_vertex:
            self.callback_dup_vertex(u, g, u_dup, self.g_dup)
        return u_dup

    def start_vertex(self, s: int, g: Graph):
        # Overloaded method
        self.dup_vertex(s, g)

    def examine_relevant_edge(self, e: EdgeDescriptor, g: Graph):
        # Overloaded method
        u = g.source(e)
        v = g.target(e)
        u_dup = self.pmap_vertices[u]
        v_dup = (
            self.pmap_vertices[v] if v in self.dup_vertices
            else self.dup_vertex(v, g)
        )
        (e_dup, _) = self.g_dup.add_edge(u_dup, v_dup)
        if self.pmap_edges:
            self.pmap_edges[e] = e_dup
        if self.callback_dup_edge:
            self.callback_dup_edge(e, g, e_dup, self.g_dup)


def graph_copy(
    s: int,
    g: Graph,
    g_dup: Graph,
    pmap_vrelevant: ReadPropertyMap = None,
    pmap_erelevant: ReadPropertyMap = None,
    pmap_vertices: ReadWritePropertyMap = None,
    pmap_edges: ReadWritePropertyMap = None,
    callback_dup_vertex: callable = None,
    callback_dup_edge: callable = None
):
    """
    Copies a sub-graph from a Graph according to an edge-based filtering
    starting from a given source node.

    Args:
        s: The VertexDescriptor of the source node.
        g: A Graph instance.
        pmap_vrelevant (ReadPropertyMap):
            A ``ReadPropertyMap{VertexDescriptor: bool}``
            which indicates for each vertex whether if it must be duped
            or not. Only relevant if ``vis == None``.
        pmap_erelevant (ReadPropertyMap):
            A ``ReadPropertyMap{EdgeDescriptor: bool}`` which indicates
            for each edge whether if it must be duped or not.
            Only used if ``vis == None``.
        callback_dup_vertex (callable): A ``Callback(u, g, u_dup, g_dup)``.
            Pass ``None`` if irrelevant.
        callback_dup_edge (callable): A ``Callback(e, g, e_dup, g_dup)``.
            Pass ``None`` if irrelevant.
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
        map_vertices = defaultdict(None)
        pmap_vertices = make_assoc_property_map(map_vertices)
    if not pmap_edges:
        map_edges = defaultdict(None)
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
        if_push=lambda e, g: pmap_erelevant[e] and pmap_vrelevant[g.target(e)]
    )
