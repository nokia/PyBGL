#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from copy import copy
from .graph import Graph
from .graphviz import GraphvizStyle, enrich_kwargs, graphviz_type, to_dot

JSON_GRAPH_FORMAT = """{
    "graph_type" : "%(graph_type)s",
    "vertices" : %(vertices)s,
    "edges" : %(edges)s
}"""

JSON_NODE_FORMAT = """{
            "id" : %(id)s%(sep)s
            %(attributes)s
        }"""

JSON_EDGE_FORMAT = """{
            "source" : %(source)s,
            "target" : %(target)s%(sep)s
            %(attributes)s
        }"""

class GraphDp:
    """
    Graph dynamic properties, used to define the style of a graph.
    It allows to render graph to GraphViz.
    """
    def __init__(
        self,
        g: Graph,
        dpv: dict = None,
        dpe: dict = None,
        dg: dict = None,
        dv: dict = None,
        de: dict = None,
        extra_style: list = None
    ):
        """
        Constructor.

        Args:
            g (Graph): The wrapped graph.
            dpv (dict): Per-vertex style. It maps a vertex Graphviz attribute with the
                corresponding vertex-based :py:class:`ReadPropertyMap` instance.
            dpe (dict): Per-edge style. It maps a edge Graphviz attribute with the
                corresponding edge-based :py:class:`ReadPropertyMap` instance.
            dg (dict): Graph attributes.
            dv (dict): Default vertex style. It maps a vertex Graphviz attribute
                with the corresponding value.
            de (dict): Default edge style. It maps a edge Graphviz attribute
                with the corresponding value.
            extra_style (list): Extra style (splines, etc).
        """
        self.g = g
        self.dpv = dpv if dpv else dict() # Vertex attributes
        self.dpe = dpe if dpe else dict() # Edge attributes
        gs = GraphvizStyle()
        self.dg = dg if dg else copy(gs.graph)
        self.dv = dv if dv else copy(gs.node)
        self.de = de if de else copy(gs.edge)
        self.extra_style = extra_style if extra_style else copy(gs.extra_style)

    def get_dpv(self) -> dict:
        return self.dpv

    def get_dpe(self) -> dict:
        return self.dpve

    def get_dg(self) -> dict:
        return self.dg

    def get_dv(self) -> dict:
        return self.dv

    def get_de(self) -> dict:
        return self.de

    def to_dot(self, **kwargs) -> str:
        """
        Exports this :py:class:`GraphDp` instance to the corresponding GraphViz string.

        Returns:
            The corresponding GraphViz string.
        """
        kwargs = enrich_kwargs(self.dpv, "dpv", **kwargs)
        kwargs = enrich_kwargs(self.dpe, "dpe", **kwargs)
        kwargs = enrich_kwargs(self.dg, "dg", **kwargs)
        kwargs = enrich_kwargs(self.dv, "dv", **kwargs)
        kwargs = enrich_kwargs(self.de,  "de",  **kwargs)
        kwargs = enrich_kwargs(self.extra_style, "extra_style", **kwargs)
        return to_dot(self.g, **kwargs)

    # TODO GraphView
    def to_json(self, vs: iter = None, es: iter = None) -> str:
        """
        Exports the GraphViz rendering of this :py:class:`GraphDp` instance to JSON.

        Args:
            vs (iter): A subset of vertices of ``self.g``.
                You should rather use the :py:class:`GraphView` class.
            es (iter): A subset of edges of ``self.g``.
                You should rather use the :py:class:`GraphView` class.

        Returns:
            The corresponding JSON string.
        """

        if vs is None:
            vs = self.g.vertices()
        if es is None:
            es = self.g.edges()

        return JSON_GRAPH_FORMAT % {
            "graph_type" : graphviz_type(self.g),
            "vertices" : "[\n        %s\n    ]" % ", ".join([
                    JSON_NODE_FORMAT % {
                        "id" : u,
                        "attributes" : ",\n            ".join([
                            "\"%s\" : \"%s\"" % (k, pmap[u])
                            for k, pmap in self.dpv.items()
                        ]),
                        "sep" : "," if self.dpv else "",
                    } for u in vs
                ]),
            "edges" : "[\n        %s\n    ]" % ", ".join([
                    JSON_EDGE_FORMAT % {
                        "source" : self.g.source(e),
                        "target" : self.g.target(e),
                        "attributes" : ",\n            ".join([
                            "\"%s\" : \"%s\"" % (k, pmap[e])
                            for k, pmap in self.dpe.items()
                        ]),
                        "sep" : "," if self.dpe else "",
                    } for e in es
                ]
            )
        }
