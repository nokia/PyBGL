#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .automaton import *
from .property_map import (
    ReadWritePropertyMap, make_assoc_property_map, make_func_property_map
)

class NodeAutomaton(Automaton):
    """
    The :py:class:`NodeAutomaton` implements a
    `Deterministic Finite Automaton <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`__.
    whose symbols are installed on the states instead of the transitions.
    This is a particular case of DFA, whose transitions targetting a same given
    target are all labeled by the same symbol.
    """
    def __init__(
        self,
        num_vertices: int = 0,
        q0: int = 0,
        pmap_vfinal = None,
        pmap_vsymbol: ReadWritePropertyMap = None
    ):
        """
        Constructor.

        Args:
            num_vertices (int): The number of states.
            q0 (int): The vertex descriptor of the initial state.
            pmap_vfinal (ReadPropertyMap): A property map which maps
                each state with a boolean indicating whether its
                a final state or not.
            pmap_vsymbol (ReadPropertyMap): A property map which maps
                each state with its corresponding symbol.
        """
        # Convention: self.adjacencies[q][a] = r
        super().__init__(num_vertices, q0, pmap_vfinal)
        if pmap_vsymbol is None:
            map_vsymbol = defaultdict(lambda: None)
            pmap_vsymbol = make_assoc_property_map(map_vsymbol)
        self.pmap_vsymbol = pmap_vsymbol

    def add_vertex(self, a: str = None) -> int:
        u = super().add_vertex()
        if a is not None:
            self.pmap_vsymbol[u] = a
        return u

    def delta(self, q: int, a: str) -> int:
        """
        Transition function, allowing to move from a state ``q`` to its
        ``a``-successor, if any.

        Args:
            q (int): The vertex descriptor of a state of this
                :py:class:`NodeAutomaton` instance.
            a (str): The symbol.

        Returns:
            The reached state (if any), :py:data:`BOTTOM` otherwise.
        """
        return self.adjacencies[q].get(a, BOTTOM)

    def add_edge(self, q: int, r: int) -> tuple:
        """
        Adds a transition to this :py:class:`NodeAutomaton` instance.

        Args:
            q (int): The vertex descriptor of source state of the new transition.
            r (int): The vertex descriptor of target state of the new transition.
            a (str): The label of the new transition.

        Returns:
            A tuple ``(e, success)`` where ``e`` is an :py:class:`EdgeDescriptor`
            compliant with this :py:class:`Automaton` class and ``success == True``
            if successful, ``(None, False)`` otherwise.
        """
        assert q is not None
        assert r is not None
        a = symbol(r, self)
        adj_q = self.adjacencies[q]
        if a in adj_q.keys():
            return (None, False)
        self.adjacencies[q][a] = r
        return (EdgeDescriptor(q, r, a), True)

    def edge(self, q: int, r: int) -> tuple:
        """
        Retrieves the edge from a state ``q`` to state ``r`` such
        that ``r`` is a ``a``-successor of ``q`` in this
        :py:class:`Automaton` instance, if any.

        Args:
            q (int): The source of the edge.
            r (int): The target of the edge.

        Returns:
            ``(e, True)`` if it exists a single edge from ``q`` to ``r``,
            ``(None, False)`` otherwise.
        """
        adj_q = self.adjacencies.get(q)
        (e, found) = (None, False)
        if adj_q:
            for (a, r_) in adj_q.items():
                if r == r_:
                    e = EdgeDescriptor(q, r, a)
                    found = True
                    break
        return (e, found)

    def symbol(self, q: int) -> str:
        """
        Retrieves the symbol installed on a state.

        Args:
            q (int): The vertex descriptor of the state.

        Raises:
            :py:class:`KeyError` if ``q`` is not a valid vertex descriptor

        Returns:
            The corresponding symbol.
        """
        return self.pmap_vsymbol[q]

    def out_edges(self, q: int) -> iter:
        """
        Retrieves an iterator over the out-transitions of a state ``q``
        involved in this :py:class:`Automaton` instance.

        Args:
            q (int): The source state.

        Returns:
            An iterator over the out-edges of ``u``.
        """
        return (
            EdgeDescriptor(q, r, a)
            for (a, r) in self.adjacencies[q].items()
        )

    def remove_edge(self, e: EdgeDescriptor):
        """
        Removes a transition from this :py:class:`NodeAutomaton` instance.

        Args:
            e (EdgeDescriptor): The edge descriptor of the transition to be removed.
        """
        q = self.source(e)
        r = self.target(e)
        a = self.symbol(r)
        adj_q = self.m_adjacencies.get(q)
        if adj_q:
            if a in adj_q:
                del adj_q[a]

    def sigma(self, q: int) -> set:
        """
        Computes sub-alphabet related to a given state of this
        :py:class:`NodeAutomaton` instance.

        Args:
            q (int): The vertex descriptor of the considered state.

        Returns:
            The corresponding set of symbols.
        """
        return (
            set(self.adjacencies.get(q, dict()).keys()) if q is not BOTTOM
            else set()
        )

    def alphabet(self) -> set:
        """
        Computes the (minimal) alphabet related to this
        :py:class:`NodeAutomaton` instance.

        Returns:
            The corresponding set of symbols.
        """
        return {
            self.symbol(q)
            for q in vertices(self)
            if not self.is_initial(q)
        }

    def edges(self) -> iter:
        """
        Retrieves an iterator over the transitions involved in this
        :py:class:`NodeAutomaton` instance.

        Returns:
            An iterator over the transitions.
        """
        return (
            EdgeDescriptor(q, r, a)
            for (q, adj_q) in self.adjacencies.items()
            for (a, r) in adj_q.items()
        )

    def label(self, e: EdgeDescriptor) -> str:
        """
        Overloads :py:meth:`Automaton.label` to retrieve the label
        assigned to a transition. The label is just the
        symbol of the target of the transition.

        Args:
            e (EdgeDescriptor): The edge descriptor of the considered
                transition.

        Returns:
            The symbol assigned to the considered transition.
        """
        return self.symbol(self.target(e))

    def to_dot(self, **kwargs) -> str:
        """
        Exports this :py:class:`Automaton` instance to a Graphviz string.
        See the :py:func:`to_dot` function.

        Returns:
            The corresponding Graphviz string.
        """
        dpv = {
            "shape":  make_func_property_map(
                lambda u: "doublecircle" if self.is_final(u) else "circle"
            ),
            "label":  make_func_property_map(
                lambda u: "^" if self.is_initial(u) else self.symbol(u)
            )
        }
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        return super().to_dot(**kwargs)


