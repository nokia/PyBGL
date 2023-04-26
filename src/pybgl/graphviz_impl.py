#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

# !!! This file must have NO dependency on .graph to avoid mutual inclusion
import re
from .singleton import Singleton
from .tokenize import TokenizeVisitor, tokenize

#------------------------------------------------------------------
# Graphviz style
#------------------------------------------------------------------

class GraphvizStyle(metaclass=Singleton):
    """
    The :py:class:`GraphvizStyle` class is a singleton that
    configure the default style used to render PyBGL graphs
    in a Jupyter notebook.

    It is useful if you want graph adapted e.g. for dark themes.

    Example:
        >>> from pybgl.graph import DirectedGraph, GraphvizStyle, ipynb_display_graph
        >>> GraphvizStyle.set_fg_color("grey")
        >>> GraphvizStyle.set_bg_color("transparent")
        >>> display_graph = ipynb_display_graph
        >>> g = DirectedGraph(2)
        >>> g.add_edge(0, 1)
        >>> display_graph(g)
    """
    graph = {
        "fontcolor": "black",
        "bgcolor": "transparent",
        "rankdir": "LR",
    }
    node = {
        "color": "black",
        "fontcolor": "black",
        "fillcolor": "transparent",
        "shape": "circle",
    }
    edge = {
        "color": "black",
        "fontcolor": "black",
    }
    extra_style = list() # splines, etc

    @staticmethod
    def set_fg_color(color: str):
        """
        Sets the foreground color used to render graphs.

        Args:
            color (str): A graphviz color. If you want to use HTML color, see
                :py:func:`html_to_graphviz`.
        """
        GraphvizStyle.graph["fontcolor"] = color
        GraphvizStyle.node["color"] = color
        GraphvizStyle.node["fontcolor"]  = color
        GraphvizStyle.edge["color"] = color
        GraphvizStyle.edge["fontcolor"]  = color

    @staticmethod
    def set_bg_color(color):
        """
        Sets the background color used to render graphs.

        Args:
            color (str): A graphviz color. If you want to use HTML color, see
                :py:func:`html_to_graphviz`.
        """
        GraphvizStyle.graph["bgcolor"] = color

    @staticmethod
    def attributes_to_dot(prefix: str, d: dict) -> str:
        """
        Internal method, used to convert this :py:class:`GraphvizStyle`
        attribute to Graphviz attributes.

        Args:
            prefix (str): A string in ``"graph"``, ``"node"``, ``"edge"``.
            d (dict): The ``prefix``-related style attributes.

        Returns:
            The corresponding Graphviz string.
        """
        return "%s [%s]" % (
            prefix,
            "; ".join([
                "%s=\"%s\"" % (k, v) for k, v in d.items()
            ])
        ) if d else ""

    def __str__(self) -> str:
        """
        String representation of this :py:class:`GraphvizStyle` instance.

        Returns:
            The corresponding string.
        """
        return "; ".join(
            [
                GraphvizStyle.attributes_to_dot("graph", GraphvizStyle.graph),
                GraphvizStyle.attributes_to_dot("node", GraphvizStyle.node),
                GraphvizStyle.attributes_to_dot("edge", GraphvizStyle.edge)
            ] + GraphvizStyle.extra_style
        )

#------------------------------------------------------------------
# Graphviz write utilities
# See also Graph.to_dot() and GraphDp.to_dot()
#------------------------------------------------------------------

GRAPHVIZ_SUPPORTED_HTML_TAGS = {
    "b", "/b", "br", "br/", "font", "/font", "hr", "/hr", "i", "/i",
    "img", "/img", "o", "/o", "s", "/s", "sub", "/sub", "sup", "/sup",
    "table", "/table", "td", "/td", "tr", "/tr", "u", "/u", "vr", "/vr",
}

GRAPHVIZ_HTML_TOKENIZER = re.compile(
    "|".join(
        "<\\s*%s%s\\s*>" % (
            tag,
            "(\\s[^>]*)?" if tag[0] != "/" else ""
        )
        for tag in GRAPHVIZ_SUPPORTED_HTML_TAGS
    ),
    re.IGNORECASE
)

# The following characters makes crash graphviz when involved in a <label>,
# so we replace them by their corresponding HTML representation. Note that
# graphviz does not support HTML entity (e.g. "&amp;") and that is why we
# rely on the HTML code (e.g. "&#38;").
GRAPHVIZ_MAP_CHAR_ESCAPED = {
    '&': "&#38;",  # &amp;
    "<": "&#60;",  # &lt;
    ">": "&#62;",  # &gt;
    "\n": "\\n",
    "\t": "\\t",
    "\r": "\\r",
    "[": "&#91;",  # "&lbrack;"
    "]": "&#93;",  # "&rbrack;"
    "{": "&#123;", # "&lbrace;"
    "}": "&#125;", # "&rbrace;"
}

