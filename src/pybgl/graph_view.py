#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .graph import *
from .graph import __len_gen__
from .property_map import ReadPropertyMap, make_func_property_map


class GraphView:
    """
    The :py:class:`GraphView` allows to iterate on a subset of vertices
    and edges of a :py:class:`Graph` instance, according to arbitary
    property maps.

    You may combine multiple :py:class:`GraphView` instances using
    logical operators (e.g., ``&``, ``|``, ``-``).
    """
    def __init__(
        self,
        g: Graph,
        pmap_vrelevant: ReadPropertyMap = None,
        pmap_erelevant: ReadPropertyMap = None
    ):
        """
        Constructor.

        Args:
            g (Graph): A graph instance.
            pmap_vrelevant (ReadPropertyMap): A read property map
                which maps each vertex with a boolean indicating
                whether the considered vertex is relevant.
            pmap_erelevant (ReadPropertyMap): A read property map
                which maps each edge with a boolean indicating
                whether the considered vertex is relevant.
        """
        self.g = g
        self.pmap_vrelevant = (
            pmap_vrelevant if pmap_vrelevant else
            make_func_property_map(lambda u: True)
        )
        self.pmap_erelevant = (
            pmap_erelevant if pmap_erelevant else
            make_func_property_map(lambda e: True)
        )

    def __getattr__(self, method_name, *args, **kwargs):
        """
        Proxy for methods of ``self.g``.

        Args:
            method_name (str): The name of the proxified method.
        """
        return getattr(self.g, method_name, *args, **kwargs)

    def __or__(self, gv):
        """
        Returns the union of self and another :py:class:`GraphView` instance.

        Args:
            gv (GraphView): A :py:class:`GraphView` instance.

        Returns:
            The corresponding :py:class:`GraphView` instance.
        """
        return GraphView(
            self.g,
            make_func_property_map(
                lambda v: self.pmap_vrelevant[v] or gv.pmap_vrelevant[v]
            ),
            make_func_property_map(
                lambda e: self.pmap_erelevant[e] or gv.pmap_erelevant[e]
            )
        )

    def __and__(self, gv):
        """
        Returns the intersection of self and another
        :py:class:`GraphView` instance.

        Args:
            gv (GraphView): A :py:class:`GraphView` instance.

        Returns:
            The corresponding :py:class:`GraphView` instance.
        """
        return GraphView(
            self.g,
            make_func_property_map(
                lambda v: self.pmap_vrelevant[v] and gv.pmap_vrelevant[v]
            ),
            make_func_property_map(
                lambda e: self.pmap_erelevant[e] and gv.pmap_erelevant[e]
            )
        )

    def __sub__(self, gv):
        """
        Returns the substraction of self and
        another :py:class:`GraphView` instance.

        Args:
            gv (GraphView): A :py:class:`GraphView` instance.

        Returns:
            The corresponding :py:class:`GraphView` instance.
        """
        return GraphView(
            self.g,
            make_func_property_map(
                lambda v: self.pmap_vrelevant[v] and not gv.pmap_vrelevant[v]
            ),
            make_func_property_map(
                lambda e: (
                    self.pmap_erelevant[e] and
                    not gv.pmap_erelevant[e] or (
                        not gv.pmap_vrelevant[self.source(e)] and
                        not gv.pmap_vrelevant[self.target(e)]
                    )
                )
            )
        )

    def vertices(self) -> iter:
        """
        Gets an iterator over the relevant vertices of the nested
        :py:class:`Graph` instance.

        Returns:
            An iterator over the relevant vertices.
        """
        return (
            u for u in self.g.vertices()
            if self.pmap_vrelevant[u]
        )

    def edges(self) -> iter:
        """
        Gets an iterator over the relevant edges of the nested
        :py:class:`Graph` instance.

        Returns:
            An iterator over the relevant edges.
        """
        return (
            e for e in self.g.edges()
            if self.pmap_erelevant[e]
            and self.pmap_vrelevant[self.source(e)]
            and self.pmap_vrelevant[self.target(e)]
        )

    def out_edges(self, u: int) -> iter:
        """
        Gets an iterator over the relevant out-edges of a given
        vertex of the nested :py:class:`Graph` instance.

        Args:
            u (int): The considered vertex.

        Returns:
            An iterator over the relevant out-edges.
        """
        return (
            e for e in self.g.out_edges(u)
            if self.pmap_erelevant[e]
            and self.pmap_vrelevant[self.source(e)]
            and self.pmap_vrelevant[self.target(e)]
        )

    def out_degree(self, u: int) -> int:
        """
        Gets the out-degree (the number of out-edges) of a vertex ``u``
        involved in this :py:class:`GraphView` instance.

        Args:
            u (int): The considered vertex.

        Returns:
            The out-degree of ``u``
        """
        return __len_gen__(self.out_edges(u))

    def in_edges(self, u: int) -> iter:
        """
        Gets an iterator over the relevant in-edges of a given
        vertex of the nested :py:class:`IncidenceGraph` instance.

        Raises:
            RuntimeError: Raised if ``self.g`` does not expose an
                ``in_edges`` method.

        Args:
            u (int): The considered vertex.

        Returns:
            An iterator over the relevant in-edges.
        """
        return (
            e for e in self.g.in_edges(u)
            if self.pmap_erelevant[e]
            and self.pmap_vrelevant[self.source(e)]
            and self.pmap_vrelevant[self.target(e)]
        )

    def in_degree(self, u: int) -> int:
        """
        Gets the in-degree (the number of out-edges) of a vertex ``u``
        involved in this :py:class:`GraphView` instance.

        Raises:
            RuntimeError: Raised if ``self.g`` does not expose an
                ``in_edges`` method.

        Args:
            u (int): The considered vertex.

        Returns:
            The out-degree of ``u``
        """
        return __len_gen__(self.in_edges(u))

    def num_vertices(self) -> int:
        """
        Counts the number of relevant vertices involved in this
        :py:class:`GraphView` instance.

        Returns:
            The number of vertices.
        """
        return __len_gen__(self.vertices())

    def num_edges(self) -> int:
        """
        Counts the number of relevant edges involved in this
        :py:class:`GraphView` instance.

        Returns:
            The number of edges.
        """
        return __len_gen__(self.edges())

    def to_dot(self, *cls, **kwargs) -> str:
        """
        Exports this :py:class:`GraphView` instance to a Graphviz string.
        See the :py:func:`to_dot` function.

        Returns:
            The corresponding graphviz string.
        """
        return self.g.to_dot(
            vs=[u for u in self.vertices()],
            es=[e for e in self.edges()],
            source=lambda e, g: self.source(e),
            target=lambda e, g: self.target(e),
            *cls, **kwargs
        )
