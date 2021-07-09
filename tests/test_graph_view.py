#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2021, Nokia"
__license__    = "BSD-3"

from pybgl.graph_view   import *
from pybgl.html         import html
from pybgl.ipynb        import ipynb_display_graph

def make_graph() -> DirectedGraph:
    g = DirectedGraph(10)
    for u in vertices(g):
        if u < num_vertices(g) - 1:
            add_edge(u, u + 1, g)
    return g

def test_graph_view_default():
    print("test_graph_view_default")
    g = make_graph()
    gv = GraphView(g)
    e = next(iter(edges(gv)))
    print(e)
    assert source(e, gv) == 0
    assert target(e, gv) == 1
    html("gv")
    ipynb_display_graph(gv)
    assert {u for u in vertices(g)} == {u for u in vertices(gv)}
    assert {e for e in edges(g)} == {e for e in edges(gv)}
    assert {e for e in out_edges(0, g)} == {e for e in out_edges(0, gv)}
    assert out_degree(0, g) == out_degree(0, gv)

    gv1 = GraphView(g, pmap_vrelevant = make_func_property_map(lambda u: bool(u % 3 != 0)))
    html("gv1")
    ipynb_display_graph(gv1)
    assert num_vertices(gv1) == 6
    assert num_edges(gv1) == 3

    gv2 = GraphView(g, pmap_erelevant = make_func_property_map(lambda e: bool(source(e, gv) % 2)))
    html("gv2")
    ipynb_display_graph(gv2)
    assert {u for u in vertices(g)} == {u for u in vertices(gv2)}
    assert {e for e in edges(g)} != {e for e in edges(gv2)}
    assert num_vertices(gv2) == num_vertices(g)
    assert num_edges(gv2) == 4

def test_graph_view_or():
    print("test_graph_view_or")
    g = make_graph()
    gv1 = GraphView(g, pmap_vrelevant = make_func_property_map(lambda u: u < 5))
    gv2 = GraphView(g, pmap_vrelevant = make_func_property_map(lambda u: u > 5))
    gv = gv1 | gv2
    html("gv1")
    ipynb_display_graph(gv1)
    html("gv2")
    ipynb_display_graph(gv2)
    html("gv1 | gv2")
    ipynb_display_graph(gv)
    assert num_vertices(gv) == 9
    assert num_edges(gv) == 7

def test_graph_view_and():
    g = make_graph()
    gv1 = GraphView(g, pmap_vrelevant = make_func_property_map(lambda u: u > 2))
    gv2 = GraphView(g, pmap_vrelevant = make_func_property_map(lambda u: u < 6))
    gv = gv1 & gv2
    html("gv1")
    ipynb_display_graph(gv1)
    html("gv2")
    ipynb_display_graph(gv2)
    html("gv1 & gv2")
    ipynb_display_graph(gv)
    assert {u for u in vertices(g)} != {u for u in vertices(gv)}
    assert {e for e in edges(g)} != {e for e in edges(gv)}
    assert {e for e in out_edges(2, g)} != {e for e in out_edges(2, gv)}
    assert {e for e in out_edges(3, g)} == {e for e in out_edges(3, gv)}
    assert {e for e in out_edges(4, g)} == {e for e in out_edges(4, gv)}
    assert {e for e in out_edges(5, g)} != {e for e in out_edges(5, gv)}
    assert num_vertices(gv) == 3
    assert num_edges(gv) == 2

def test_graph_view_sub():
    g = make_graph()
    gv1 = GraphView(g, pmap_vrelevant = make_func_property_map(lambda u: u > 2))
    gv2 = GraphView(g, pmap_vrelevant = make_func_property_map(lambda u: u > 6))
    gv = gv1 - gv2
    html("gv1")
    ipynb_display_graph(gv1)
    html("gv2")
    ipynb_display_graph(gv2)
    html("gv1 - gv2")
    ipynb_display_graph(gv)
    assert {u for u in vertices(g)} != {u for u in vertices(gv)}
    assert {e for e in edges(g)} != {e for e in edges(gv)}
    assert num_vertices(gv) == 4
    assert num_edges(gv) == 3