def add_vertex(a: str, g: NodeAutomaton) -> int:
    return g.add_vertex(a)


def symbol(q: int, g: NodeAutomaton) -> str:
    return g.symbol(q)


def add_edge(u: int, v: int, g: NodeAutomaton) -> tuple:
    return g.add_edge(u, v)


def edge(u: int, v: int, g: NodeAutomaton) -> tuple:
    return g.edge(u, v)


def make_node_automaton(
    transitions: list,
    pmap_vlabel: ReadPropertyMap,
    q0n: int = 0,
    pmap_vfinal: ReadPropertyMap = None,
    NodeAutomatonClass = NodeAutomaton
) -> NodeAutomaton:
    """
    Makes an automaton of type `NodeAutomatonClass`
    according to a list of transitions.
    You may use any arbitrary identifier to characterize
    the states involved in the transitions.

    Args:
        transitions (list): The list of transitions,
            where is each transition is modeled by
            a ``(qn, rn, a)`` tuple and where
            ``qn`` identifies the source of the transition
            ``rn`` identifies the target of the transition
            and ``a`` labels the transition.
        pmap_vlabel (ReadPropertyMap): A property map which maps each
            state identifier with its corresponding symbol.
        q0n (int): The identifier in transitions of the
            initial state.
        pmap_vfinal (ReadPropertyMap): A property map
            which maps each state identifier with a boolean indicating
            whether the state is final (``True``) or not (``False``).
        NodeAutomatonClass: The class use to allocate the automaton.
            Defaults to :py:class:`NodeAutomaton`.

    Example:

        >>> from collections import defaultdict
        >>> from pybgl import Automaton, make_assoc_property_map, make_node_automaton
        >>> transitions = [("root", "sink"), ("root", "sink")]
        >>> map_vlabel = defaultdict(bool, {"root": "a", "sink": "b"})
        >>> map_vfinal = defaultdict(bool, {"root": False, "sink": True})
        >>> g = make_node_automaton(
        ...     transitions,
        ...     q0n="root",
        ...     pmap_vlabel=make_assoc_property_map(map_vlabel),
        ...     pmap_vfinal=make_assoc_property_map(map_vfinal)
        ... )

    Returns:
        The corresponding `NodeAutomatonClass` instance.
    """
    if not pmap_vfinal:
        pmap_vfinal = make_assoc_property_map(defaultdict(bool))
    vertex_names = sorted(
        list(
            {qn for (qn, rn) in transitions} |
            {rn for (qn, rn) in transitions}
        )
    )
    map_vertices = {
        qn: q
        for (q, qn) in enumerate(vertex_names)
    }
    g = NodeAutomatonClass(0)
    for vertex_name in vertex_names:
        a = pmap_vlabel[vertex_name]
        u = g.add_vertex(a)
        if pmap_vfinal[u]:
            g.set_final(u)
    for (qn, rn) in transitions:
        q = map_vertices[qn]
        r = map_vertices[rn]
        g.add_edge(q, r)
    q0 = map_vertices[q0n]
    g.set_initial(q0)
    return g
