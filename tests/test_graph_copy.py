#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import sys

from pybgl.graph                import DirectedGraph, add_edge, edges, num_edges, source, target, vertices
from pybgl.graph_dp             import GraphDp
from pybgl.graphviz             import dotstr_to_html
from pybgl.html                 import html
from pybgl.ipynb                import in_ipynb
from pybgl.property_map         import make_assoc_property_map, make_func_property_map
from pybgl.test_common          import run_tests
from pybgl.graph_copy           import graph_copy

def test_graph_copy_small(threshold :int = 50):
    g = DirectedGraph(5)
    (e01, _) = add_edge(0, 1, g)
    (e02, _) = add_edge(0, 2, g)
    (e04, _) = add_edge(0, 4, g)
    (e12, _) = add_edge(1, 2, g)
    (e23, _) = add_edge(2, 3, g)
    (e24, _) = add_edge(2, 4, g)
    (e40, _) = add_edge(4, 0, g)
    (e44, _) = add_edge(4, 4, g)
    map_eweight = {
        e01 : 83,
        e02 : 3,
        e04 : 78,
        e12 : 92,
        e23 : 7,
        e24 : 18,
        e40 : 51,
        e44 : 84,
    }
    pmap_eweight = make_assoc_property_map(map_eweight)
    pmap_erelevant = make_func_property_map(lambda e: pmap_eweight[e] >= threshold)

    g_dup = DirectedGraph(0)

    # Edge duplicate
    map_eweight_dup = dict()
    pmap_eweight_dup = make_assoc_property_map(map_eweight_dup)
    def callback_dup_edge(e, g, e_dup, g_dup):
        pmap_eweight_dup[e_dup] = pmap_eweight[e]

    # Vertex mapping
    map_vertices = dict()
    pmap_vertices = make_assoc_property_map(map_vertices)
    map_edges = dict()
    pmap_edges = make_assoc_property_map(map_edges)

    graph_copy(
        0, g, g_dup,
        pmap_erelevant    = pmap_erelevant,
        pmap_vertices     = pmap_vertices,
        pmap_edges        = pmap_edges,
        callback_dup_edge = callback_dup_edge
    )

    if in_ipynb():
        ori_html = dotstr_to_html(
            GraphDp(
                g,
                dpv = {
                    "label" : make_func_property_map(lambda u: "%s<br/>(becomes %s)" % (u, pmap_vertices[u]))
                },
                dpe = {
                    "color" : make_func_property_map(lambda e : "darkgreen" if pmap_erelevant[e] else "lightgrey"),
                    "style" : make_func_property_map(lambda e : "solid"     if pmap_erelevant[e] else "dashed"),
                    "label" : pmap_eweight,
                }
            ).to_dot()
        )
        dup_html = dotstr_to_html(
            GraphDp(
                g_dup,
                dpe = {
                    "label" : pmap_eweight_dup,
                }
            ).to_dot()
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
            0 : 0,
            1 : 1,
            2 : 2,
            4 : 3
        }
        for e, e_dup in map_edges.items():
            u = source(e, g)
            v = target(e, g)
            u_dup = source(e_dup, g_dup)
            v_dup = target(e_dup, g_dup)
            assert u_dup == pmap_vertices[u], "u_dup = %s ; pmap_vertices[%s] = %s" % (u_dup, u, pmap_vertices[u])
            assert v_dup == pmap_vertices[v], "v_dup = %s ; pmap_vertices[%s] = %s" % (v_dup, v, pmap_vertices[v])
            assert pmap_eweight[e] == pmap_eweight_dup[e_dup]
    elif threshold < min([w for w in map_eweight.values()]):
        expected_num_edges = num_edges(g)
    elif threshold > max([w for w in map_eweight.values()]):
        expected_num_edges = 0

    assert expected_num_edges == num_edges(g_dup), \
        """
        Invalid edge number:
          Expected: %s
          Obtained: %s
        """ % (expected_num_edges, num_edges(g_dup))

#--------------------------------------------------
# Main program
#--------------------------------------------------

def test_graph_copy():
    """
    Runs the suite test related to CorrelationReverser* classes.
    """
    run_tests([
        (test_graph_copy_small, (0,   )),
        (test_graph_copy_small, (50,  )),
        (test_graph_copy_small, (100, )),
    ])

