#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Graph dynamic properties
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from copy       import copy
from .graph     import Graph, edges, source, target, vertices
from .graphviz  import GraphvizStyle, enrich_kwargs, graphviz_type, to_dot

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
    def __init__(
        self,
        g   :Graph,
        dpv :dict = None, # Vertex attributes
        dpe :dict = None, # Edge attributes
        dg  :dict = None, # Graph attributes
        dv  :dict = None, # Vertex default attributesde  :dict = None,
        de  :dict = None, # Edge default attributesde  :dict = None,
        extra_style :list = None  # Extra style (splines etc)
    ):
        self.g = g
        self.dpv = dpv if dpv else dict() # Vertex attributes
        self.dpe = dpe if dpe else dict() # Edge attributes
        gs = GraphvizStyle()
        self.dg  = dg  if dg  else copy(gs.graph)
        self.dv  = dv  if dv  else copy(gs.node)
        self.de  = de  if de  else copy(gs.edge)
        self.extra_style = extra_style if extra_style else copy(gs.extra_style)

    def get_dpv(self) -> dict: return self.dpv
    def get_dpe(self) -> dict: return self.dpve
    def get_dg(self) -> dict: return self.dg
    def get_dv(self) -> dict: return self.dv
    def get_de(self) -> dict: return self.de

    def to_dot(self, **kwargs) -> str:
        kwargs = enrich_kwargs(self.dpv, "dpv", **kwargs)
        kwargs = enrich_kwargs(self.dpe, "dpe", **kwargs)
        kwargs = enrich_kwargs(self.dg,  "dg",  **kwargs)
        kwargs = enrich_kwargs(self.dv,  "dv",  **kwargs)
        kwargs = enrich_kwargs(self.de,  "de",  **kwargs)
        kwargs = enrich_kwargs(self.extra_style, "extra_style", **kwargs)
        return to_dot(self.g, **kwargs)

    def to_json(self, vs = None, es = None) -> str:
        if vs is None: vs = vertices(self.g)
        if es is None: es = edges(self.g)

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
                        "source" : source(e, self.g),
                        "target" : target(e, self.g),
                        "attributes" : ",\n            ".join([
                            "\"%s\" : \"%s\"" % (k, pmap[e])
                            for k, pmap in self.dpe.items()
                        ]),
                        "sep" : "," if self.dpv else "",
                    } for e in es
                ]
            )
        }
