#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .graphviz_impl import *


def __len_gen__(gen: iter) -> int:
    """
    Retrieves the length of an iterable (e.g., a generator).

    _Remark:_ ``__len_gen__(gen)`` is faster and consumes less
    memory than ``len([for x in gen])``.

    Example:
        >>> g = (i for i in (2, 5, 8))
        >>> __len_gen__(g)
        3

    Args:
        gen (iter): An iterable

    Returns:
        The length of the input iterable.
    """
    n = 0
    for x in gen:
        n += 1
    return n


# -------------------------------------------------------------------
# EdgeDescriptor
# -------------------------------------------------------------------

class EdgeDescriptor:
    def __init__(self, u: int, v: int, distinguisher: int):
        """
        Constructor.

        Never call explicitely this constructor. You are
        supposed a method like :py:meth:`Graph.edges`,
        :py:meth:`Graph.out_edges`, etc.

        Args:
            u (int): The source vertex.
            v (int): The target vertex.
            n (int): The distinguisher (if several edge may exist from
                ``u`` to ``v``).
        """
        self.source = u
        self.target = v
        self.distinguisher = distinguisher

    def __str__(self) -> str:
        """
        Converts this :py:class:`EdgeDescriptor` instance to its
        string representation when using :py:func:`str`.

        Returns:
            The corresponding string representation.
        """
        return "(%s -> %s)" % (self.source, self.target)

    def __repr__(self) -> str:
        """
        Converts this :py:class:`EdgeDescriptor` instance to its
        string representation when using :py:func:`repr`.

        Returns:
            The corresponding string representation.
        """
        return str(self)

    def __hash__(self) -> int:
        """
        Computes the hash of this :py:class:`EdgeDescriptor` instance.

        Returns:
            The corresponding hash.
        """
        return hash((self.source, self.target, self.distinguisher))

    def __eq__(self, e) -> bool:
        """
        Checks whether this :py:class:`EdgeDescriptor` instance equals
        another one.

        Args:
            e (EdgeDescriptor): The other :py:class:`EdgeDescriptor` instance.

        Returns:
            ``True`` if ``self`` and ``e`` are equal,
            ``False`` otherwise
        """
        return (
            e is not None
            and self.source == e.source
            and self.target == e.target
            and self.distinguisher == e.distinguisher
        )

    def __lt__(self, e) -> bool:
        """
        Checks whether this :py:class:`EdgeDescriptor` instance strictly
        preceeds another one.

        Args:
            e (EdgeDescriptor): The other :py:class:`EdgeDescriptor` instance.

        Returns:
            ``True`` if ``self`` strictly preceeds ``e``,
            ``False`` otherwise
        """
        return (
            (
                self.source,
                self.target,
                self.distinguisher
            ) < (
                e.source,
                e.target,
                e.distinguisher
            )
        )


# -------------------------------------------------------------------
# Generic graph
# -------------------------------------------------------------------

