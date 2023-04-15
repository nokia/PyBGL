#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob, Achille Salaün"
__maintainer__ = "Marc-Olivier Buob, Achille Salaün"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2021, Nokia"
__license__    = "BSD-3"

from pybgl.graph        import *
from pybgl.graph        import __len_gen__
from pybgl.graphviz     import to_dot
from pybgl.property_map import ReadPropertyMap, make_func_property_map

class GraphView:
    def __init__(
        self,
        g :DirectedGraph,
        pmap_vrelevant :ReadPropertyMap = None,
        pmap_erelevant :ReadPropertyMap = None
    ):
        self.g = g
        self.pmap_vrelevant = (
            pmap_vrelevant if pmap_vrelevant else
            make_func_property_map(lambda u: True)
        )
        self.pmap_erelevant = (
            pmap_erelevant if pmap_erelevant else
            make_func_property_map(lambda e: True)
        )
    def __getattr__(self, method_name, *args, **kwargs):
        return getattr(self.g, method_name, *args, **kwargs)
    def __or__(self, gv):
        return GraphView(
            self.g,
            make_func_property_map(lambda v: self.pmap_vrelevant[v] or gv.pmap_vrelevant[v]),
            make_func_property_map(lambda e: self.pmap_erelevant[e] or gv.pmap_erelevant[e])
        )
    def __and__(self, gv):
        return GraphView(
            self.g,
            make_func_property_map(lambda v: self.pmap_vrelevant[v] and gv.pmap_vrelevant[v]),
            make_func_property_map(lambda e: self.pmap_erelevant[e] and gv.pmap_erelevant[e])
        )
    def __sub__(self, gv):
        return GraphView(
            self.g,
            make_func_property_map(lambda v: self.pmap_vrelevant[v] and not gv.pmap_vrelevant[v]),
            make_func_property_map(
                lambda e: (
                    self.pmap_erelevant[e] and
                    not gv.pmap_erelevant[e] or (
                        not gv.pmap_vrelevant[self.source(e)] and
                        not gv.pmap_vrelevant[self.target(e)]
                    )
                )
            )
        )
    def vertices(self) -> iter:
        return (
            u for u in self.g.vertices()
            if self.pmap_vrelevant[u]
        )
    def edges(self) -> iter:
        return (
            e for e in self.g.edges()
            if self.pmap_erelevant[e]
            and self.pmap_vrelevant[self.source(e)]
            and self.pmap_vrelevant[self.target(e)]
        )
    def out_edges(self, u :int) -> iter:
        return (
            e for e in self.g.out_edges(u)
            if self.pmap_erelevant[e]
            and self.pmap_vrelevant[self.source(e)]
            and self.pmap_vrelevant[self.target(e)]
        )
    def num_vertices(self) -> int:
        return __len_gen__(self.vertices())
    def num_edges(self) -> int:
        return __len_gen__(self.edges())
    def to_dot(self, *cls, **kwargs) -> str:
        return self.g.to_dot(
            vs = [u for u in self.vertices()],
            es = [e for e in self.edges()],
            source = lambda e, g: self.source(e),
            target = lambda e, g: self.target(e),
            *cls, **kwargs
        )