def graphviz_escape_char(a: str) -> str:
    """
    Escapes a character that must be involved in a Graphviz string.

    Args:
        a (str): A (possibly special) character.

    Returns:
        The corresponding escaped character for Graphviz.
    """
    escaped = GRAPHVIZ_MAP_CHAR_ESCAPED.get(a)
    if escaped is None and ord(a) < 32:
        escaped = "\\x%02x;" % ord(a)
    return escaped if escaped is not None else a

class EscapeHtmlTokenizeVisitor(TokenizeVisitor):
    """
    Internal class used by the :py:func:`graphviz_escape_html` function.
    """
    def __init__(self):
        self.out = ""

    def on_unmatched(self, unmatched: str, start: int, end: int, s: str):
        for a in unmatched:
            self.out += graphviz_escape_char(a)

    def on_matched(self, matched: str, start: int, end: int, s: str):
        self.out += matched

def graphviz_escape_html(s: str) -> str:
    """
    Escapes a string that must be involved in a Graphviz string.

    Args:
        s (str): A string involving possibly special characters.

    Returns:
        The corresponding escaped string for Graphviz.
    """
    vis = EscapeHtmlTokenizeVisitor()
    tokenize(GRAPHVIZ_HTML_TOKENIZER, s, vis)
    return vis.out

#------------------------------------------------------------------
# Graphviz export
# See also Graph.to_dot() and GraphDp.to_dot()
#------------------------------------------------------------------

# TODO factorize with attributes_to_dot
def graphviz_properties_to_str(x: object, dpx: dict) -> str:
    """
    Internal method, used to exports a vertex or an edge as
    well at its style to the corresponding Graphviz string.
    See the :py:func:`vertex_to_graphviz` and :py:func:`edge_to_graphviz`
    functions.

    Args:
        x (object): The vertex or the edge to be exported.
        dpx (dict): The corresponding style.
            See also :py:class:`GraphDp` class.

    Returns:
        The resulting Graphviz string.
    """
    return "[%s]" % "; ".join([
        "%s=\"%s\"" % (k, pmap[x]) if k != "label" else
        "%s=<%s>"   % (k, graphviz_escape_html(str(pmap[x])))
        for (k, pmap) in dpx.items()
        if pmap[x] is not None
    ]) if dpx else ""

def default_graphviz_style() -> str:
    """
    Crafts the default Graphviz string corresponding to the default style
    used to render a graph.

    Returns:
        The corresponding Graphviz string.
    """
    return str(GraphvizStyle())

def vertex_to_graphviz(
    u: int,
    g,
    dpv: dict = None,
    vertex_to_str: callable = None
) -> str:
    """
    Exports a vertex as well as its style properties to Graphviz.

    Args:
        u (int): The considered vertex.
        g (Graph): The considered graph.
        dpv (dict): The vertex-based style.
            See also :py:class:`GraphDp` class.
        vertex_to_str (callable): A function used to convert a vertex
            descriptor to the corresponding Graphviz vertex identifier.
            This is useful if the vertex descriptor is more sophisticated
            than an ``int`` (e.g., a tuple).

    Returns:
        The corresponding Graphviz string.
    """
    if not vertex_to_str: vertex_to_str = str
    return " ".join([vertex_to_str(u), graphviz_properties_to_str(u, dpv)])

def graphviz_arc(g, is_directed: bool = None) -> str:
    """
    Returns the appropriate string for directed/undirected edge declarations
    in Graphviz.

    Returns:
        ``"->"`` if the graph is directed,
        ``"--"`` otherwise.
    """
    if is_directed is None:
        is_directed = lambda g: g.is_directed()
    return "->" if is_directed else "--"

def graphviz_type(g, is_directed: bool = None) -> str:
    """
    Returns the appropriate string for directed/undirected graph declarations
    in Graphviz.

    Returns:
        ``"digraph"`` if the graph is directed,
        ``"graph"`` otherwise.
    """
    if is_directed is None:
        is_directed = lambda g: g.is_directed()
    return "digraph" if is_directed else "graph"

def graphviz_dx_to_dot(prefix: str, dx: dict) -> str:
    assert prefix in {"graph", "node", "edge"}
    return "%s [%s]" % (
        prefix,
        "; ".join([
            "%s=\"%s\"" % (k, v)
            for (k, v) in dx.items()
        ])
    ) if dx else ""

