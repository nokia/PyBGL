#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import sys
from collections import defaultdict

from pybgl.graph import (
    DirectedGraph, EdgeDescriptor, UndirectedGraph,
    add_edge, add_vertex, edges, source, target, vertices
)
from pybgl.ipynb import in_ipynb, ipynb_display_graph
from pybgl.property_map import (
    ReadWritePropertyMap,
    make_assoc_property_map, make_func_property_map
)
from pybgl.dijkstra_shortest_paths import (
    INFINITY, DijkstraVisitor, DijkstraDebugVisitor,
    dijkstra_shortest_path, dijkstra_shortest_paths, make_path
)

# For debug purposes

from pybgl.graphviz import GraphvizStyle
from pybgl.ipynb import in_ipynb, ipynb_display_graph

def display_graph(g, pmap_eweight = None, map_vpreds = None):
    if in_ipynb():
        dpe = dict()
        if pmap_eweight:
            dpe["label"] = pmap_eweight
        if map_vpreds:
            shortest_path_dag = {e for es in map_vpreds.values() for e in es}
            dpe["color"] = make_func_property_map(
                lambda e: "red" if e in shortest_path_dag else None
            )
        ipynb_display_graph(g, dpe = dpe)

LINKS = [
    # (u, v, weight)
    (0, 1, 1),
    (1, 2, 1),
    (1, 3, 3),
    (3, 0, 1),
    (0, 4, 1),
    (0, 5, 1),
    (2, 5, 6),
    (5, 6, 8),
    (6, 7, 1),
    (6, 8, 1),
    (8, 2, 1),
    (8, 3, 3.99),
    (9, 2, 1)
]

def make_graph(
    links :list,
    pmap_eweight :ReadWritePropertyMap,
    directed :bool = True,
    build_reverse_edge = True
):
    def add_node(un, g, d):
        u = d.get(un)
        if u is None:
            u = add_vertex(g)
            d[un] = u
        return u

    g = DirectedGraph() if directed else UndirectedGraph()
    d = dict()
    for (un, vn, w) in links:
        u = add_node(un, g, d)
        v = add_node(vn, g, d)
        (e, added) = add_edge(u, v, g)
        assert added
        pmap_eweight[e] = w

        if build_reverse_edge:
            (e, added) = add_edge(v, u, g)
            assert added
            pmap_eweight[e] = w
    return g

def test_isolated_vertices():
    # Create 10 isolated vertices
    infty = sys.maxsize
    g = DirectedGraph(10)
    map_eweight = dict()

    for s in vertices(g):
        map_vpreds = defaultdict(set)
        map_vdist = dict()
        dijkstra_shortest_paths(
            g, s,
            make_assoc_property_map(map_eweight),
            make_assoc_property_map(map_vpreds),
            make_assoc_property_map(map_vdist)
        )

        # No incident arc in the shortest path DAG
        assert map_vpreds == dict()

        # Every target are at infinite distance excepted the source node.
        assert map_vdist  == {u : infty if u != s else 0 for u in vertices(g)}

def test_simple_graph():
    # Prepare graph, just a 0 -> 1 arc
    g = DirectedGraph()
    u = add_vertex(g)
    v = add_vertex(g)
    e, added = add_edge(u, v, g)
    assert added
    w = 1
    map_eweight = {
        e : w,
    }

    # Call Dijkstra
    map_vpreds = defaultdict(set)
    map_vdist = dict()
    dijkstra_shortest_paths(
        g, u,
        make_assoc_property_map(map_eweight),
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist)
    )

    # Check
    assert map_vpreds == {
        v : {e},
    }

    assert map_vdist == {
        u : 0,
        v : w
    }

def test_parallel_edges():
    # Prepare graph, two parallel edges from 0 to 1
    g = DirectedGraph()
    u = add_vertex(g)
    v = add_vertex(g)
    (e1, added) = add_edge(u, v, g)
    assert added
    (e2, added) = add_edge(u, v, g)
    assert added
    w = 1
    map_eweight = {
        e1 : w,
        e2 : w,
    }

    # Call Dijkstra
    map_vpreds = defaultdict(set)
    map_vdist = dict()
    dijkstra_shortest_paths(
        g, u,
        make_assoc_property_map(map_eweight),
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist)
    )

    # Check
    assert map_vpreds == {
        v : {e1, e2},
    }

    assert map_vdist == {
        u : 0,
        v : w
    }

