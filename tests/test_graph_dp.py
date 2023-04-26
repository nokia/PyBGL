#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

import json
from pybgl.graph import DirectedGraph
from pybgl.graph_dp import GraphDp
from pybgl.graphviz import read_graphviz
from pybgl.property_map import make_func_property_map
from pybgl.ipynb import ipynb_display_graph

def make_g() -> DirectedGraph:
    g = DirectedGraph(3)
    (e01, _) = g.add_edge(0, 1)
    (e12, _) = g.add_edge(1, 2)
    (e02, _) = g.add_edge(0, 2)
    return g

def make_gdp1() -> GraphDp:
    g = make_g()
    gdp = GraphDp(g)
    return gdp

def make_gdp2() -> GraphDp:
    g = make_g()
    gdp = GraphDp(
        g,
        dpv={
            "label": make_func_property_map(lambda q: "v{q}"),
            "color": make_func_property_map(lambda q: "red" if q % 2 else "green"),
        },
        dpe={
            "label": make_func_property_map(lambda e: f"e{g.source(e)}{g.target(e)}"),
            "color": make_func_property_map(lambda e: "red" if g.target(e) % 2 else "green"),
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
        return vertex_filter(g.source(e)) and vertex_filter(g.target(e))

    g = make_g()
    gdp = GraphDp(
        g,
        dv={"color": "red"},
        de={"color": "purple"},
        dpv={
            "fontcolor": make_func_property_map(
                lambda e: "blue" if e % 2 else "green"
            )
        }
    )
    ipynb_display_graph(
        gdp,
        vs=(u for u in g.vertices() if vertex_filter(u)),
        es=(e for e in g.edges() if edge_filter(e, g, vertex_filter))
    )
    gdp = GraphDp(
        g,
        dv={"color": "red"},
        de={"color": "purple"},
        dpv={
            "fontcolor": make_func_property_map(
                lambda e: "blue" if e % 2 else "green"
            )
        }
    )
