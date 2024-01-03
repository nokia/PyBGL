#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pybgl import (
    DirectedGraph,
    EdgeDescriptor,
    GraphDp,
    ReadPropertyMap,
    graph_to_html,
    html,
    in_ipynb,
    make_assoc_property_map, make_func_property_map,
    strong_components,
)


def edge_color(
    e: EdgeDescriptor,
    g: GraphDp,
    pmap_component: ReadPropertyMap,
    pmap_color: ReadPropertyMap,
    default_color: str = "black"
) -> str:
    """
    Returns the color assigned to an edge.

    Args:
        e: The edge being processed.
        g: The graph of being procesed.
        pmap_component (ReadPropertyMap): Maps each vertex with its strongly
            connected component.
        pmap_color (ReadPropertyMap): Maps a component ID with a color.
        default_color (str): The color returned if the color of the source
            and the target of e mismatch.

    Returns:
        The edge color.
    """
    u = g.source(e)
    v = g.target(e)
    color_u = pmap_color[pmap_component[u]]
    color_v = pmap_color[pmap_component[v]]
    return color_u if color_u == color_v else default_color


def strong_components_to_html(
    g: DirectedGraph,
    pmap_color: ReadPropertyMap,
    pmap_component: ReadPropertyMap
) -> str:
    """
    Run the GraphViz rendering for the :py:func:`strong_components` function.

    Args:
        g (DirectedGraph): A DirectedGraph.
        pmap_component (ReadPropertyMap): Maps each vertex with its strongly
            connected component.

    Returns:
        The corresponding HTML rendering.
    """
    return graph_to_html(
        g,
        dpv={
            "color": make_func_property_map(
                lambda u: pmap_color[pmap_component[u]]
            )
        },
        dpe={
            "color": make_func_property_map(
                lambda e: edge_color(e, g, pmap_component, pmap_color)
            ),
            "style": make_func_property_map(
                lambda e: (
                    "solid" if edge_color(
                        e, g, pmap_component, pmap_color, None
                    )
                    else "dashed"
                )
            ),
        }
    )


def test_strong_components():
    # Create the graph
    g = DirectedGraph(7)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    g.add_edge(3, 4)
    g.add_edge(4, 5)
    g.add_edge(5, 6)
    g.add_edge(6, 4)

    # Find strong connected components
    map_component = defaultdict(lambda: None)
    pmap_component = make_assoc_property_map(map_component)
    strong_components(g, pmap_component)

    # Rendering
    pmap_color = make_assoc_property_map(
        defaultdict(
            lambda: None,
            {
                0: "red",
                1: "blue",
                2: "green",
                3: "purple"
            }
        )
    )
    assert map_component == {
        0: 2,
        1: 1,
        2: 1,
        3: 1,
        4: 0,
        5: 0,
        6: 0,
    }

    if in_ipynb():
        html(
            strong_components_to_html(
                g, pmap_color, pmap_component
            ).replace("\\n", "")
        )
