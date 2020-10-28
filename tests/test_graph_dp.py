#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import json
from pybgl.graph        import DirectedGraph, add_edge, edges, num_edges, num_vertices, source, target, vertices
from pybgl.graph_dp     import GraphDp
from pybgl.graphviz     import read_graphviz
from pybgl.property_map import make_assoc_property_map, make_func_property_map
from pybgl.ipynb        import ipynb_display_graph

def make_g() -> DirectedGraph:
    g = DirectedGraph(3)
    e01, _ = add_edge(0, 1, g)
    e12, _ = add_edge(1, 2, g)
    e02, _ = add_edge(0, 2, g)
    return g

def make_gdp1() -> GraphDp:
    g = make_g()
    gdp = GraphDp(g)
    return gdp

def make_gdp2() -> GraphDp:
    g = make_g()
    vlabel = {u : "v%s" % u for u in vertices(g)}
    elabel = {e : "e%s%s" % (source(e, g), target(e, g)) for e in edges(g)}
    gdp = GraphDp(
        g,
        dpv = {
            "label" : make_assoc_property_map(vlabel),
            "color" : make_func_property_map(lambda q: "red" if q % 2 else "green"),
        },
        dpe = {
            "label" : make_assoc_property_map(elabel),
            "color" : make_func_property_map(lambda e: "red" if target(e, g) % 2 else "green"),
        }
    )
    return gdp

def make_gdps() -> list:
    gdp1 = make_gdp1()
    gdp2 = make_gdp2()
    return [gdp1, gdp2]

def test_graph_dp_dot():
    g_expected = make_g()
    for gdp in make_gdps():
        g = DirectedGraph()
        # Try to load graphviz
        # TODO: fix read_graphviz
        read_graphviz(gdp.to_dot(), g)
        #assert num_vertices(g) == num_vertices(g_expected)
        #assert num_edges(g) == num_edges(g_expected)

def test_graph_dp_json():
    for gdp in make_gdps():
        s_json = gdp.to_json()
        print(s_json)
        # Try to load json
        json.loads(s_json)

def test_graph_dp_filter():
    def vertex_filter(u):
        return u < 2

    def edge_filter(e, g, vertex_filter):
        return vertex_filter(source(e, g)) and vertex_filter(target(e, g))

    g = make_g()
    gdp = GraphDp(
        g,
        dv = {"color" : "red"},
        de = {"color" : "purple"},
        dpv = {"fontcolor" : make_func_property_map(lambda e: "blue" if e % 2 else "green")}
    )
    ipynb_display_graph(
        gdp,
        vs = (u for u in vertices(g) if vertex_filter(u)),
        es = (e for e in edges(g)    if edge_filter(e, g, vertex_filter))
    )
    gdp = GraphDp(
        g,
        dv = {"color" : "red"},
        de = {"color" : "purple"},
        dpv = {"fontcolor" : make_func_property_map(lambda e: "blue" if e % 2 else "green")}
    )
