#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.graph        import *
from pybgl.graph_dp     import GraphDp
from pybgl.graphviz     import graphviz_escape_char, graphviz_escape_html, graph_to_html, read_graphviz
from pybgl.html         import html
from pybgl.ipynb        import in_ipynb, ipynb_display_graph

WEIRD_CHARS = "&<>\n\t\r[]{}" + "".join([chr(i) for i in range(32)])

def test_graphviz_escape_char():
    # All these characters must be escaped otherwise graphviz crashes.
    invalid_escape = set()
    chars = WEIRD_CHARS
    for a in chars:
        escaped = graphviz_escape_char(a)
        print(ord(a), escaped)
        if a == escaped:
            invalid_escape.add(a)
    assert not invalid_escape

def test_graph_to_html_with_weird_chars():
    from pybgl.automaton import Automaton, add_edge
    g = Automaton(2)
    add_edge(0, 1, WEIRD_CHARS, g)
    graph_to_html(g)
    if in_ipynb():
        ipynb_display_graph(g)

def test_graphviz_escape_html():
    assert graphviz_escape_html("<table><tr><td>foo</td></tr></table>") == "<table><tr><td>foo</td></tr></table>"
    assert graphviz_escape_html("<b>foo</b>") == "<b>foo</b>"
    assert graphviz_escape_html("<") == "&#60;"
    assert graphviz_escape_html(">") == "&#62;"
    assert graphviz_escape_html("\n") == "\\n"
    assert graphviz_escape_html("\t") == "\\t"
    assert graphviz_escape_html("[") == "&#91;"
    assert graphviz_escape_html("]") == "&#93;"
    assert graphviz_escape_html("{") == "&#123;"
    assert graphviz_escape_html("}") == "&#125;"
    assert graphviz_escape_html("<foo>") == "&#60;foo&#62;"
    assert graphviz_escape_html("<b>foo</b><bar>") == "<b>foo</b>&#60;bar&#62;"

def test_graph_to_html():
    g = DirectedGraph(2)
    (e, _) = add_edge(0, 1, g)
    shtml = graph_to_html(g)
    if in_ipynb():
        ipynb_display_graph(g)

def make_graph(G):
    g = G(10)
    for u in vertices(g):
        for v in vertices(g):
            if u < v < u + 3:
                add_edge(u, v, g)
    return g

def test_graph_to_html_with_pmaps():
    # Configure theme

    GraphvizStyle.set_fg_color("grey")
    GraphvizStyle.set_bg_color("transparent")
    display_graph = ipynb_display_graph

    from pybgl.graph_dp     import GraphDp
    from pybgl.property_map import make_func_property_map

    def vertex_filter(u):
        return u < 5

    def edge_filter(e, g, vertex_filter):
        return vertex_filter(source(e, g)) and vertex_filter(target(e, g))

    for G in [DirectedGraph, UndirectedGraph]:
        html(str(G))
        g = make_graph(G)

        # Graph configuration display
        dv = {"color" : "purple"}
        de = {"color" : "red"}
        dpv = {
            "fontcolor" : make_func_property_map(
                lambda e: "cyan" if e % 2 else "orange"
            )
        }
        dpe = {
            "fontcolor" : make_func_property_map(
                lambda e: "blue" if source(e, g) % 2 else "red"
            ),
            "label" : make_func_property_map(
                lambda e: f"({source(e, g)}, {target(e, g)})"
            )
        }

        # Choose view
        # Omit vs (resp. es) to iterate over all vertices (resp. edges)
        vs = [u for u in vertices(g) if vertex_filter(u)]
        es = [e for e in edges(g)    if edge_filter(e, g, vertex_filter)]

        # Method1: call helper (ipynb_display_graph, graph_to_html)
        shtml = graph_to_html(g, dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es)
        if in_ipynb():
            ipynb_display_graph(g, dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es)

        # Method2: use GraphDp. This offers the opportunity to export the
        # displayed graph to other export formats.
        gdp = GraphDp(g, dpv=dpv, dpe=dpe, dv=dv, de=de)

        # These two commands have the same outcome
        shtml = graph_to_html(gdp, vs=vs, es=es)
        shtml = graph_to_html(gdp, dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es)

        if in_ipynb():
            # These two commands have the same outcome
            ipynb_display_graph(gdp, vs=vs, es=es)
            ipynb_display_graph(gdp, dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es)

def test_graph_to_html_with_html_sequences():
    from collections        import defaultdict
    from pybgl.property_map import make_assoc_property_map

    g = DirectedGraph(2)
    (e, _) = add_edge(0, 1, g)
    pmap_vlabel = make_assoc_property_map(defaultdict(str))
    pmap_elabel = make_assoc_property_map(defaultdict(str))
    gdp = GraphDp(
        g,
        dpv = {"label" : pmap_vlabel},
        dpe = {"label" : pmap_elabel}
    )

    for label in [
        "<b>foo</b>", "<foo>", "<", ">",
        "<b>foo</b><bar>",
        "<bar><b>foo</b>",
        "<font color='red'><b>foo</b></font>",
        # NB: foo.png must exists + graphviz imposes <img/> not <img>
        #"<table><tr><td><img src='foo.png'/></td></tr></table>",
    ]:
        print(f"{label} --> {graphviz_escape_html(label)}")
        pmap_vlabel[0] = pmap_vlabel[1] = pmap_elabel[e] = label
        shtml = graph_to_html(gdp)
        if in_ipynb():
            html(shtml)
            ipynb_display_graph(gdp)

# Graphviz file parsing
def test_read_graphviz_simple():
    g = DirectedGraph()
    dot = """digraph G {
        0;
        1;
        2;
        0->1;
    }"""
    read_graphviz(dot.splitlines(), g)
    if in_ipynb():
        ipynb_display_graph(g)
    assert num_vertices(g) == 3
    assert num_edges(g) == 1

def test_read_graphviz_custom():
    from collections        import defaultdict
    from pybgl.property_map import ReadWritePropertyMap, make_assoc_property_map
    from pybgl.graphviz     import ReadGraphvizVisitor

    class MyReadGraphvizVisitor(ReadGraphvizVisitor):
        def __init__(self, g :Graph, pmap_vlabel :ReadWritePropertyMap, pmap_elabel :ReadWritePropertyMap):
            super().__init__(g)
            self.pmap_vlabel = pmap_vlabel
            self.pmap_elabel = pmap_elabel

        def on_install_vertex_property(self, u, g, key, value):
            if key == "label":
                self.pmap_vlabel[u] = value

        def on_install_edge_property(self, e, g, key, value):
            if key == "label":
                self.pmap_elabel[e] = value

    map_vlabel = defaultdict(str)
    map_elabel = defaultdict(str)
    g = DirectedGraph()
    dot = """digraph G {
        0 [fontsize=8 label='red'];
        1 [label='green'];
        2 [label='blue' fontsize=10];
        0->1 [label='my_label'];
    }"""
    vis = MyReadGraphvizVisitor(
        g,
        make_assoc_property_map(map_vlabel),
        make_assoc_property_map(map_elabel)
    )
    read_graphviz(dot.splitlines(), g, vis)
    if in_ipynb(): ipynb_display_graph(g)
    assert map_vlabel == {0: "red", 1: "green", 2: "blue"}, map_vlabel
    e_01 = next(iter(edges(g)))
    assert map_elabel == {e_01 : "my_label"}, map_vlabel