class Graph:
    """
    :py:class:`Graph` implements base class used to implement
    the :py:class:`DirectedGraph` and the :py:class:`UndirectedGraph` classes.
    """
    def __init__(self, directed: bool = None, num_vertices: int = 0):
        """
        Constructor.

        Args:
            directed (bool): Pass ``True`` if the graph is directed,
                ``False`` otherwise.
            num_vertices (int): Pass the (initial) number of vertices.
        """
        assert isinstance(directed, bool)
        self.directed = directed
        self.last_vertex_id = 0
        self.adjacencies = dict()
        for u in range(num_vertices):
            self.add_vertex()

    def add_vertex(self) -> int:
        """
        Adds a vertex to this :py:class:`Graph` instance.

        Returns:
            The vertex descriptor of the added vertex.
        """
        u = self.last_vertex_id
        self.adjacencies[u] = dict()
        self.last_vertex_id += 1
        return u

    def num_vertices(self) -> int:
        """
        Counts the number of vertices involved in this
        :py:class:`Graph` instance.

        Returns:
            The number of vertices.
        """
        return __len_gen__(self.vertices())

    def remove_vertex(self, u: int):
        """
        Removes a vertex from this :py:class:`Graph` instance.

        Args:
            u (int): The vertex descriptor of the vertex to be removed.

        Raises:
            `KeyError` if ``u`` does not exist.
        """
        # Remove in-edges
        for e in [e for e in self.edges()]:
            if u == self.target(e):
                self.remove_edge(e)

        # Remove out-edges
        for e in [e for e in self.out_edges(u)]:
            self.remove_edge(e)

        # Remove u
        del self.adjacencies[u]

    def vertices(self) -> iter:
        """
        Gets an iterator over the vertices involved in this
        :py:class:`Graph` instance.

        Returns:
            An iterator over the vertices.
        """
        return self.adjacencies.keys()

    def add_edge(self, u: int, v: int) -> tuple:
        """
        Adds an edge to this :py:class:`Graph` instance.

        Args:
            u (int): The vertex descriptor of source vertex of the new edge.
            v (int): The vertex descriptor of target vertex of the new edge.

        Returns:
            A tuple ``(e, success)`` where ``e`` is an
            :py:class:`EdgeDescriptor` compliant with this
            :py:class:`Graph` class and ``success == True``
            if successful, ``(None, False)`` otherwise.
        """
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

    def remove_edge(self, e: EdgeDescriptor):
        """
        Removes an edge from this :py:class:`Graph` instance.

        Args:
            e (EdgeDescriptor): The edge descriptor of the edge to be removed.
        """
        u = e.source
        v = e.target
        n = e.distinguisher
        adjs_u = self.adjacencies[u]
        s = adjs_u[v]
        if n in s:
            s.remove(n)
            if s == set():
                del adjs_u[v]
                # We keep the empty dictionary to allow to create
                # out-arcs for u.
                # if not bool(adjs_u):
                #    del self.adjacencies[u]

    def num_edges(self) -> int:
        """
        Counts the number of edges involved in this :py:class:`Graph` instance.

        Returns:
            The number of edges.
        """
        return __len_gen__(self.edges())

    def out_edges(self, u: int) -> iter:
        """
        Gets an iterator over the out-edges of a vertex ``u``
        involved in this :py:class:`Graph` instance.

        Args:
            u (int): The source vertex.

        Returns:
            An iterator over the out-edges of ``u``.
        """
        return (
            EdgeDescriptor(u, v, n)
            for (v, s) in self.adjacencies.get(u, dict()).items()
            for n in s
        )

    def out_degree(self, u: int) -> int:
        """
        Gets the out-degree (the number of out-edges) of a vertex ``u``
        involved in this :py:class:`Graph` instance.

        Args:
            u (int): The considered vertex.

        Returns:
            The out-degree of ``u``
        """
        return __len_gen__(self.out_edges(u))

    def in_edges(self, u: int) -> iter:
        """
        Gets an iterator over the in-edges of a vertex ``v``
        involved in this :py:class:`Graph` instance.

        Args:
            v (int): The target vertex.

        Returns:
            An iterator over the out-edges of ``v``.
        """
        # As the mapping is only in the forward direction, the
        # in_edges primitive is not implemented on purpose.
        # It requires an additional mapping map each vertex
        # with its in-edges or to implemented an inefficient
        # iterator, e.g:
        #
        #   (e for e in self.edges() if self.target(e) == u)
        return NotImplementedError(
            "in_edges must be implemented in the child class"
        )

    def in_degree(self, u: int) -> int:
        """
        Gets the in-degree (the number of in-edges) of a vertex ``u``
        involved in this :py:class:`Graph` instance.

        Args:
            u (int): The considered vertex.

        Returns:
            The in-degree of ``u``
        """
        return __len_gen__(self.in_edges(u))

    def edges(self) -> iter:
        """
        Gets an iterator over the edges involved in this
        :py:class:`Graph` instance.

        Returns:
            An iterator over the edges.
        """
        return (
            EdgeDescriptor(u, v, n)
            for (u, vs) in self.adjacencies.items()
            for (v, s) in vs.items()
            for n in s
        )

    def edge(self, u: int, v: int) -> tuple:
        """
        Retrieves the edge from a vertex ``u`` to vertex ``v``, if any.

        Args:
            u (int): The source of the edge.
            v (int): The target of the edge.

        Returns:
            ``(e, True)`` if it exists a single edge from ``u`` to ``v``,
            ``(None, False)`` otherwise.
        """
        ret = (None, False)
        candidates_edges = {
            e
            for e in self.out_edges(u)
            if self.target(e) == v
        }
        if len(candidates_edges) == 1:
            ret = (candidates_edges.pop(), True)
        return ret

    def to_dot(self, **kwargs) -> str:
        """
        Exports this :py:class:`Graph` instance to a Graphviz string.
        See the :py:func:`to_dot` function.

        Returns:
            The corresponding graphviz string.
        """
        return to_dot(self, **kwargs)

    def has_vertex(self) -> bool:
        """
        Checks if this :py:class:`Graph` contains at least one vertex.

        Returns:
            ``True`` if the graph has at least one vertex,
            ``False`` otherwise.
        """
        for _ in self.vertices():
            return True
        return False

    def has_edge(self) -> bool:
        """
        Checks if this :py:class:`Graph` instance contains at least one edge.

        Returns:
            ``True`` if the graph has at least one edge,
            ``False`` otherwise.
        """
        for _ in self.edges():
            return True
        return False

    def source(self, e: EdgeDescriptor) -> int:
        """
        Retrieves the source vertex of an arc in this
        :py:class:`Graph` instance.

        Args:
            e (EdgeDescriptor): The considered arc.

        Returns:
            The vertex descriptor of the source of ``e``.
        """
        return e.source

    def target(self, e: EdgeDescriptor) -> int:
        """
        Retrieves the target vertex of an arc in this
        :py:class:`Graph` instance.

        Args:
            e (EdgeDescriptor): The considered arc.

        Returns:
            The vertex descriptor of the target of ``e``.
        """
        return e.target