def test_directed_graph(links :list = LINKS):
    map_eweight = dict()
    pmap_eweight = make_assoc_property_map(map_eweight)
    g = make_graph(links, pmap_eweight, directed = True, build_reverse_edge = False)

    map_vpreds = defaultdict(set)
    map_vdist = dict()
    dijkstra_shortest_paths(
        g, 0,
        pmap_eweight,
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist),
        vis = DijkstraDebugVisitor()
    )

    E = {(source(e, g), target(e, g)) : e for e in edges(g)}

    assert map_vpreds == {
        1 : {E[0, 1]},
        2 : {E[1, 2]},
        3 : {E[1, 3]},
        4 : {E[0, 4]},
        5 : {E[0, 5]},
        6 : {E[5, 6]},
        7 : {E[6, 7]},
        8 : {E[6, 8]},
    }
    assert map_vdist == {
        0 : 0,
        1 : 1,
        2 : 2,
        3 : 4,
        4 : 1,
        5 : 1,
        6 : 9,
        7 : 10,
        8 : 10,
        9 : INFINITY
    }

def test_decrease_key():
    g = DirectedGraph(3)
    (e01, _) = add_edge(0, 1, g)
    (e02, _) = add_edge(0, 2, g)
    (e21, _) = add_edge(2, 1, g)
    map_eweight = {
        e01 : 9,
        e02 : 1,
        e21 : 1,
    }
    pmap_eweight = make_assoc_property_map(map_eweight)

    map_vpreds = defaultdict(set)
    map_vdist = dict()
    dijkstra_shortest_paths(
        g, 0,
        pmap_eweight,
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist)
    )
    display_graph(g, pmap_eweight, map_vpreds)

    assert map_vpreds[1] == {e21}
    assert map_vpreds[2] == {e02}
    assert map_vdist == {
        0  : 0,
        1  : 2,
        2  : 1,
    }

def test_directed_symmetric_graph(links :list = LINKS):
    map_eweight = dict()
    pmap_eweight = make_assoc_property_map(map_eweight)
    g = make_graph(LINKS, pmap_eweight, directed = True, build_reverse_edge = True)

    map_vpreds = defaultdict(set)
    map_vdist = dict()
    dijkstra_shortest_paths(
        g, 0,
        pmap_eweight,
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist)
    )
    display_graph(g, pmap_eweight, map_vpreds)

    E = {(source(e, g), target(e, g)) : e for e in edges(g)}

    assert map_vpreds == {
        1 : {E[0, 1]},
        2 : {E[1, 2]},
        3 : {E[0, 3]},
        4 : {E[0, 4]},
        5 : {E[0, 5]},
        6 : {E[8, 6]},
        7 : {E[6, 7]},
        8 : {E[2, 8]},
        9 : {E[2, 9]}
    }
    assert map_vdist == {
        0 : 0,
        1 : 1,
        2 : 2,
        3 : 1,
        4 : 1,
        5 : 1,
        6 : 4,
        7 : 5,
        8 : 3,
        9 : 3
    }

def test_dijkstra_shortest_path(links :list = LINKS):
    # Prepare graph
    map_eweight = defaultdict(int)
    pmap_eweight = make_assoc_property_map(map_eweight)
    g = make_graph(links, pmap_eweight, build_reverse_edge = False)

    # Dijkstra, stopped when vertex 9 is reached
    map_vpreds = defaultdict(set)
    map_vdist = defaultdict(int)
    s = 0
    t = 8
    path = dijkstra_shortest_path(
        g, s, t,
        pmap_eweight,
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist)
    )
    if in_ipynb():
        ipynb_display_graph(
            g,
            dpe = {
                "color" : make_func_property_map(lambda e: "green" if e in path else "red"),
                "label" : pmap_eweight
            }
        )
    assert [
        (source(e, g), target(e, g))
        for e in path
    ] == [(0, 5), (5, 6), (6, 8)]

def test_dijkstra_shortest_paths_bandwidth():
    # Prepare graph
    map_eweight = defaultdict(int)
    pmap_eweight = make_assoc_property_map(map_eweight)
    links = [
        # (u, v, weight)
        (0, 1, 100),
        (1, 2, 80),
        (1, 2, 70),
        (1, 3, 30),
        (3, 0, 10),
    ]
    g = make_graph(links, pmap_eweight, build_reverse_edge = False)

    map_vpreds = defaultdict(set)
    map_vdist = defaultdict(int)
    s = 0

    dijkstra_shortest_paths(
        g, s,
        make_assoc_property_map(map_eweight),
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist),
        compare = lambda a, b: a >= b,
        combine = min,
        zero    = INFINITY,
        infty   = 0
    )
    display_graph(g, pmap_eweight)
    print(map_vdist)
    assert map_vdist == {
        0 : INFINITY,
        1 : 100,
        2 : 80,
        3 : 30
    }
