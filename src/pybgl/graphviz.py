#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the PyBGL project.
# https://github.com/nokia/pybgl

import re, sys

from html.parser import HTMLParser
from subprocess import Popen, PIPE
from .graph import Graph, EdgeDescriptor
from .graphviz_impl import *

#------------------------------------------------------------------
# Graphviz read
#------------------------------------------------------------------

class GraphvizOptsParser(HTMLParser):
    """
    Implementation details for the: py:class:`ReadGraphvizVisitor` class.
    used to parse the options related to a vertex or an edge.
    """
    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.d = dict()

    def handle_starttag(self, tag, attrs):
        for (k, v) in attrs:
            self.d[k] = v

    def feed(self, graphviz_opts):
        if graphviz_opts:
            graphviz_opts= "<fake_tag " + graphviz_opts[1:-1] + ">"
            super().feed(graphviz_opts)

    def items(self):
        return self.d.items()

class GraphvizVisitor():
    """
    Base of the: py:class:`GraphvizVisitor` class.
    """
    def on_vertex(self, line: str, u: int, opts: str):
        pass
    def on_edge(self, line: str, u: int, v: int, opts: str):
        pass
    def on_else(self, line: str):
        pass

class ReadGraphvizVisitor(GraphvizVisitor):
    """
    The: py:class:`ReadGraphvizVisitor` is used to implement
    the: py:func:`read_graphviz` function. It is used to
    initialize a: py:class:`Graph` instance from a
    Graphviz file.
    """
    def __init__(self, g: Graph):
        """
        Constructor.

        Args:
            g: The graph to populate.
        """
        super().__init__()
        self.m_g = g
        self.m_aliases = dict()

    def on_install_vertex_property(self, u, g, key, value):
        pass

    def on_install_edge_property(self, e, g, key, value):
        pass

    def on_vertex(self, line: str, u_alias: int, opts: str) -> int:
        u = self.m_g.add_vertex()
        self.m_aliases[u_alias] = u
        parser = GraphvizOptsParser()
        parser.feed(opts)
        for (key, value) in parser.items():
            self.on_install_vertex_property(u, self.m_g, key, value)
        return u

    def on_edge(self, line: str, u_alias: int, v_alias: int, opts: str) -> EdgeDescriptor:
        u = self.m_aliases[u_alias]
        v = self.m_aliases[v_alias]
        (e, added) = self.m_g.add_edge(u, v)
        assert added
        parser = GraphvizOptsParser()
        parser.feed(opts)
        for (key, value) in parser.items():
            self.on_install_edge_property(e, self.m_g, key, value)
        return e

PATTERN_SPACE = "\\s*"
PATTERN_VERTEX_ID = "([0-9]+)"
PATTERN_EDGE_CONNECTOR = "->" # TODO manage -- for undirected graphs
PATTERN_OPTS = "(\\[(.*)\\])?"
PATTERN_LINE_VERTEX = PATTERN_SPACE.join([PATTERN_VERTEX_ID, PATTERN_OPTS, ";"])
PATTERN_LINE_EDGE = PATTERN_SPACE.join([
    PATTERN_VERTEX_ID, PATTERN_EDGE_CONNECTOR,
    PATTERN_VERTEX_ID, PATTERN_OPTS, ";"
])

RE_GRAPHVIZ_SVG = re.compile(".*(<svg.*>.*</svg>).*")
RE_LINE_VERTEX = re.compile(PATTERN_LINE_VERTEX)
RE_LINE_EDGE = re.compile(PATTERN_LINE_EDGE)

def read_graphviz(iterable, g: Graph, vis: ReadGraphvizVisitor = None):
    """
    Read an iterable where each element is a line of a graphviz string to
    extract a graph, but not its attributes. See read_graphviz_dp if needed.
    This function expect at most one vertex per line and one edge per line.

    Assumptions:

    - The vertices are identified using integer
    - The vertices are described in the dot file before the edges
    - The vertex/edge attributes are not too weird strings

    See the: py:func:`read_graphviz_dp` function to load Graphviz styles.

    Args:
        iterable: The input Graphviz lines (e.g. my_file.readlines() or my_str.splitlines())
        g (Graph): Pass an empty: py:class:`DirectedGraph` or: py:class:`UndirectedGraph`
            instance.
    """
    if not vis:
        vis = ReadGraphvizVisitor(g)
    for line in iterable:
        line = line.strip()
        m_v = RE_LINE_VERTEX.match(line)
        if m_v:
            vis.on_vertex(line, int(m_v.group(1)), m_v.group(2))
            continue
        m_e = RE_LINE_EDGE.match(line)
        if m_e:
            vis.on_edge(line, int(m_e.group(1)), int(m_e.group(2)), m_e.group(3))
            continue
        vis.on_else(line)

#------------------------------------------------------------------
# Graphviz read with dynamic property (dp)
#------------------------------------------------------------------

