#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

import re, sys

from subprocess     import Popen, PIPE
from .graph         import Graph, add_vertex, add_edge, EdgeDescriptor
from .graphviz_impl import *

#------------------------------------------------------------------
# Graphviz parser
#------------------------------------------------------------------

PATTERN_SPACE          = "\\s*"
PATTERN_VERTEX_ID      = "([0-9]+)"
PATTERN_EDGE_CONNECTOR = "->" #TODO manage -- for undirected graphs
PATTERN_OPTS           = "\[(.*)\]"
PATTERN_LINE_VERTEX    = PATTERN_SPACE.join([PATTERN_VERTEX_ID, PATTERN_OPTS, ";"])
PATTERN_LINE_EDGE      = PATTERN_SPACE.join([PATTERN_VERTEX_ID, PATTERN_EDGE_CONNECTOR, PATTERN_VERTEX_ID, PATTERN_OPTS, ";"])

RE_GRAPHVIZ_SVG = re.compile(".*(<svg.*>.*</svg>).*")
RE_LINE_VERTEX = re.compile(PATTERN_LINE_VERTEX)
RE_LINE_EDGE = re.compile(PATTERN_LINE_EDGE)

class GraphvizVisitor():
    def on_vertex(self, line :str, u :int, opts :str):  pass
    def on_edge(self, line :str, u :int, v :int, opts :str): pass
    def on_else(self, line :str): pass

def read_graphviz_vis(iterable, vis :GraphvizVisitor):
    """
    Process an iterable where each element is a line of a graphviz string.
    This function expect at most one vertex per line and one edge per line.
    Args:
        iterable: An iterable (e.g. my_file.readlines() or my_str.splitlines())
        vis: A GraphvizVisitor instance.
    """
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
# Graphviz read
#------------------------------------------------------------------

# NOTE: Assumptions:
# - vertices are identified using integer
# - vertices are described in the dot file before the edges
# - vertex/edge attributes are not too weird strings

class ReadGraphvizVisitor(GraphvizVisitor):
    def __init__(self, g :Graph):
        super().__init__()
        self.m_g = g
        self.m_aliases = dict()

    def on_install_vertex_property(self, u, g, key, value):
        pass

    def on_install_edge_property(self, e, g, key, value):
        pass

    def on_vertex(self, line :str, u_alias :int, opts :str) -> int:
        u = add_vertex(self.m_g)
        self.m_aliases[u_alias] = u
        if self.on_install_vertex_property:
            l = re.findall("\\w+=[^\\s]+",opts) # do not split on "," it fails if coma are in 'value'
            for opt in l:
                key, value = opt.split("=")
                key = key.strip().strip(",")
                value = value.strip().strip(",")
                value = value.strip("\"'").lstrip("<").rstrip(">")
                self.on_install_vertex_property(u, self.m_g, key, value)
        return u

    def on_edge(self, line :str, u_alias :int, v_alias :int, opts :str) -> EdgeDescriptor:
        u = self.m_aliases[u_alias]
        v = self.m_aliases[v_alias]
        (e, added) = add_edge(u, v, self.m_g)
        assert added

        if self.on_install_edge_property:
            l = re.findall("\\w+=[^\\s]+",opts) # CRAPPY split
            for opt in l:
                key, value = opt.split("=")
                key = key.strip().strip(",")
                value = value.strip().strip(",")
                self.on_install_edge_property(e, self.m_g, key, value)
        return e

def read_graphviz(iterable, g :Graph, vis = None):
    """
    Read an iterable where each element is a line of a graphviz string to
    extract a graph, but not its attributes. See read_graphviz_dp if needed.
    This function expect at most one vertex per line and one edge per line.
    Args:
        iterable: An iterable (e.g. my_file.readlines() or my_str.splitlines())
        g: Pass an empty DirectedGraph.
    """
    if not vis: vis = ReadGraphvizVisitor(g)
    read_graphviz_vis(iterable, vis)

