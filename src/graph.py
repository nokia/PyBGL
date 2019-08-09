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

def __len_gen__(gen) -> int:
    """
    Get the "length" of a generator.
    """
    # __len_gen__(gen) is faster and consumes less memory than len([for x in gen])
    n = 0
    for x in gen: n += 1
    return n

#-------------------------------------------------------------------
# EdgeDescriptor
#-------------------------------------------------------------------

class EdgeDescriptor:
    def __init__(self, u :int, v :int, distinguisher :int):
        """
        Constructor.
        Never call explicitely this constructor. You're supposed
        to get EdgeDescriptor via *edge() and edges() methods.
        """
        self.m_source = u
        self.m_target = v
        self.m_distinguisher = distinguisher

    def __str__(self) -> str:
        return "(%s -> %s)" % (self.m_source, self.m_target)

    def __repr__(self) -> str:
        return "(%s -> %s)" % (self.m_source, self.m_target)

    def __hash__(self):
        return hash((self.m_source, self.m_target, self.m_distinguisher))

    def __eq__(self, e):
        return e != None \
            and self.m_source == e.m_source \
            and self.m_target == e.m_target \
            and self.m_distinguisher == e.m_distinguisher

    def __lt__(self, e) -> bool:
        return (self.m_source, self.m_target, self.m_distinguisher) \
             < (e.m_source,    e.m_target,    e.m_distinguisher)

#-------------------------------------------------------------------
# Generic graph
#-------------------------------------------------------------------

def default_graphviz_style() -> str:
    FG_COLOR = "black"
    BG_COLOR = "transparent"
    return "graph[bgcolor = %(BG_COLOR)s fontcolor = %(FG_COLOR)s rankdir = LR]; " \
            "node[color = %(FG_COLOR)s fontcolor = %(FG_COLOR)s]; " \
            "edge[color = %(FG_COLOR)s fontcolor = %(FG_COLOR)s]; " % locals()

def is_directed(g) -> bool:
    return g.directed

def graphviz_type(g) -> str:
    return "digraph" if is_directed(g) else "graph"

def graphviz_arc(g) -> str:
    return "->" if is_directed(g) else "--"

class Graph:
    def __init__(self, directed = None, num_vertices = 0):
        assert isinstance(directed, bool)
        self.m_directed = directed
        self.m_id = 0 # Last used vertex descriptor
        self.m_adjacencies = dict()
        for u in range(num_vertices):
            self.add_vertex()

    @property
    def directed(self):
        return self.m_directed

    def add_vertex(self) -> int:
        u = self.m_id
        self.m_adjacencies[u] = dict()
        self.m_id += 1
        return u

    def num_vertices(self):
        return __len_gen__(self.vertices())

    def remove_vertex(self, u :int):
        del self.adjacencies[u]

    def vertices(self):
        return self.adjacencies.keys()

    @property
    def adjacencies(self) -> dict:
        return self.m_adjacencies

    def add_edge(self, u :int, v :int) -> tuple: # (EdgeDescriptor, bool)
        u_adjs = self.adjacencies[u]
        is_new = v not in u_adjs
        if is_new:
            n = 0
            u_adjs[v] = {n}
        else:
            s = u_adjs[v]
            n = 0 if len(s) == 0 else max(s) + 1
            s.add(n)
        return (EdgeDescriptor(u, v, n), True)

    def remove_edge(self, e :EdgeDescriptor):
        u = e.m_source
        v = e.m_target
        n = e.m_distinguisher
        adjs_u = self.adjacencies[u]
        s = adjs_u[v]
        if n in s:
            s.remove(n)
            if s == set():
                del adjs_u[v]
                # We keep the empty dictionary to allow to create out-arcs for u.
                #if not bool(adjs_u):
                #    del self.adjacencies[u]

    def num_edges(self):
        return __len_gen__(self.edges())

    def out_edges(self, u :int):
        return (EdgeDescriptor(u, v, n) for v, s in self.adjacencies.get(u, dict()).items() for n in s)

    def edges(self):
        return (EdgeDescriptor(u, v, n) for u, vs in self.adjacencies.items() for v, s in vs.items() for n in s)

    def edge(self, u :int, v :int) -> tuple:
        """
        Retrieve the edge from a vertex u to vertex v.
        Args:
            u: The source of the edge.
            v: The target of the edge.
        Returns:
            (e, True) if it exists a single edge from u to v,
            (None, False) otherwise.
        """
        ret = (None, False)
        candidates_edges = {e for e in out_edges(u, self) if target(e, self) == v}
        if len(candidates_edges) == 1:
            ret = (candidates_edges.pop(), True)
        return ret


    def to_dot(self, graphviz_style = None) -> str:
        if graphviz_style == None:
            graphviz_style = default_graphviz_style()
        return "%(type)s G {%(style)s %(arcs)s}" % {
            "style"    : graphviz_style,
            "type"     : graphviz_type(self),
            "vertices" : "; ".join(["%s" % u for u in self.vertices()]),
            "arcs"     : "; ".join([
                            "%s %s %s" % (
                                source(e, self),
                                graphviz_arc(self),
                                target(e, self)
                            ) for e in self.edges()
                        ])
        }

    def source(self, e :EdgeDescriptor):
        return e.m_source

    def target(self, e :EdgeDescriptor):
        return e.m_target

