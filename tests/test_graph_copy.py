#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl import (
    DirectedGraph,
    graph_to_html,
    html,
    in_ipynb,
    make_assoc_property_map, make_func_property_map,
)
from pybgl.graph_copy import graph_copy


def _test_graph_copy_small(threshold: int = 50):
    g = DirectedGraph(5)
    (e01, _) = g.add_edge(0, 1)
    (e02, _) = g.add_edge(0, 2)
    (e04, _) = g.add_edge(0, 4)
    (e12, _) = g.add_edge(1, 2)
    (e23, _) = g.add_edge(2, 3)
    (e24, _) = g.add_edge(2, 4)
    (e40, _) = g.add_edge(4, 0)
    (e44, _) = g.add_edge(4, 4)
    map_eweight = defaultdict(
        lambda: None,
        {
            e01: 83,
            e02: 3,
            e04: 78,
            e12: 92,
            e23: 7,
            e24: 18,
            e40: 51,
            e44: 84,
        }
    )
    pmap_eweight = make_assoc_property_map(map_eweight)
    pmap_erelevant = make_func_property_map(
        lambda e: pmap_eweight[e] >= threshold
    )

    g_dup = DirectedGraph(0)

    # Edge duplicate
    map_eweight_dup = defaultdict()
    pmap_eweight_dup = make_assoc_property_map(map_eweight_dup)

    def callback_dup_edge(e, g, e_dup, g_dup):
        pmap_eweight_dup[e_dup] = pmap_eweight[e]

    # Vertex mapping
    map_vertices = defaultdict()
    pmap_vertices = make_assoc_property_map(map_vertices)
    map_edges = defaultdict()
    pmap_edges = make_assoc_property_map(map_edges)

    graph_copy(
        0, g, g_dup,
        pmap_erelevant=pmap_erelevant,
        pmap_vertices=pmap_vertices,
        pmap_edges=pmap_edges,
        callback_dup_edge=callback_dup_edge
    )

    if in_ipynb():
        ori_html = graph_to_html(
            g,
            dpv={
                "label": make_func_property_map(
                    lambda u: f"{u}<br/>(becomes {pmap_vertices[u]})"
                )
            },
            dpe={
                "color": make_func_property_map(
                    lambda e: "darkgreen" if pmap_erelevant[e] else "lightgrey"
                ),
                "style": make_func_property_map(
                    lambda e: "solid" if pmap_erelevant[e] else "dashed"
                ),
                "label": pmap_eweight,
            }
        )
        dup_html = graph_to_html(
            g_dup,
            dpe={
                "label": pmap_eweight_dup,
            }
        )
        html(
            """
            <table>
                <tr>
                    <th>Original</th>
                    <th>Extracted</th>
                </tr><tr>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
            </table>
            """ % (ori_html, dup_html)
        )

    if threshold == 50:
        expected_num_edges = 5
        assert map_vertices == {
            0: 0,
            1: 1,
            2: 2,
            4: 3
        }
        for e, e_dup in map_edges.items():
            u = g.source(e)
            v = g.target(e)
            u_dup = g_dup.source(e_dup)
            v_dup = g_dup.target(e_dup)
            assert u_dup == pmap_vertices[u], (
                f"u_dup = {u_dup} ; pmap_vertices[{u}] = {pmap_vertices[u]}"
            )
            assert v_dup == pmap_vertices[v], (
                f"v_dup = {v_dup} ; pmap_vertices[{v}] = {pmap_vertices[v]}"
            )
            assert pmap_eweight[e] == pmap_eweight_dup[e_dup]
    elif threshold < min(w for w in map_eweight.values()):
        expected_num_edges = g.num_edges()
    elif threshold > max(w for w in map_eweight.values()):
        expected_num_edges = 0

    assert expected_num_edges == g_dup.num_edges(), (
        f"""
        Invalid edge number:
          Expected: {expected_num_edges}
          Obtained: {g_dup.num_edges()}
        """
    )


def test_graph_copy_small():
    for threshold in [0, 50, 100]:
        _test_graph_copy_small(threshold)
