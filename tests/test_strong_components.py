#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#   ./test_strong_components.py > foo.svg
#
# Authors:
#   Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

from pybgl.graph             import DirectedGraph, add_edge, source, target, vertices
from pybgl.graph_dp          import GraphDp
from pybgl.graphviz          import dotstr_to_html, graph_to_html
from pybgl.strong_components import strong_components
from pybgl.property_map      import make_assoc_property_map, make_func_property_map

def edge_color(e, g, pmap_component, pmap_color, default_color = "black"):
    """
    Returns the color assigned to an edge.
    Args:
        e: An EdgeDescriptor.
        g: A DirectedGraph.
        pmap_component: A ReadPropertyMap, mapping a vertex with its strongly
            connected component.
        pmap_color: A ReadPropertyMap, mapping a component ID with a color.
        default_color: color returned if the color of the source and the
            target of e mismatch.
    """
    u = source(e, g)
    v = target(e, g)
    color_u = pmap_color[pmap_component[u]]
    color_v = pmap_color[pmap_component[v]]
    return color_u if color_u == color_v else default_color

def display_strong_components(g, pmap_color, pmap_component) -> str:
    """
    Args:
        g: A DirectedGraph.
        pmap_component: A ReadPropertyMap, mapping a vertex with its strongly
            connected component.
    """
    html = dotstr_to_html(GraphDp(
        g,
        {
            "color" : make_func_property_map(lambda u : pmap_color[pmap_component[u]])
        }, {
            "color" : make_func_property_map(lambda e : edge_color(e, g, pmap_component, pmap_color)),
            "style" : make_func_property_map(lambda e : \
                "solid" if edge_color(e, g, pmap_component, pmap_color, None) else \
                "dashed"
            ),
        }
    ).to_dot())

    return html

#-------------------------------------------------------------
# Main program
#-------------------------------------------------------------

# Create the graph
g = DirectedGraph(7)
add_edge(0, 1, g)
add_edge(1, 2, g)
add_edge(2, 3, g)
add_edge(3, 1, g)
add_edge(3, 4, g)
add_edge(4, 5, g)
add_edge(5, 6, g)
add_edge(6, 4, g)

# Find strong connected components
pmap_component = make_assoc_property_map({u : None for u in vertices(g)})
strong_components(g, pmap_component)

# Rendering
pmap_color = make_assoc_property_map({
    0 : "red",
    1 : "blue",
    2 : "green",
    3 : "purple"
})

print(display_strong_components(g, pmap_color, pmap_component).replace("\\n", ""))

