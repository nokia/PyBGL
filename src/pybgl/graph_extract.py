#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict

from .graph import Graph, EdgeDescriptor
from .depth_first_search import BLACK, DefaultDepthFirstSearchVisitor, depth_first_search
from .property_map import (
    ReadWritePropertyMap, ReadPropertyMap,
    make_assoc_property_map, make_func_property_map
)

# TODO GraphView
class DepthFirstSearchExtractVisitor(DefaultDepthFirstSearchVisitor):
    """
    The :py:class:`DepthFirstSearchExtractVisitor`
    limits the DFS walk to traverse only relevant arcs.

    See also the :py:class:`DepthFirstSearchCopyVisitor` class.
    """
    def __init__(
        self,
        pmap_vrelevant: ReadPropertyMap,
        pmap_erelevant: ReadPropertyMap,
        pmap_vcolor: ReadWritePropertyMap,
        callback_vertex_extract: callable = None,
        callback_edge_extract: callable = None
    ):
        """
        Constructor.

        Args:
            pmap_vrelevant (ReadPropertyMap): A
                ``ReadPropertyMap{VertexDescriptor: bool}`` which indicates
                for each vertex whether if it must be duped or not.
                You shoud consider the :py:class:`GraphView` class.
            pmap_erelevant (ReadPropertyMap): A
                ``ReadPropertyMap{EdgeDescriptor: bool}`` which indicates
                for each edge whether it is relevant or not.
                You shoud consider the :py:class:`GraphView` class.
            pmap_vcolor (ReadWritePropertyMap): A
                ``ReadWritePropertyMap{VertexDescriptor: Color}`` which maps
                each vertex with its status in the DFS walk.
                See the :py:func:`depth_first_search` function.
            callback_vertex_extract (callable): Callback triggered when discovering
                a vertex to extract.
            callback_edge_extract (callable): Callback triggered when discovering
                an edge to extract.
        """
        super().__init__()
        self.m_pmap_vrelevant = pmap_vrelevant
        self.m_pmap_erelevant = pmap_erelevant
        self.m_pmap_vcolor = pmap_vcolor
        self.m_callback_vertex_extract = callback_vertex_extract
        self.m_callback_edge_extract = callback_edge_extract

    def discover_vertex(self, u: int, g: Graph):
        """
        Method invoked when the DFS discover a relevant vertex not yet visited.

        Args:
            u (int): The discovered vertex.
            g (Graph): The considered graph.
        """
        if self.m_callback_vertex_extract:
            self.m_callback_vertex_extract(u, g)

    def examine_relevant_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method triggered when discovering a relevant edge not yet visited.

        Args:
            e (EdgeDescriptor): The discovered edge.
            g (Graph): The considered graph.
        """
        if self.m_callback_edge_extract:
            self.m_callback_edge_extract(e, g)

    def examine_edge(self, e: EdgeDescriptor, g: Graph):
        """
        Method invoked when the DFS discover a vertex not yet visited.

        Args:
            e (EdgeDescriptor): The discovered edge.
            g (Graph): The considered graph.
        """
        if self.m_pmap_erelevant[e] and self.m_pmap_vrelevant[g.target(e)]:
            self.examine_relevant_edge(e, g)

# TODO GraphView
def graph_extract(
    s: int,
    g: Graph,
    pmap_vrelevant = None,
    pmap_erelevant = None,
    callback_vertex_extract = None,
    callback_edge_extract = None
):
    """
    Extract the edges of a given Graph according to an edge-based filtering starting
    from a given source node.

    Args:
        s: The VertexDescriptor of the source node.
        g: A Graph instance.
        pmap_vrelevant: A ReadPropertyMap{VertexDescriptor:  bool} which indicates
            for each vertex whether if it must be duped or not.
            You shoud consider the :py:class:`GraphView` class.
        pmap_erelevant: A ReadPropertyMap{EdgeDescriptor:  bool} which indicates
            each edge of the Graph with a boolean equal to True iff the edge is relevant.
            You shoud consider the :py:class:`GraphView` class.
        callback_vertex_extract (callable): Callback triggered when discovering
            a vertex to extract.
        callback_edge_extract (callable): Callback triggered when discovering
            an edge to extract.
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
        if_push = lambda e, g: pmap_erelevant[e] and pmap_vrelevant[g.target(e)]
    )
