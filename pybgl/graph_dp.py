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

from .graph         import default_graphviz_style, DirectedGraph, edges, Graph, source, target, vertices
from .property_map  import get

class GraphDp:
    def __init__(self, g :Graph, dpv = {}, dpe = {}, dg_default = {}, dv_default = {}, de_default = {}, extra_style = list()):
        self.m_g = g
        self.m_dpv = dpv                 # Vertex attributes
        self.m_dpe = dpe                 # Edge attributes
        self.m_dg_default = dg_default   # Graph attributes
        self.m_dv_default = dv_default   # Vertex default attributes
        self.m_de_default = de_default   # Edge default attributes
        self.m_extra_style = extra_style # Extra style (splines etc)

    def get_dpv(self) -> dict: return self.m_dpv
    def get_dpe(self) -> dict: return self.m_dpve
    def get_dg_default(self) -> dict: return self.m_dg_default
    def get_dv_default(self) -> dict: return self.m_dv_default
    def get_de_default(self) -> dict: return self.m_de_default

    @staticmethod
    def default_to_dot(prefix :str, d :dict) -> str:
        return "%s [%s]" % (
            prefix,
            "; ".join([
                "%s=\"%s\"" % (k, v) for k, v in d.items()
            ])
        )

    def to_dot(self, vs = None, es = None) -> str:
        if vs == None: vs = vertices(self.m_g)
        if es == None: es = edges(self.m_g)
        graphviz_style = ("%s;" % "; ".join(self.m_extra_style)) if self.m_extra_style else ""
        graphviz_style += "; ".join([
            GraphDp.default_to_dot("graph", self.m_dg_default),
            GraphDp.default_to_dot("node",  self.m_dv_default),
            GraphDp.default_to_dot("edge",  self.m_de_default),
            ""
        ])

        return "%s G {%s %s}" % (
            self.m_g.s_graphviz_type,
            graphviz_style,
            "; ".join(
                [
                    "%s [%s]" % (
                        u,
                        "; ".join(["%s=\"%s\"" % (k, get(pmap, u)) if k != "label" else "%s=<%s>" % (k, get(pmap, u)) for k, pmap in self.m_dpv.items()])
                    ) for u in vs
                ] + [
                    "%s %s %s [%s]" % (
                        source(e, self.m_g),
                        DirectedGraph.s_graphviz_arc,
                        target(e, self.m_g),
                        "; ".join(["%s=\"%s\"" % (k, get(pmap, e)) if k != "label" else "%s=<%s>" % (k, get(pmap, e)) for k, pmap in self.m_dpe.items()])
                    ) for e in es
                ]
            )
        )