def source(e: EdgeDescriptor, g: Graph) -> int:
    """
    Retrieves the source vertex of an arc in a graph.

    Args:
        e (EdgeDescriptor): The considered arc.
        g (Graph): The considered graph.

    Returns:
        The vertex descriptor of the source of ``e`` in ``g``.
    """
    return g.source(e)


def target(e: EdgeDescriptor, g: Graph) -> int:
    """
    Retrieves the target vertex of an arc in this :py:class:`Graph` instance.

    Args:
        e (EdgeDescriptor): The considered arc.
        g (Graph): The considered graph.

    Returns:
        The vertex descriptor of the target of ``e``.
    """
    return g.target(e)


def is_directed(g) -> bool:
    """
    Tests whether a graph is directed or not.

    Args:
        g (Graph): The considered graph.

    Returns:
        ``True`` if ``g`` is directed,
        ``False`` otherwise.
    """
    return g.directed


# -------------------------------------------------------------------
# Directed graph
# -------------------------------------------------------------------

class DirectedGraph(Graph):
    """
    The :py:class:`DirectedGraph` models a directed graph.
    See also the :py:class:`UndirectedGraph` class.
    """
    def __init__(self, num_vertices: int = 0):
        """
        Constructor.

        Args:
            num_vertices (int): Pass the (initial) number of vertices.
        """
        super().__init__(True, num_vertices)


# -------------------------------------------------------------------
# Undirected graph
# -------------------------------------------------------------------

class UndirectedGraph(Graph):
    """
    The :py:class:`UndirectedGraph` models a undirected graph.
    As it is undirected the reverse edge are automatically added/inserted.

    See also the :py:class:`DirectedGraph` class.
    """

    def __init__(self, num_vertices: int = 0):
        """
        Constructor.

        Args:
            num_vertices (int): Pass the (initial) number of vertices.
        """
        super().__init__(False, num_vertices)

    def add_edge(self, u: int, v: int) -> tuple:
        """
        Adds an edge to this :py:class:`Graph` instance.

        Args:
            u (int): The vertex descriptor of source of the new edge.
            v (int): The vertex descriptor of source of the new edge.

        Returns:
            A tuple ``(e, success)`` where ``e`` is an
            :py:class:`EdgeDescriptor`
            compliant with this :py:class:`Graph` class and ``success == True``
            if successful, ``(None, False)`` otherwise.
        """
        (u, v) = (min(u, v), max(u, v))
        (e, added) = super().add_edge(u, v)
        if added:
            n = e.distinguisher
            if u not in self.adjacencies[v].keys():
                self.adjacencies[v][u] = set()
            self.adjacencies[v][u].add(n)
        return (e, added)

    def out_edges(self, u: int) -> iter:
        """
        Gets an iterator over the out-edges of a given vertex
        involved in this :py:class:`Graph` instance.

        Args:
            u (int): The source vertex.

        Returns:
            An iterator over the out-edges of ``u``.
        """
        # source(e, g) and target(e, g) impose to returns (u, v)-like
        # EdgeDescriptors.
        return (
            EdgeDescriptor(u, v, n)
            for v, s in self.adjacencies.get(u, dict()).items()
            for n in s
        )

    def remove_edge(self, e: EdgeDescriptor):
        """
        Removes an edge from this :py:class:`Graph` instance.

        Args:
            e (EdgeDescriptor): The edge descriptor of the edge to be removed.
        """
        super().remove_edge(e)
        u = self.source(e)
        v = self.target(e)
        if u != v:
            # Remove the reverse adjacency
            n = e.distinguisher
            self.adjacencies[v][u].remove(n)

    def in_edges(self, u: int) -> iter:
        """
        Gets an iterator over the in-edges of a vertex ``u``
        involved in this :py:class:`Graph` instance.

        Args:
            u (int): The target vertex.

        Returns:
            An iterator over the in-edges of ``u``.
        """
        return self.out_edges(u)

    def edges(self) -> iter:
        """
        Gets an iterator over the edges involved in this
        :py:class:`Graph` instance.

        Returns:
            An iterator over the edges.
        """
        return (
            EdgeDescriptor(u, v, n)
            for (u, vs) in self.adjacencies.items()
            for (v, s) in vs.items()
            for n in s if u <= v
        )