def source(e :EdgeDescriptor, g :Graph):
    return g.source(e)

def target(e :EdgeDescriptor, g :Graph):
    return g.target(e)

#-------------------------------------------------------------------
# Directed graph
#-------------------------------------------------------------------

class DirectedGraph(Graph):
    def __init__(self, num_vertices = 0):
        super().__init__(True, num_vertices)

#-------------------------------------------------------------------
# Undirected graph
#-------------------------------------------------------------------

class UndirectedGraph(Graph):
    # The reverse are automatically added/inserted.

    def __init__(self, num_vertices = 0):
        super().__init__(False, num_vertices)

    def add_edge(self, u :int, v :int) -> tuple:
        (u, v) = (min(u, v), max(u, v))
        (e, added) = super().add_edge(u, v)
        if added:
            n = e.m_distinguisher
            if u not in self.m_adjacencies[v].keys():
                self.m_adjacencies[v][u] = set()
            self.m_adjacencies[v][u].add(n)
        return (e, added)

    def out_edges(self, u :int):
        # source(e, g) and target(e, g) impose to returns (u, v)-like
        # EdgeDescriptors.
        return (
            EdgeDescriptor(u, v, n) \
            for v, s in self.adjacencies.get(u, dict()).items() \
            for n in s
        )

    def remove_edge(self, e :EdgeDescriptor):
        super().remove_edge(e)
        # Remove the reverse adjacency
        u = source(e, self)
        v = target(e, self)
        v = max(u, v)
        n = e.m_distinguisher
        self.m_adjacencies[v][u].remove(n)

    def in_edges(self, u :int):
        return self.out_edges(u)

    def edges(self):
        return (EdgeDescriptor(u, v, n) for u, vs in self.adjacencies.items() for v, s in vs.items() for n in s if u <= v)

    def remove_vertex(self, u):
        # Clear reverse adjacencies
        for e in self.out_edges(u):
            v = target(e, self)
            n = e.m_distinguisher
            self.m_adjacencies[v][u].remove(n)
        super().remove_vertex(u)

#-------------------------------------------------------------------
# Common methods
#-------------------------------------------------------------------

def vertices(g :Graph):
    return g.vertices()

def num_vertices(g :Graph) -> int:
    return g.num_vertices()

def add_vertex(g :Graph) -> int:
    return g.add_vertex()

def remove_vertex(u :int, g :Graph):
    g.remove_vertex(u)

def edges(g :Graph):
    return g.edges()

def num_edges(g :Graph) -> int:
    return g.num_edges()

def add_edge(u :int, v :int, g :Graph) -> EdgeDescriptor:
    return g.add_edge(u, v)

def remove_edge(e :EdgeDescriptor, g :Graph):
    g.remove_edge(e)

def in_edges(u :int, g :Graph):
    return g.in_edges(u)

def in_degree(u :int, g :Graph):
    return __len_gen__(in_edges(u, g))

def out_edges(u :int, g :Graph):
    return g.out_edges(u)

def out_degree(u :int, g :Graph) -> int:
    return __len_gen__(out_edges(u, g))

def edge(u :int, v :int, g :Graph) -> tuple:
    """
    Retrieve the edge from a vertex u to vertex v.
    Args:
        u: The source of the edge.
        v: The target of the edge.
        g: The Graph.
    Returns:
        (e, True) if it exists a single edge from u to v,
        (None, False) otherwise.
    """
    return g.edge(u, v)
