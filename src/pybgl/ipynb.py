#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Jupyter ipython notebook utilities.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .graphviz import dotstr_to_html
from .html import html

def in_ipynb() -> bool:
    """
    Tests whether the code is running inside a Jupyter Notebook.

    Returns:
        True iff the code is running inside a Jupyter Notebook.
    """
    try:
        from IPython import get_ipython
        return str(type(get_ipython())) == "<class 'ipykernel.zmqshell.ZMQInteractiveShell'>"
    except NameError:
        return False
    except ImportError:
        return False

def background_template_html(background_color: str = None) -> str:
    """
    Crafts an HTML template to nest HTML code in a div setting the background to
    a given color.

    Example:
        >>> from pybgl import DirectedGraph, html, background_template_html, graph_to_html
        >>> g = DirectedGraph(2)
        >>> g.add_edge(0, 1)
        >>> html(background_template_html("white") % graph_to_html(g))

    Args:
        background_color (str): An HTML color.

    Returns:
        The corresponding HTML template.
    """
    return "<div style='background-color:%s'>%%s</div>" % background_color if background_color else "%s"

def ipynb_display_graph(g, background_color: str = None, **kwargs):
    """
    Display a Graph in a Jupyter Notebook.
    If the graph is too tiny, see :py:func:display_svg instead.

    Args:
        g (Graph): The graph to display
        background_color (str): An HTML color.
        **kwargs (dict): See the :py:meth:`Graph.to_dot` method.
    """
    template_html = background_template_html(background_color)
    engine = kwargs.pop("engine", "dot")
    html(
        template_html % dotstr_to_html(
            g.to_dot(**kwargs),
            engine=engine
        )
    )

def display_svg(svg, filename_svg: str, background_color: str = None):
    """
    Writes SVG content into and display it in a Jupyter Notebook with an HTML link.
    This is useful is the graph is too large to be readable in Jupyter.
    See also the :py:func:`display_body` function if the generated HTML must be standalone.

    Args:
        svg (str): The SVG content.
        filename_svg (str): The path to the SVG file in which ``svg`` will be dumped.
        background_color (str): An HTML color or ``None`` if not needed.

    Example:
        >>> from pybgl import DirectedGraph, html, background_template_html, graph_to_html
        >>> g = DirectedGraph(2)
        >>> g.add_edge(0, 1)
        >>> display_svg(graph_to_html(g), "graph.svg", background_color="white")
    """
    with open(filename_svg, "w") as f:
        print(svg, file = f)
        html("<a href='%s' target='_blank'>View</a>" % filename_svg)
    template_html = background_template_html(background_color)
    html(template_html % svg)

def display_body(body_html, filename_html, background_color: str = None) -> str:
    """
    Wraps HTML content in an HTML body tag.

    Args:
        body_html (str): The HTML content.
        filename_html (str): The path of the HTML file in which ``body_html`` will be dumped.
        background_color (str): An HTML color or ``None`` if not needed.
    """
    display_svg(
        "<html><head><meta charset='UTF-8'></head><body>%s</body></html>" % body_html,
        filename_html,
        background_color=background_color
    )