def edge_to_graphviz(
    e,
    g,
    dpe: dict = None,
    source: callable = None,  # TODO to remove
    target: callable = None,  # TODO to remove
    is_directed: bool = None,
    vertex_to_str: callable = None
) -> str:
    """
    Exports a edge as well as its style properties to Graphviz.

    Args:
        e (int): The considered edge.
        g (Graph): The considered graph.
        dpe (dict): The edge-based style.
            See also :py:class:`GraphDp` class.
        vertex_to_str (callable): A function used to convert a vertex
            descriptor to the corresponding Graphviz vertex identifier.
            This is useful if the vertex descriptor is more sophisticated
            than an ``int`` (e.g., a tuple).

    Returns:
        The corresponding Graphviz string.
    """
    if source is None:
        source = lambda e, g: g.source(e)
    if target is None:
        target = lambda e, g: g.target(e)
    if is_directed is None:
        is_directed = lambda g: g.is_directed()
    if vertex_to_str is None:
        vertex_to_str = str
    return " ".join([
        vertex_to_str(source(e, g)),
        graphviz_arc(g, is_directed),
        vertex_to_str(target(e, g)),
        graphviz_properties_to_str(e, dpe)
    ])

def enrich_kwargs(default_d: dict, key: str, **kwargs) -> dict:
    """
    Add a key value pair in a dictionnary involved in the values of ``**kwargs``.
    This function is commonly used in the methods that inherit
    the :py:class:`Graph.to_dot` method to complete the Graphviz style.
    See for example the the :py:class:`Automaton.to_dot` method.

    Args:
        default_d (dict): The source dictionnary, containing the key
            value pairs used to complete ``**kwargs``.
        key (dict): The key of ``**kwargs`` to update.

    Returns:
        The updated ``**kwargs``.
    """
    if default_d:
        if not key in kwargs:
            kwargs[key] = dict()
        for (k, v) in default_d.items():
            if k not in kwargs[key].keys():
                kwargs[key][k] = v
    return kwargs

# TODO GraphView
def to_dot(
    g,
    vs: iter = None,
    es: iter = None,
    dg: dict = None,
    extra_style: str  = None,
    dv: dict = None,
    de: dict = None,
    dpv: dict = None,
    dpe: dict = None,
    graphviz_style: str = None,
    source: callable = None,
    target: callable = None,
    is_directed: bool = None,
    vertex_to_str: callable = None
) -> str:
    """
    Internal method, used for Graphviz rendering.
    Exports a graph to its corresponding Graphviz string.
    See also :py:class:`GraphDp`.

    Args:
        g (Graph): The graph to be rendered.
        vs (iter): A subset of vertices of ``g``.
            If you pass ``None``, iterates over all the vertices.
            Use rather :py:class:`GraphView`.
        es (iter): A subset of edges of ``g``.
            If you pass ``None``, iterates over all the edges.
            Use rather :py:class:`GraphView`.
        dpv (dict): Per-vertex style. It maps a vertex Graphviz attribute with the
            corresponding vertex-based :py:class:`ReadPropertyMap` instance.
        dpe (dict): Per-edge style. It maps a edge Graphviz attribute with the
            corresponding edge-based :py:class:`ReadPropertyMap` instance.
        dg (dict): Graph attributes.
        dv (dict): Default vertex style. It maps a vertex Graphviz attribute
            with the corresponding value.
        de (dict): Default edge style. It maps a edge Graphviz attribute
            with the corresponding value.
        graphviz_style (list): Extra style (splines, etc).
        source (callable): Callback used to extract the vertex descriptor
            corresponding to the source of an edge descriptor.
        target (callable): Callback used to extract the vertex descriptor
            corresponding to the target of an edge descriptor.
        is_directed (bool): Pass ``True`` if ``g`` is directed,
            ``False`` otherwise. You may pass ``None`` to let the function
            detect what is the appropriate value.
        vertex_to_str (callable): A function used to convert a vertex
            descriptor to the corresponding Graphviz vertex identifier.
            This is useful if the vertex descriptor is more sophisticated
            than an ``int`` (e.g., a tuple).

    Returns:
        The corresponding Graphviz string.
    """
    if vs is None:
        vs = (u for u in g.vertices())
    if es is None:
        es = (e for e in g.edges())
    if source is None:
        source = lambda e, g: g.source(e)
    if target is None:
        target = lambda e, g: g.target(e)
    if is_directed is None:
        is_directed = g.directed
    if graphviz_style is None:
        graphviz_style = default_graphviz_style()
    if vertex_to_str  is None:
        vertex_to_str = str

    dg = graphviz_dx_to_dot("graph", dg)
    dv = graphviz_dx_to_dot("node", dv)
    de = graphviz_dx_to_dot("edge", de)
    instructions = (
          ([graphviz_style] if graphviz_style else [])
        + ([dg] if dg else [])
        + ([dv] if dv else [])
        + ([de] if de else [])
        + ([extra_style] if extra_style else [])
        + [vertex_to_graphviz(u, g, dpv, vertex_to_str) for u in vs]
        + [
            edge_to_graphviz(e, g, dpe, source, target, is_directed, vertex_to_str)
            for e in es
        ]
    )

    return "%(type)s G {%(instructions)s}" % {
        "type":  "digraph" if is_directed else "graph",
        "instructions":  "\n  %s;\n" % ";\n  ".join(instructions) if instructions else ""
    }
