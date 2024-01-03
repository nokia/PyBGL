#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl import (
    Automaton,
    DirectedGraph,
    GraphDp,
    GraphvizStyle,
    ReadWritePropertyMap,
    ReadGraphvizVisitor,
    UndirectedGraph,
    graph_to_html,
    make_assoc_property_map,
    make_func_property_map,
    html,
    in_ipynb,
    ipynb_display_graph,
    read_graphviz
)
from pybgl.graphviz import (
    graphviz_escape_char,
    graphviz_escape_html,
)


WEIRD_CHARS = "&<>\n\t\r[]{}" + "".join([chr(i) for i in range(32)])


def display_graph(g, *args, **kwargs):
    if in_ipynb():
        ipynb_display_graph(g, *args, **kwargs)
    else:
        _ = g.to_dot()


def test_graphviz_escape_char():
    # All these characters must be escaped otherwise graphviz crashes.
    invalid_escape = set()
    chars = WEIRD_CHARS
    for a in chars:
        escaped = graphviz_escape_char(a)
        # print(ord(a), escaped)
        if a == escaped:
            invalid_escape.add(a)
    assert not invalid_escape


def test_graph_to_html_with_weird_chars():
    g = Automaton(2)
    g.add_edge(0, 1, WEIRD_CHARS)
    graph_to_html(g)
    if in_ipynb():
        ipynb_display_graph(g)


def test_graphviz_escape_html():
    assert graphviz_escape_html(
        "<table><tr><td>foo</td></tr></table>"
    ) == "<table><tr><td>foo</td></tr></table>"
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
    (e, _) = g.add_edge(0, 1)
    _ = graph_to_html(g)
    if in_ipynb():
        display_graph(g)


def make_graph(G):
    g = G(10)
    for u in g.vertices():
        for v in g.vertices():
            if u < v < u + 3:
                g.add_edge(u, v)
    return g


def test_graph_to_html_with_pmaps():
    # Configure theme
    GraphvizStyle.set_fg_color("grey")
    GraphvizStyle.set_bg_color("transparent")

    def vertex_filter(u):
        return u < 5

    def edge_filter(e, g, vertex_filter):
        return vertex_filter(g.source(e)) and vertex_filter(g.target(e))

    for G in [DirectedGraph, UndirectedGraph]:
        if in_ipynb():
            html(str(G))
        g = make_graph(G)

        # Graph configuration display
        dv = {"color": "purple"}
        de = {"color": "red"}
        dpv = {
            "fontcolor": make_func_property_map(
                lambda e: "cyan" if e % 2 else "orange"
            )
        }
        dpe = {
            "fontcolor": make_func_property_map(
                lambda e: "blue" if g.source(e) % 2 else "red"
            ),
            "label": make_func_property_map(
                lambda e: f"({g.source(e)}, {g.target(e)})"
            )
        }

        # Choose view
        # Omit vs (resp. es) to iterate over all vertices (resp. edges)
        vs = [u for u in g.vertices() if vertex_filter(u)]
        es = [e for e in g.edges() if edge_filter(e, g, vertex_filter)]

        # Method1: call helper (ipynb_display_graph, graph_to_html)
        shtml = graph_to_html(g, dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es)
        assert isinstance(shtml, str)
        display_graph(g, dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es)

        # Method2: use GraphDp. This offers the opportunity to export the
        # displayed graph to other export formats.
        gdp = GraphDp(g, dpv=dpv, dpe=dpe, dv=dv, de=de)

        # These two commands have the same outcome
        shtml = graph_to_html(gdp, vs=vs, es=es)
        assert isinstance(shtml, str)
        shtml = graph_to_html(
            gdp,
            dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es
        )
        assert isinstance(shtml, str)

        # These two commands have the same outcome
        display_graph(gdp, vs=vs, es=es)
        display_graph(gdp, dpv=dpv, dpe=dpe, dv=dv, de=de, vs=vs, es=es)


def test_graph_to_html_with_html_sequences(debug: bool = False):

    if not debug:
        def print(*args, **kwargs):
            pass

    g = DirectedGraph(2)
    (e, _) = g.add_edge(0, 1)
    pmap_vlabel = make_assoc_property_map(defaultdict(str))
    pmap_elabel = make_assoc_property_map(defaultdict(str))
    gdp = GraphDp(
        g,
        dpv={"label": pmap_vlabel},
        dpe={"label": pmap_elabel}
    )

    for label in [
        "<b>foo</b>", "<foo>", "<", ">",
        "<b>foo</b><bar>",
        "<bar><b>foo</b>",
        "<font color='red'><b>foo</b></font>",
        # NB: foo.png must exists + graphviz imposes <img/> not <img>
        # "<table><tr><td><img src='foo.png'/></td></tr></table>",
    ]:
        print(f"{label} --> {graphviz_escape_html(label)}")
        pmap_vlabel[0] = pmap_vlabel[1] = pmap_elabel[e] = label
        shtml = graph_to_html(gdp)
        if in_ipynb():
            html(shtml)
        display_graph(gdp)


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
    display_graph(g)
    assert g.num_vertices() == 3
    assert g.num_edges() == 1


def test_read_graphviz_custom():

    class MyReadGraphvizVisitor(ReadGraphvizVisitor):
        def __init__(
            self,
            pmap_vlabel: ReadWritePropertyMap,
            pmap_elabel: ReadWritePropertyMap
        ):
            super().__init__()
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
        make_assoc_property_map(map_vlabel),
        make_assoc_property_map(map_elabel)
    )
    read_graphviz(dot.splitlines(), g, vis)
    display_graph(g)
    assert map_vlabel == {0: "red", 1: "green", 2: "blue"}, map_vlabel
    e_01 = next(iter(g.edges()))
    assert map_elabel == {e_01: "my_label"}, map_vlabel