# -------------------------------------------------------------------
# Common methods
# -------------------------------------------------------------------

def vertices(g: Graph) -> iter:
    """
    Gets an iterator over the vertices involved of a graph ``g``.

    Args:
        g (Graph): The considered graph.

    Returns:
        An iterator over the vertices of ``g``.
    """
    return g.vertices()


def num_vertices(g: Graph) -> int:
    """
    Counts the number of vertices involved of a graph ``g``.

    Args:
        g (Graph): The considered graph.

    Returns:
        The number of vertices in ``g``.
    """
    return g.num_vertices()


def has_vertex(g: Graph) -> bool:
    """
    Checks if a graph ``g`` instance contains at least one vertex.

    Args:
        g (Graph): The considered graph.

    Returns:
        ``True`` if the graph has at least one edge,
        ``False`` otherwise.
    """
    return g.has_vertex()


def add_vertex(g: Graph) -> int:
    """
    Adds a vertex to a graph ``g``

    Args:
        g (Graph): The considered graph.

    Returns:
        The vertex descriptor of the added vertex.
    """
    return g.add_vertex()


def remove_vertex(u: int, g: Graph):
    """
    Removes a vertex from a graph ``g``.

    Args:
        u (int): The vertex descriptor of the vertex to be removed.
        g (Graph): The considered graph.

    Raises:
        `KeyError` if ``u`` does not exist in ``g``.
    """
    g.remove_vertex(u)


def edges(g: Graph):
    """
    Gets an iterator over the edges involved of a graph ``g``.

    Args:
        g (Graph): The considered graph.

    Returns:
        An iterator over the vertices of ``g``.
    """
    return g.edges()


def num_edges(g: Graph) -> int:
    """
    Counts the number of edges involved of a graph ``g``.

    Args:
        g (Graph): The considered graph.

    Returns:
        The number of edges in ``g``.
    """
    return g.num_edges()


def has_edge(g: Graph) -> bool:
    """
    Checks if a graph ``g`` instance contains at least one edge.

    Returns:
        ``True`` if the graph has at least one edge,
        ``False`` otherwise.
    """
    return g.has_edge()


def add_edge(u: int, v: int, g: Graph) -> EdgeDescriptor:
    """
    Adds an edge to a graph ``g``.

    Args:
        u (int): The vertex descriptor of source vertex of the new edge.
        v (int): The vertex descriptor of target vertex of the new edge.
        g (Graph): The considered graph.

    Returns:
        A tuple ``(e, success)`` where ``e`` is an :py:class:`EdgeDescriptor`
        compliant with this :py:class:`Graph` class and ``success == True``
        if successful, ``(None, False)`` otherwise.
    """

    return g.add_edge(u, v)


def remove_edge(e: EdgeDescriptor, g: Graph):
    """
    Removes an edge from  a graph ``g``.

    Args:
        e (EdgeDescriptor): The edge descriptor of the edge to be removed.
        g (Graph): The considered graph.
    """
    g.remove_edge(e)


def in_edges(u: int, g: Graph) -> iter:
    """
    Gets an iterator over the in-edges of a vertex ``u``
    involved a graph ``g``.

    Args:
        u (int): The target vertex.
        g (Graph): The considered graph.

    Returns:
        An iterator over the edges.
    """
    return g.in_edges(u)


def in_degree(u: int, g: Graph) -> int:
    """
    Gets the out-degree (the number of in-edges) of a vertex ``u``
    involved a graph ``g``.

    Args:
        u (int): The considered vertex.
        g (Graph): The considered graph.

    Returns:
        The in-degree of ``u``
    """
    return g.in_degree(u)


def out_edges(u: int, g: Graph) -> iter:
    """
    Gets an iterator over the out-edges of a vertex ``u``
    involved a graph ``g``.

    Args:
        u (int): The source vertex.
        g (Graph): The considered graph.

    Returns:
        An iterator over the out-edges of ``u``.
    """
    return g.out_edges(u)


def out_degree(u: int, g: Graph) -> int:
    """
    Gets the out-degree (the number of out-edges) of a vertex ``u``
    involved a graph ``g``.

    Args:
        u (int): The considered vertex.
        g (Graph): The considered graph.

    Returns:
        The out-degree of ``u``
    """
    return __len_gen__(g.out_edges(u))


def edge(u: int, v: int, g: Graph) -> tuple:
    """
    Retrieves the edge from ``u`` to ``v``.

    Args:
        u: The source of the edge.
        v: The target of the edge.
        g (Graph): The considered graph.

    Returns:
        ``(e, True)`` if it exists a single edge from ``u`` to ``v``,
        ``(None, False)`` otherwise.
    """
    return g.edge(u, v)
