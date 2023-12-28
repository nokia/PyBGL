#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .graph import __len_gen__
from .property_map import ReadPropertyMap
from .incidence_automaton import in_degree, in_edges # Forward import
from .node_automaton import *

class IncidenceNodeAutomaton(NodeAutomaton):
    # TODO **kwargs
    def __init__(self, *args, pmap_vsymbol :ReadPropertyMap = None, **kwargs):
        """
        Constructor.

        Args:
            pmap_vsymbol (ReadPropertyMap): A property map which maps
                each state with its corresponding symbol.
        """
        self.predecessors = defaultdict(set) # predecessors[r] = {q}
        super().__init__(*args, pmap_vsymbol=pmap_vsymbol) # UGLY

    # TODO: Factorize with IncidenceAutomaton
    def add_edge(self, q: int, r: int) -> tuple:
        """
        Adds a transition to this :py:class:`IncidenceAutomaton` instance.
        Overloads the :py:meth:`Automaton.add_edge` method.

        Args:
            q (int): The vertex descriptor of source state of the new transition.
            r (int): The vertex descriptor of target state of the new transition.

        Returns:
            A tuple ``(e, success)`` where ``e`` is an :py:class:`EdgeDescriptor`
            compliant with this :py:class:`IncidenceAutomaton` class and ``success == True``
            if successful, ``(None, False)`` otherwise.
        """
        (e, added) = super().add_edge(q, r)
        if added:
            self.predecessors[r].add(q)
        return (e, added)

    def in_edges(self, r: int):
        """
        Gets an iterator over the in-edges of a vertex ``r``
        involved in this :py:class:`IncidenceAutomaton` instance.
        Overwrites the :py:class:`Graph.in_edges` method.

        Args:
            r (int): The target state.

        Returns:
            An iterator over the in-edges of ``r``.
        """
        return (
            EdgeDescriptor(q, r, self.symbol(r))
            for q in self.predecessors.get(r, set())
        )

    def remove_vertex(self, q: int):
        """
        Removes a vertex from this :py:class:`IncidenceAutomaton` instance.
        Overloads the :py:class:`Graph.remove_vertex` method.

        Args:
            u (int): The vertex descriptor of the vertex to be removed.

        Raises:
            `KeyError` if ``u`` does not exist.
        """
        # Note: we could rely on remove_edge for each in/out-edge, but the
        # following implementation is faster.

        # In-edges: (p, q) edges
        if q in self.predecessors.keys():
            a = self.symbol(q)
            for e in self.in_edges(q):
                p = self.source(e)
                del self.adjacencies[p][a]
            del self.predecessors[q]

        # Out-edges: (q, r) edges
        if q in self.adjacencies.keys():
            for e in self.out_edges(q):
                r = self.target(e)
                if q in self.predecessors[r]:
                    # This test is required to cope with parallel (q, r) edges.
                    self.predecessors[r].remove(q)
            del self.adjacencies[q]

    def remove_edge(self, e: EdgeDescriptor):
        """
        Removes an edge from this :py:class:`IncidenceAutomaton` instance.
        Overloads the :py:class:`Graph.remove_edge` method.

        Args:
            e (EdgeDescriptor): The edge descriptor of the edge to be removed.
        """
        super().remove_edge(e)
        q = self.source(e)
        r = self.target(e)
        self.predecessors[r].remove(q)


def make_incidence_node_automaton(
    transitions: list,
    pmap_vlabel: ReadPropertyMap,
    q0n: int = 0,
    pmap_vfinal: ReadPropertyMap = None
) -> IncidenceNodeAutomaton:
    """
    Specialization of the :py:func:`make_node_automaton` function for
    the :py:class:`IncidenceNodeAutomaton` class.

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
        >>> from pybgl import Automaton, make_assoc_property_map, make_incidence_node_automaton
        >>> transitions = [("root", "sink"), ("root", "sink")]
        >>> map_vlabel = defaultdict(bool, {"root": "a", "sink": "b"})
        >>> map_vfinal = defaultdict(bool, {"root": False, "sink": True})
        >>> g = make_incidence_node_automaton(
        ...     transitions,
        ...     q0n="root",
        ...     pmap_vlabel=make_assoc_property_map(map_vlabel),
        ...     pmap_vfinal=make_assoc_property_map(map_vfinal)
        ... )

    Returns:
        The corresponding :py:class:`IncidenceNodeAutomaton` instance.

    """
    return make_node_automaton(
        transitions,
        pmap_vlabel,
        q0n,
        pmap_vfinal,
        NodeAutomatonClass=IncidenceNodeAutomaton
    )