class ReadGraphvizDpVisitor(ReadGraphvizVisitor):
    """
    The: py:class:`ReadGraphvizDpVisitor` is used to implement
    the: py:func:`read_graphviz_dp` function. It is used to
    initialize a: py:class:`Graph` instance from a
    Graphviz file.
    """
    def __init__(self, g, dpv: dict, dpe: dict):
        super().__init__(g)
        self.m_dpv = dpv
        self.m_dpe = dpe

    def on_install_vertex_property(self, u, g, key, value):
        pmap = self.m_dpv[key] if self.m_dpv else None
        if pmap: pmap[u] = value

    def on_install_edge_property(self, e, g, key, value):
        pmap = self.m_dpe[key] if self.m_dpe else None
        if pmap: pmap[e] = value

def read_graphviz_dp(iterable: iter, g: Graph, dpv: dict = None, dpe: dict = None):
    """
    Read an iterable where each element is a line of a graphviz string to
    extract a graph and its node/edge attributes.
    This function expect at most one vertex per line and one edge per line.

    Args:
        iterable: An iterable (e.g. my_file.readlines() or my_str.splitlines())
        g: Pass an empty DirectedGraph.
        dpv: Pass an empty dict if needed. It will map for each vertex a
            dict mapping each specified graphviz attributes with its value.
        dpe: Pass an empty dict if needed. It will map for each edge a
            dict mapping each specified graphviz attributes with its value.
    """
    vis = ReadGraphvizDpVisitor(g, dpv, dpe)
    read_graphviz(iterable, g, vis)

#------------------------------------------------------------------
# Graphviz call
#------------------------------------------------------------------

def error(*cls):
    """
    Prints an error message.
    """
    print(*cls, file=sys.stderr)

def run_graphviz(s_dot: str, layout_engine: str = "dot", format: str = "svg") -> bytes:
    """
    Converts a dot string (graphviz format) into a graphic file.

    Args:
        s_dot: A string in the graphviz format.
        layout_engine: The graphviz engine used for the rendering.
            See "man dot" for more details.
        format: The output graphviz terminal.
            See "man dot" for more details.

    Returns:
        The bytes/str of the output image iff successful, None otherwise.
    """
    cmd = ['dot', '-T' + format, '-K', layout_engine]
    dot = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = dot.communicate(s_dot.encode("utf-8"))
    status = dot.wait()
    if status == 0:
        if format == "svg":
            return stdout_data.decode("utf-8")
        else:
            return stdout_data
    else:
        error(f"dot returned {status}\n[==== stderr ====]\n{stderr_data.decode('utf-8')}")
        error("Input dot string was:\n%s\n" % s_dot)
        raise RuntimeError("run_graphviz: invalid string")

def dot_to_svg(s_dot: str, engine: str = "dot", format: str = "svg") -> str:
    """
    Converts a Graphviz string to SVG.

    Args:
        s_dot (str): A Graphviz string.
        engine (str): A graphviz engine (e.g.,
            ``"dot"``, ``"fdp"``, ``"neato"``, ...).
        format (str): The output graphviz terminal, e.g. ``"svg"``, ``"png"``.
            See `man dot <https://linux.die.net/man/1/dot>`__ for more details.

    Returns:
        The corresponding SVG string.
    """
    bytes_img = run_graphviz(s_dot, engine, format)
    if isinstance(bytes_img, bytes): # This should no more occur
        return bytes_img.decode("utf-8")
    elif isinstance(bytes_img, str):
        i = bytes_img.find("<svg")
        return bytes_img[i:]
    return None

def write_graphviz(s_dot: str, filename: str, engine: str = "dot", format: str = "svg") -> bool:
    """
    Writes a dot string (Graphviz format) into a graphic file.

    Args:
        s_dot (str): A string in the graphviz format.
        filename (str): The path of the output file.
        engine (str): A graphviz engine (e.g.,
            ``"dot"``, ``"fdp"``, ``"neato"``, ...).
        format (str): The output graphviz terminal, e.g. ``"svg"``, ``"png"``.
            See `man dot <https://linux.die.net/man/1/dot>`__ for more details.

    Returns:
        True iff successful.
    """
    def write_graphviz_impl(
        s_dot: str,
        filename: str,
        format: str = "svg",
        engine: str = "dot"
    ) -> bool:
        ret = False
        bytes_img = run_graphviz(s_dot, engine, format)
        if bytes_img:
            print(bytes_img.decode("utf-8"), file = filename)
            ret = True
        return ret

    if isinstance(filename, str):
        with open(filename, "w") as f_img:
            return write_graphviz_impl(s_dot, filename, format, engine)
    else:
        return write_graphviz_impl(s_dot, filename, format, engine)

def dotstr_to_html(s_dot: str, engine = "dot") -> str:
    """
    Converts a Graphviz string to a HTML string.

    Args:
        s_dot (str): A dot string.
        engine (str): A graphviz engine (e.g.,
            ``"dot"``, ``"fdp"``, ``"neato"``, ...).

    Returns:
        The corresponding HTML string.
    """
    return str(run_graphviz(s_dot, engine, format="svg"))

def graph_to_html(g, engine: str = "dot", **kwargs) -> str:
    """
    Converts a graph to a HTML string.

    Args:
        g (Graph): The input graph.
        engine (str): A graphviz engine (e.g. "dot", "fdp", "neato", ...).
        **kwargs (dict): See the: py:meth:`Graph.to_dot` method.

    Returns:
        The corresponding HTML string.
    """
    s_dot = g.to_dot(**kwargs)
    return dotstr_to_html(s_dot, engine)
