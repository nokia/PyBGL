#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl import (
    INFINITY,
    Graph, DirectedGraph, EdgeDescriptor, UndirectedGraph,
    ReadPropertyMap,
    ReadWritePropertyMap,
    DijkstraVisitor,
    dijkstra_shortest_path,
    dijkstra_shortest_paths,
    in_ipynb, ipynb_display_graph,
    make_assoc_property_map,
    make_func_property_map
)


# For debug purposes

def display_graph(
    g: Graph,
    pmap_eweight: ReadPropertyMap = None,
    map_vpreds: dict = None
):
    if in_ipynb():
        dpe = dict()
        if pmap_eweight:
            dpe["label"] = pmap_eweight
        if map_vpreds:
            shortest_path_dag = {e for es in map_vpreds.values() for e in es}
            dpe["color"] = make_func_property_map(
                lambda e: "red" if e in shortest_path_dag else None
            )
        ipynb_display_graph(g, dpe=dpe)


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
    links: list,
    pmap_eweight: ReadWritePropertyMap,
    directed: bool = True,
    build_reverse_edge: bool = True
):
    def add_node(un, g, d):
        u = d.get(un)
        if u is None:
            u = g.add_vertex()
            d[un] = u
        return u

    g = DirectedGraph() if directed else UndirectedGraph()
    d = dict()
    for (un, vn, w) in links:
        u = add_node(un, g, d)
        v = add_node(vn, g, d)
        (e, added) = g.add_edge(u, v)
        assert added
        pmap_eweight[e] = w

        if build_reverse_edge:
            (e, added) = g.add_edge(v, u)
            assert added
            pmap_eweight[e] = w
    return g


def test_isolated_vertices():
    # Create 10 isolated vertices
    g = DirectedGraph(10)
    map_eweight = defaultdict()

    for s in g.vertices():
        map_vpreds = defaultdict(set)
        map_vdist = defaultdict()
        dijkstra_shortest_paths(
            g, s,
            make_assoc_property_map(map_eweight),
            make_assoc_property_map(map_vpreds),
            make_assoc_property_map(map_vdist)
        )

        # No incident arc in the shortest path DAG
        assert map_vpreds == dict()

        # Every target are at infinite distance excepted the source node.
        assert map_vdist == {
            u: INFINITY if u != s else 0
            for u in g.vertices()
        }


def test_simple_graph():
    # Prepare graph, just a 0 -> 1 arc
    g = DirectedGraph()
    u = g.add_vertex()
    v = g.add_vertex()
    (e, added) = g.add_edge(u, v)
    assert added
    w = 1
    map_eweight = defaultdict()
    map_eweight[e] = w

    # Call Dijkstra
    map_vpreds = defaultdict(set)
    map_vdist = defaultdict()
    dijkstra_shortest_paths(
        g, u,
        make_assoc_property_map(map_eweight),
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist),
        vis=DijkstraDebugVisitor()
    )

    # Check
    assert map_vpreds == {
        v: {e},
    }

    assert map_vdist == {
        u: 0,
        v: w
    }


def test_parallel_edges():
    # Prepare graph, two parallel edges from 0 to 1
    g = DirectedGraph()
    u = g.add_vertex()
    v = g.add_vertex()
    (e1, added) = g.add_edge(u, v)
    assert added
    (e2, added) = g.add_edge(u, v)
    assert added
    w = 1
    map_eweight = defaultdict()
    map_eweight[e1] = map_eweight[e2] = w

    # Call Dijkstra
    map_vpreds = defaultdict(set)
    map_vdist = defaultdict()
    dijkstra_shortest_paths(
        g, u,
        make_assoc_property_map(map_eweight),
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist)
    )

    # Check
    assert map_vpreds == {
        v: {e1, e2},
    }

    assert map_vdist == {
        u: 0,
        v: w
    }


class DijkstraDebugVisitor(DijkstraVisitor):
    def __init__(self, debug: bool = False):
        self.debug = debug

    def initialize_vertex(self, u: int, g: DirectedGraph):
        if self.debug:
            print(f"initialize_vertex({u})")

    def examine_vertex(self, u: int, g: DirectedGraph):
        if self.debug:
            print(f"examine_vertex({u})")

    def examine_edge(self, e: EdgeDescriptor, g: DirectedGraph):
        if self.debug:
            print(f"examine_edge({e} {e.m_distinguisher})")

    def discover_vertex(self, u: int, g: DirectedGraph):
        if self.debug:
            print(f"discover_vertex({u})")

    def edge_relaxed(self, e: EdgeDescriptor, g: DirectedGraph):
        if self.debug:
            print(f"edge_relaxed({e}  {e.m_distinguisher})")

    def edge_not_relaxed(self, e: EdgeDescriptor, g: DirectedGraph):
        if self.debug:
            print(f"edge_not_relaxed({e}  {e.m_distinguisher})")

    def finish_vertex(self, u: int, g: DirectedGraph):
        if self.debug:
            print(f"finish_vertex({u})")


