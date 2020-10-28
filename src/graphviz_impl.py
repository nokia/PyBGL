#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

# This file must have NO dependency on .graph to avoid mutual inclusion
import re
from .singleton     import Singleton
from .tokenize      import TokenizeVisitor, tokenize

#------------------------------------------------------------------
# Graphviz style
# Useful if you want graph adapted e.g. for dark themes.
#
# from pybgl.graph import GraphvizStyle
# from pybgl.ipynb import ipynb_display_graph
#
# GraphvizStyle.set_fg_color("grey")
# GraphvizStyle.set_bg_color("transparent")
# display_graph = ipynb_display_graph
#
#------------------------------------------------------------------

class GraphvizStyle(metaclass=Singleton):
    graph = {
        "fontcolor" : "black",
        "bgcolor"   : "transparent",
        "rankdir"   : "LR",
    }
    node = {
        "color"     : "black",
        "fontcolor" : "black",
        "shape"     : "circle",
    }
    edge = {
        "color"     : "black",
        "fontcolor" : "black",
    }
    extra_style = list() # splines, etc

    @staticmethod
    def set_fg_color(color):
        GraphvizStyle.graph["fontcolor"] = color
        GraphvizStyle.node["color"]      = color
        GraphvizStyle.node["fontcolor"]  = color
        GraphvizStyle.edge["color"]      = color
        GraphvizStyle.edge["fontcolor"]  = color

    @staticmethod
    def set_bg_color(color):
        GraphvizStyle.graph["bgcolor"] = color

    @staticmethod
    def attributes_to_dot(prefix :str, d :dict) -> str:
        return "%s [%s]" % (
            prefix,
            "; ".join([
                "%s=\"%s\"" % (k, v) for k, v in d.items()
            ])
        ) if d else ""

    def __str__(self) -> str:
        return "; ".join(
            [
                GraphvizStyle.attributes_to_dot("graph", GraphvizStyle.graph),
                GraphvizStyle.attributes_to_dot("node",  GraphvizStyle.node),
                GraphvizStyle.attributes_to_dot("edge",  GraphvizStyle.edge)
            ] + GraphvizStyle.extra_style
        )

#------------------------------------------------------------------
# Graphviz write utilities
# See also Graph.to_dot() and GraphDp.to_dot()
#------------------------------------------------------------------

GRAPHVIZ_SUPPORTED_HTML_TAGS = {
    "b", "/b", "br", "br/", "font", "/font", "hr", "/hr", "i", "/i",
    "img", "/img", "o", "/o", "s", "/s", "sub", "/sub", "sup", "/sup",
    "table", "/table", "td", "/td", "tr", "/tr", "u", "/u", "vr", "/vr",
}

GRAPHVIZ_HTML_TOKENIZER = re.compile(
    "|".join(
        f"<\\s*{tag}\\s*>"
        for tag in GRAPHVIZ_SUPPORTED_HTML_TAGS
    )
)

# The following characters makes crash graphviz when involved in a <label>,
# so we replace them by their corresponding HTML representation.
GRAPHIVZ_MAP_CHAR_ESCAPED = {
    "<"  : "&#60;",
    ">"  : "&#62;",
    "\n" : "\\n",
    "\t" : "\\t",
    "["  : "&#91;",
    "]"  : "&#93;",
    "{"  : "&#123;",
    "}"  : "&#125;",
}

class EscapeHtmlTokenizeVisitor(TokenizeVisitor):
    def __init__(self):
        self.out = ""
    def on_unmatched(self, unmatched :str, start :int, end :int, s :str):
        for a in unmatched:
            escaped = GRAPHIVZ_MAP_CHAR_ESCAPED.get(a, a)
            self.out += escaped
    def on_matched(self, matched :str, start :int, end :int, s :str):
        self.out += matched

def graphviz_escape_html(s :str) -> str:
    vis = EscapeHtmlTokenizeVisitor()
    tokenize(GRAPHVIZ_HTML_TOKENIZER, s, vis)
    return vis.out

#------------------------------------------------------------------
# Graphviz export
# See also Graph.to_dot() and GraphDp.to_dot()
#------------------------------------------------------------------

# TODO factorize with attributes_to_dot
def graphviz_properties_to_str(x, dpx :dict) -> str:
    return "[%s]" % "; ".join([
        "%s=\"%s\"" % (k, pmap[x]) if k != "label" else
        "%s=<%s>"   % (k, graphviz_escape_html(str(pmap[x])))
        for (k, pmap) in dpx.items()
    ]) if dpx else ""

def default_graphviz_style() -> str:
    return str(GraphvizStyle())

def vertex_to_graphviz(u :int, g, dpv :dict = None) -> str:
    return " ".join([str(u), graphviz_properties_to_str(u, dpv)])

def graphviz_arc(g, is_directed :bool = None) -> str:
    if is_directed is None:
        is_directed = lambda g: g.is_directed()
    return "->" if is_directed else "--"

def graphviz_type(g, is_directed :bool = None) -> str:
    if is_directed is None:
        is_directed = lambda g: g.is_directed()
    return "digraph" if is_directed else "graph"

def graphviz_dx_to_dot(prefix :str, dx :dict) -> str:
    assert prefix in {"graph", "node", "edge"}
    return "%s [%s]" % (
        prefix,
        "; ".join([
            "%s=\"%s\"" % (k, v)
            for (k, v) in dx.items()
        ])
    ) if dx else ""

def edge_to_graphviz(e, g, dpe :dict = None, source :callable = None, target :callable = None, is_directed :bool = None) -> str:
    if source is None:
        source = lambda e, g: g.source(e)
    if target is None:
        target = lambda e, g: g.target(e)
    if is_directed is None:
        is_directed = lambda g: g.is_directed()
    return " ".join([
        str(source(e, g)),
        graphviz_arc(g, is_directed),
        str(target(e, g)),
        graphviz_properties_to_str(e, dpe)
    ])

def to_dot(
    g,
    vs              :iter = None,
    es              :iter = None,
    dg              :dict = None,
    dv              :dict = None,
    de              :dict = None,
    dpv             :dict = None,
    dpe             :dict = None,
    graphviz_style  :str = None,
    source          :callable = None,
    target          :callable = None,
    is_directed     :bool = None
) -> str:
    if vs             is None: vs     = (u for u in g.vertices())
    if es             is None: es     = (e for e in g.edges())
    if source         is None: source = lambda e, g: g.source(e)
    if target         is None: target = lambda e, g: g.target(e)
    if is_directed    is None: is_directed = g.directed
    if graphviz_style is None: graphviz_style = default_graphviz_style()

    dg = graphviz_dx_to_dot("graph", dg)
    dv = graphviz_dx_to_dot("node",  dv)
    de = graphviz_dx_to_dot("edge",  de)
    instructions = (
          ([graphviz_style] if graphviz_style else [])
        + ([dg] if dg else [])
        + ([dv] if dv else [])
        + ([de] if de else [])
        + [vertex_to_graphviz(u, g, dpv) for u in vs]
        + [edge_to_graphviz(e, g, dpe, source, target, is_directed) for e in es]
    )

    return "%(type)s G {%(instructions)s}" % {
        "type" : "digraph" if is_directed else "graph",
        "instructions" : "\n  %s;\n" % ";\n  ".join(instructions) if instructions else ""
    }