#------------------------------------------------------------------
# Graphviz read with dynamic property (dp)
#------------------------------------------------------------------

class ReadGraphvizDpVisitor(ReadGraphvizVisitor):
    def __init__(self, g, dpv :dict, dpe :dict):
        super().__init__(g)
        self.m_dpv = dpv
        self.m_dpe = dpe

    def on_install_vertex_property(self, u, g, key, value):
        pmap = self.m_dpv[key] if self.m_dpv else None
        if pmap: pmap[u] = value

    def on_install_edge_property(self, e, g, key, value):
        pmap = self.m_dpe[key] if self.m_dpe else None
        if pmap: pmap[e] = value

def read_graphviz_dp(iterable, g :Graph, dpv = None, dpe = None):
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
    read_graphviz_vis(iterable, vis)

#------------------------------------------------------------------
# Graphviz call
#------------------------------------------------------------------

def error(*cls):
    print(*cls, file=sys.stderr)

def run_graphviz(s_dot, layout_engine = "dot", format = "svg") -> bytes:
    """
    Convert a dot string (graphviz format) into a graphic file.
    Args:
        s_dot: A string in the graphviz format.
        layout_engine: The graphviz engine used for the rendering.
            See "man dot" for more details.
        format: The output graphviz terminal.
            See "man dot" for more details.
    Returns:
        The bytes of the output image iff successful, None otherwise.
    """
    cmd = ['dot', '-T' + format, '-K', layout_engine]
    dot = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdoutdata, stderrdata = dot.communicate(s_dot.encode("utf-8"))
    status = dot.wait()
    if status == 0:
        return stdoutdata.decode("utf-8")
    else:
        fstr = "dot returned {}\n[==== stderr ====]\n{}"
        error(fstr.format(status, stderrdata.decode('utf-8')))
        error("Input dot string was:\n%s\n" % s_dot);
        raise RuntimeError("run_graphviz: invalid string")

def dot_to_svg(s_dot :str, layout_engine = "dot", format = "svg") -> str:
    bytes_img = run_graphviz(s_dot, layout_engine, format)
    if isinstance(bytes_img, bytes): # This should no more occur
        return bytes_img.decode("utf-8")
    elif isinstance(bytes_img, str):
        i = bytes_img.find("<svg")
        return bytes_img[i:]
    return None

# TODO Swap format / engine parameters
def write_graphviz(s_dot :str, filename, format = "svg", engine = "dot") -> bool:
    """
    Write a dot string (graphviz format) into a graphic file.
    Args:
        s_dot: A string in the graphviz format.
        filename: The path of the output file.
        format: The output graphviz terminal.
            See "man dot" for more details.
        engine: A graphviz engine (e.g. "dot", "fp", "neato", ...).
    Returns:
        True iff successfull.
    """
    def write_graphviz_impl(s_dot :str, f_img, format = "svg", engine = "dot") -> bool:
        ret = False
        bytes_img = run_graphviz(s_dot, engine, format)
        if bytes_img:
            print(bytes_img.decode("utf-8"), file = f_img)
            ret = True
        return ret

    if isinstance(filename, str):
        with open(filename, "w") as f_img:
            return write_graphviz_impl(s_dot, f_img, format, engine)
    else:
        return write_graphviz_impl(s_dot, f_img, format, engine)

def dotstr_to_html(s_dot :str, engine = "dot") -> str:
    """
    Convert a dot string to a html string.
    Args:
        s_dot: A dot string.
        engine: A graphviz engine (e.g. "dot", "fdp", "neato", ...).
    Returns:
        The corresponding HTML string.
    """
    return run_graphviz(s_dot, engine)

def graph_to_html(g, engine = "dot", **kwargs) -> str:
    """
    Convert a Graph to a HTML string.
    Args:
        g: The input Graph.
        engine: A graphviz engine (e.g. "dot", "fdp", "neato", ...).
    Returns:
        The corresponding HTML string.
    """
    s_dot = g.to_dot(**kwargs)
    return dotstr_to_html(s_dot, engine)
