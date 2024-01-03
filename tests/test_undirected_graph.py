#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from pybgl import UndirectedGraph


(u, v, w) = (0, 1, 2)


def make_g1() -> UndirectedGraph:
    g1 = UndirectedGraph()
    g1.add_vertex()
    g1.add_vertex()
    g1.add_vertex()
    return g1


def make_g2() -> UndirectedGraph:
    g2 = make_g1()
    g2.add_edge(u, v)
    g2.add_edge(u, v)  # parallel edge
    g2.add_edge(u, w)
    g2.add_edge(v, w)
    g2.add_edge(w, w)
    return g2


def test_undirected_graph_num_vertices():
    g1 = make_g1()
    assert g1.num_vertices() == 3


def test_undirected_graph_node_add_edge():
    # Make graph
    g = make_g1()
    assert g.out_degree(u) == 0
    assert g.num_edges() == 0

    # Add e1
    (e1, added1) = g.add_edge(u, v)
    assert added1
    (e, found) = g.edge(u, v)
    assert found
    assert e == e1
    assert g.out_degree(u) == 1
    assert g.num_edges() == 1

    # No arc
    (e, found) = g.edge(u, w)
    assert not found
    assert {e for e in g.out_edges(u)} == {e1}

    # Add e2
    (e2, added2) = g.add_edge(u, w)
    assert added2
    assert {e for e in g.out_edges(u)} == {e1, e2}
    assert g.out_degree(u) == 2
    assert g.num_edges() == 2


def test_undirected_graph_add_vertex():
    g = make_g2()
    assert g.num_vertices() == 3
    assert g.num_edges() == 5

    # Add vertex x
    x = g.add_vertex()
    assert g.num_vertices() == 4

    # Add edge (v -> x)
    g.add_edge(v, x)
    assert g.num_edges() == 6
    assert g.out_degree(v) == 4


def test_undirected_graph_remove_edge():
    g = make_g2()
    assert g.num_edges() == 5

    (e, found) = g.edge(v, w)
    assert found
    g.remove_edge(e)
    assert g.num_edges() == 4

    (e, found) = g.edge(w, w)
    # print(g.adjacencies)
    assert found
    g.remove_edge(e)
    assert g.num_edges() == 3


def test_undirected_graph_remove_vertex():
    g = make_g2()
    assert g.num_vertices() == 3
    assert g.num_edges() == 5

    g.remove_vertex(v)
    assert g.num_vertices() == 2
    assert g.num_edges() == 2

    g.remove_vertex(w)
    assert g.num_vertices() == 1
    assert g.num_edges() == 0

    g.remove_vertex(u)
    assert g.num_vertices() == 0
    assert g.num_edges() == 0


def test_undirected_graph(debug: bool = False):
    if not debug:
        def print(*args, **kwargs):
            pass
    g = UndirectedGraph()

    assert g.num_vertices() == 0
    u = g.add_vertex()
    assert g.num_vertices() == 1
    v = g.add_vertex()
    assert g.num_vertices() == 2
    w = g.add_vertex()
    assert g.num_vertices() == 3

    assert g.num_edges() == 0
    e_uv,  _ = g.add_edge(u, v)
    assert g.num_edges() == 1
    e_uv1, _ = g.add_edge(v, u)
    assert g.num_edges() == 2
    e_uw,  _ = g.add_edge(u, w)
    assert g.num_edges() == 3
    e_vw,  _ = g.add_edge(v, w)
    assert g.num_edges() == 4

    print(f"Edges = {set(e for e in g.edges())}")

    print(f"In-edges({u}) = {{e for e in g.in_edges(u)}}")
    assert g.in_degree(u) == 3
    assert g.in_degree(v) == 3
    assert g.in_degree(w) == 2, (
        f"g.in_edges({w}) = {{u for u in g.in_edges(w)}}"
    )

    print(f"Out-edges({u}) = {{e for e in g.out_edges(u)}}")
    assert g.out_degree(u) == 3
    assert g.out_degree(v) == 3
    assert g.out_degree(w) == 2

    print(f"Removing {e_uv}")
    g.remove_edge(e_uv)
    assert g.num_edges() == 3

    print(f"Removing {e_uv1}")
    g.remove_edge(e_uv1)
    assert g.num_edges() == 2

    print(f"Removing {v}")
    g.remove_vertex(v)
    assert g.num_vertices() == 2

    print(f"Edges = {set(e for e in g.edges())}")
    assert g.num_edges() == 1

    print(f"Out-edges({u}) = {{e for e in g.out_edges(u)}}")
    assert g.out_degree(u) == 1
    assert g.out_degree(w) == 1
    assert g.in_degree(u) == 1
    assert g.in_degree(w) == 1