def test_directed_graph(links: list = None):
    if links is None:
        links = LINKS
    map_eweight = defaultdict()
    pmap_eweight = make_assoc_property_map(map_eweight)
    g = make_graph(
        links,
        pmap_eweight,
        directed=True,
        build_reverse_edge=False
    )

    map_vpreds = defaultdict(set)
    map_vdist = defaultdict()
    dijkstra_shortest_paths(
        g, 0,
        pmap_eweight,
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist),
        vis=DijkstraDebugVisitor(debug=False)
    )

    edge_dict = {(g.source(e), g.target(e)): e for e in g.edges()}

    assert map_vpreds == {
        1: {edge_dict[0, 1]},
        2: {edge_dict[1, 2]},
        3: {edge_dict[1, 3]},
        4: {edge_dict[0, 4]},
        5: {edge_dict[0, 5]},
        6: {edge_dict[5, 6]},
        7: {edge_dict[6, 7]},
        8: {edge_dict[6, 8]},
    }
    assert map_vdist == {
        0: 0,
        1: 1,
        2: 2,
        3: 4,
        4: 1,
        5: 1,
        6: 9,
        7: 10,
        8: 10,
        9: INFINITY
    }


def test_decrease_key():
    g = DirectedGraph(3)
    (e01, _) = g.add_edge(0, 1)
    (e02, _) = g.add_edge(0, 2)
    (e21, _) = g.add_edge(2, 1)
    map_eweight = defaultdict(
        lambda: None,
        {
            e01: 9,
            e02: 1,
            e21: 1,
        }
    )
    pmap_eweight = make_assoc_property_map(map_eweight)

    map_vpreds = defaultdict(set)
    map_vdist = defaultdict()
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
        0: 0,
        1: 2,
        2: 1,
    }


def test_directed_symmetric_graph(links: list = None):
    if links is None:
        links = LINKS
    map_eweight = defaultdict()
    pmap_eweight = make_assoc_property_map(map_eweight)
    g = make_graph(LINKS, pmap_eweight, directed=True, build_reverse_edge=True)

    map_vpreds = defaultdict(set)
    map_vdist = defaultdict()
    dijkstra_shortest_paths(
        g, 0,
        pmap_eweight,
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist)
    )
    display_graph(g, pmap_eweight, map_vpreds)

    E = {(g.source(e), g.target(e)): e for e in g.edges()}

    assert map_vpreds == {
        1: {E[0, 1]},
        2: {E[1, 2]},
        3: {E[0, 3]},
        4: {E[0, 4]},
        5: {E[0, 5]},
        6: {E[8, 6]},
        7: {E[6, 7]},
        8: {E[2, 8]},
        9: {E[2, 9]}
    }
    assert map_vdist == {
        0: 0,
        1: 1,
        2: 2,
        3: 1,
        4: 1,
        5: 1,
        6: 4,
        7: 5,
        8: 3,
        9: 3
    }


def test_dijkstra_shortest_path(links: list = None):
    if links is None:
        links = LINKS
    # Prepare graph
    map_eweight = defaultdict(int)
    pmap_eweight = make_assoc_property_map(map_eweight)
    g = make_graph(links, pmap_eweight, build_reverse_edge=False)

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
            dpe={
                "color": make_func_property_map(
                    lambda e: "green" if e in path else "red"
                ),
                "label": pmap_eweight
            }
        )
    assert [
        (g.source(e), g.target(e))
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
    g = make_graph(links, pmap_eweight, build_reverse_edge=False)

    map_vpreds = defaultdict(set)
    map_vdist = defaultdict(int)
    s = 0

    dijkstra_shortest_paths(
        g, s,
        make_assoc_property_map(map_eweight),
        make_assoc_property_map(map_vpreds),
        make_assoc_property_map(map_vdist),
        compare=lambda a, b: a >= b,
        combine=min,
        zero=INFINITY,
        infty=0
    )
    display_graph(g, pmap_eweight)
    assert map_vdist == {
        0: INFINITY,
        1: 100,
        2: 80,
        3: 30
    }, map_vdist
