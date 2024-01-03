#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import (
    DirectedGraph,
    GraphView,
    html as _html,
    in_ipynb, ipynb_display_graph,
    make_func_property_map,
)


def display_graph(g, *args, **kwargs):
    if in_ipynb():
        ipynb_display_graph(g, *args, **kwargs)
    else:
        _ = g.to_dot()


def html(s):
    if in_ipynb():
        _html(s)


def make_graph() -> DirectedGraph:
    g = DirectedGraph(10)
    for u in g.vertices():
        if u < g.num_vertices() - 1:
            g.add_edge(u, u + 1)
    return g


def test_graph_view_default():
    g = make_graph()
    gv = GraphView(g)
    e = next(iter(gv.edges()))
    assert gv.source(e) == 0
    assert gv.target(e) == 1
    display_graph(gv)
    assert set(g.vertices()) == set(gv.vertices())
    assert set(g.edges()) == set(gv.edges())
    assert set(g.out_edges(0)) == set(gv.out_edges(0))
    assert g.out_degree(0) == gv.out_degree(0)

    gv1 = GraphView(
        g,
        pmap_vrelevant=make_func_property_map(
            lambda u: bool(u % 3 != 0)
        )
    )
    display_graph(gv1)
    assert gv1.num_vertices() == 6
    assert gv1.num_edges() == 3

    gv2 = GraphView(
        g,
        pmap_erelevant=make_func_property_map(
            lambda e: bool(gv.source(e) % 2)
        )
    )
    html("gv2")
    display_graph(gv2)
    assert set(g.vertices()) == set(gv2.vertices())
    assert set(g.edges()) != set(gv2.edges())
    assert gv2.num_vertices() == g.num_vertices()
    assert gv2.num_edges() == 4


def test_graph_view_or():
    g = make_graph()
    gv1 = GraphView(g, pmap_vrelevant=make_func_property_map(lambda u: u < 5))
    gv2 = GraphView(g, pmap_vrelevant=make_func_property_map(lambda u: u > 5))
    gv = gv1 | gv2
    html("gv1")
    display_graph(gv1)
    html("gv2")
    display_graph(gv2)
    html("gv1 | gv2")
    display_graph(gv)
    assert gv.num_vertices() == 9
    assert gv.num_edges() == 7


def test_graph_view_and():
    g = make_graph()
    gv1 = GraphView(g, pmap_vrelevant=make_func_property_map(lambda u: u > 2))
    gv2 = GraphView(g, pmap_vrelevant=make_func_property_map(lambda u: u < 6))
    gv = gv1 & gv2
    html("gv1")
    display_graph(gv1)
    html("gv2")
    display_graph(gv2)
    html("gv1 & gv2")
    display_graph(gv)
    assert set(g.vertices()) != set(gv.vertices())
    assert set(g.edges()) != set(gv.edges())
    assert set(g.out_edges(2)) != set(gv.out_edges(2))
    assert set(g.out_edges(3)) == set(gv.out_edges(3))
    assert set(g.out_edges(4)) == set(gv.out_edges(4))
    assert set(g.out_edges(5)) != set(gv.out_edges(5))
    assert gv.num_vertices() == 3
    assert gv.num_edges() == 2


def test_graph_view_sub():
    g = make_graph()
    gv1 = GraphView(g, pmap_vrelevant=make_func_property_map(lambda u: u > 2))
    gv2 = GraphView(g, pmap_vrelevant=make_func_property_map(lambda u: u > 6))
    gv = gv1 - gv2
    html("gv1")
    display_graph(gv1)
    html("gv2")
    display_graph(gv2)
    html("gv1 - gv2")
    display_graph(gv)
    assert set(g.vertices()) != set(gv.vertices())
    assert set(g.edges()) != set(gv.edges())
    assert gv.num_vertices() == 4
    assert gv.num_edges() == 3
