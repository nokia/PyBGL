#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .graph import *

class IncidenceGraph(DirectedGraph):
    """
    The :py:class:`IncidenceGraph` extends the :py:class:`DirectedGraph`
    so that the :py:meth:`IncidenceGraph.in_edges` and the
    :py:meth:`IncidenceGraph.in_degree` are well-defined.
    This is done by mapping each state with its input transitions.
    """
    def __init__(self, num_vertices: int = 0):
        """
        Constructor.

        Args:
            See :py:meth:`Graph.__init__`.
        """
        self.m_in_adjacencies = dict()
        super().__init__(num_vertices)

    @property
    def in_adjacencies(self) -> dict:
        """
        Accessor to the input transitions of each state.

        Returns:
            The storage memorizing the input transitions.
        """
        return self.m_in_adjacencies

    def add_vertex(self) -> int:
        """
        Adds a vertex to this :py:class:`IncidenceGraph` instance.
        Overloads the :py:meth:`DirectedGraph.add_vertex` method.

        Returns:
            The vertex descriptor of the added vertex.
        """
        u = super().add_vertex()
        self.in_adjacencies[u] = dict()
        return u

    def add_edge(self, u: int, v: int) -> tuple:
        """
        Adds an edge to this :py:class:`IncidenceGraph` instance.
        Overloads the :py:meth:`DirectedGraph.add_edge` method.

        Args:
            u (int): The vertex descriptor of source vertex of the new edge.
            v (int): The vertex descriptor of target vertex of the new edge.

        Returns:
            A tuple ``(e, success)`` where ``e`` is an :py:class:`EdgeDescriptor`
            compliant with this :py:class:`IncidenceGraph` class and ``success == True``
            if successful, ``(None, False)`` otherwise.
        """
        (e, added) = super().add_edge(u, v)
        if added:
            v_in_adjs = self.in_adjacencies[v]
            is_new = u not in v_in_adjs
            n = e.m_distinguisher
            if is_new:
                v_in_adjs[u] = {n}
            else:
                v_in_adjs[u].add(n)
        return (e, added)

    def remove_vertex(self, u: int):
        """
        Removes a vertex from this :py:class:`IncidenceGraph` instance.
        Overloads the :py:class:`DirectedGraph.remove_vertex` method.

        Args:
            u (int): The vertex descriptor of the vertex to be removed.

        Raises:
            `KeyError` if ``u`` does not exist.
        """
        for e in [e for e in self.in_edges(u)]:
            remove_edge(e, self)
        for e in [e for e in self.out_edges(u)]:
            remove_edge(e, self)
        del self.adjacencies[u]
        del self.in_adjacencies[u]

    def remove_edge(self, e: EdgeDescriptor):
        """
        Removes an edge from this :py:class:`IncidenceGraph` instance.
        Overloads the :py:class:`Graph.remove_edge` method.

        Args:
            e (EdgeDescriptor): The edge descriptor of the edge to be removed.
        """
        super().remove_edge(e)
        u = e.m_source
        v = e.m_target
        n = e.m_distinguisher
        in_adjs_v = self.in_adjacencies[v]
        s = in_adjs_v[u]
        if n in s:
            s.remove(n)
            if s == set():
                del in_adjs_v[u]
                # We keep the empty dictionary to allow to create out-arcs for u.

    def in_edges(self, v: int):
        """
        Gets an iterator over the in-edges of a vertex ``v``
        involved in this :py:class:`IncidenceAutomaton` instance.
        Overwrites the :py:class:`Graph.in_edges` method.

        Args:
            v (int): The target vertex.

        Returns:
            An iterator over the in-edges of ``v``.
        """
        return (
            EdgeDescriptor(u, v, n)
            for (u, s) in self.in_adjacencies.get(v, dict()).items()
            for n in s
        )
