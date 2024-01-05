#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict

# NB: pybgl.graph.edge and pybgl.graph.add_edge are overloaded by
# this file because they don't have the same signature.
from .graph import *
# from .graph import DirectedGraph, EdgeDescriptor
from .graphviz import enrich_kwargs
from .property_map import (
    ReadPropertyMap,
    make_assoc_property_map,
    make_func_property_map,
)


BOTTOM = None


class Automaton(DirectedGraph):
    """
    The :py:class:`Automaton` implements a
    `Deterministic Finite Automaton
    <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`__.
    """
    # Convention: EdgeDescriptor(q, r, a)
    # Convention: self.adjacencies[q][a] == r
    def __init__(
        self,
        num_vertices: int = 0,
        q0: int = 0,
        pmap_vfinal: ReadPropertyMap = None
    ):
        """
        Constructor.

        Args:
            num_vertices (int): Pass the (initial) number of vertices.
            q0 (int): The vertex descriptor of the initial state.
            pmap_vfinal (ReadPropertyMap): A :py:class:`ReadPropertyMap`
                that maps a vertex descriptor with a boolean which
                equals ``True`` if the vertex is a final state
                ``None`` otherwise.
        """
        super().__init__(num_vertices)
        self.q0 = q0
        if not pmap_vfinal:
            self.map_vfinal = defaultdict(bool)
            self.pmap_vfinal = make_assoc_property_map(self.map_vfinal)
        else:
            self.pmap_vfinal = pmap_vfinal

    def delta(self, q: int, a: str) -> int:
        """
        Transition function, allowing to move from a state ``q`` to its
        ``a``-successor, if any.
        See also :py:meth:`Automaton.delta_word`.

        Args:
            q (int): The vertex descriptor of a state of this
                :py:class:`Automaton` instance.
            a (str): The symbol.

        Returns:
            The reached state (if any), :py:data:`BOTTOM` otherwise.
        """
        return self.adjacencies.get(q, dict()).get(a, BOTTOM)

    def add_edge(self, q: int, r: int, a: str) -> tuple:
        """
        Adds a transition to this :py:class:`Automaton` instance.

        Args:
            q (int): The vertex descriptor of source state of the
                new transition.
            r (int): The vertex descriptor of target state of the
                new transition.
            a (str): The label of the new transition.

        Returns:
            A tuple ``(e, success)`` where ``e`` is an
            :py:class:`EdgeDescriptor` compliant with this
            :py:class:`Automaton` class and ``success == True``
            if successful, ``(None, False)`` otherwise.
        """
        assert q is not None
        assert r is not None
        if self.delta(q, a):
            return (None, False)
        self.adjacencies[q][a] = r
        return (EdgeDescriptor(q, r, a), True)

    def edge(self, q: int, r: int, a: str) -> tuple:
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
        assert q is not BOTTOM
        return (
            (EdgeDescriptor(q, r, a), True) if (
                q is not None
                and r == self.delta(q, a)
            )
            else (None, False)
        )

    def in_edges(self, q: int):
        """
        Retrieves an iterator over the in-edges of a state ``q``
        involved in this :py:class:`Automaton` instance.

        Args:
            q (int): The target vertex.

        Raises:
            ``RuntimeError`` as a :py:class:`Automaton` must not
            support this primitive. If you require it, use the
            :py:class:`IncidenceAutomaton` class.

        Returns:
            An iterator over the edges of ``q``.
        """
        raise RuntimeError("Nope.")

    def out_edges(self, q: int) -> iter:
        """
        Retrieves an iterator over the out-transitions of a state ``q``
        involved in this :py:class:`Automaton` instance.

        Args:
            q (int): The source state.

        Returns:
            An iterator over the out-edges of ``q``.
        """
        return (
            EdgeDescriptor(q, r, a)
            for (a, r) in self.adjacencies.get(q, dict()).items()
        )

    def remove_edge(self, e: EdgeDescriptor):
        """
        Removes a transition from this :py:class:`Automaton` instance.

        Args:
            e (EdgeDescriptor): The edge descriptor of the
                transition to be removed.
        """
        q = self.source(e)
        a = self.label(e)
        adj_q = self.adjacencies.get(q)
        if adj_q:
            if a in adj_q.keys():
                del adj_q[a]

    def sigma(self, q: int) -> set:
        """
        Computes sub-alphabet related to a given state of this
        :py:class:`Automaton` instance.

        Args:
            q (int): The vertex descriptor of the considered state.

        Returns:
            The corresponding set of symbols.
        """
        return {
            a
            for a in self.adjacencies.get(q, dict()).keys()
        } if q is not None else set()

    def alphabet(self) -> set:
        """
        Computes the (minimal) alphabet related to this
        :py:class:`Automaton` instance.

        Returns:
            The corresponding set of symbols.
        """
        return {
            a
            for q in self.vertices()
            for a in self.adjacencies.get(q, dict()).keys()
        }

    def edges(self) -> iter:
        """
        Retrieves an iterator over the transitions involved in this
        :py:class:`Automaton` instance.

        Returns:
            An iterator over the transitions.
        """
        return (
            EdgeDescriptor(q, r, a)
            for (q, adj_q) in self.adjacencies.items()
            for (a, r) in adj_q.items()
        )

    def set_initial(self, q: int, is_initial: bool = True):
        """
        Sets the status of a state as the initial state of this
        :py:class:`Automaton` instance.

        Args:
            q (int): The vertex descriptor of the new initial state.
            is_initial (bool): Pass ``True`` if ``q`` must be the
                new initial state, ``False`` otherwise.
        """
        if is_initial:
            self.q0 = q
        elif self.q0 == q:
            self.q0 = None

    def initial(self) -> int:
        """
        Returns the vertex descriptor of the initial state of this
        :py:class:`Automaton` instance.

        Returns:
            The vertex descriptor of the initial state if set,
            ``None`` otherwise.
        """
        return self.q0

    def is_initial(self, q: int) -> bool:
        """
        Tests whether state is the initial state of this
        :py:class:`Automaton` instance.

        Args:
            q (int): The vertex descriptor of the considered state.

        Returns:
            ``True`` if ``q`` is the initial state,
            ``None`` otherwise.
        """
        return self.q0 == q

    def label(self, e: EdgeDescriptor) -> str:
        """
        Retrieves the symbol assigned to a transition of this
        :py:class:`Automaton` instance.

        Args:
            e (EdgeDescriptor): The edge descriptor of the considered
                transition.

        Returns:
            The symbol assigned to the considered transition.
        """
        return e.distinguisher

    def set_final(self, q: int, is_final: bool = True):
        """
        Sets the status of a state as the final state of this
        :py:class:`Automaton` instance.

        Args:
            q (int): The vertex descriptor of the new final state.
            is_final (bool): Pass ``True`` if ``q`` must be the
                new final state, ``False`` otherwise.
        """
        self.pmap_vfinal[q] = is_final

    def is_final(self, q: int) -> bool:
        """
        Tests whether state is a final state of this
        :py:class:`Automaton` instance.

        Args:
            q (int): The vertex descriptor of the considered state.

        Returns:
            ``True`` if ``q`` is a final state,
            ``None`` otherwise.
        """
        return self.pmap_vfinal[q]

    def finals(self) -> set:
        """
        Returns the vertex descriptors of the final states of this
        :py:class:`Automaton` instance.

        Returns:
            The vertex descriptors of the final state if set,
            ``None`` otherwise.
        """
        return {
            q
            for q in self.vertices()
            if self.is_final(q)
        }

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
        }
        dpe = {
            "label":  make_func_property_map(self.label)
        }
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        kwargs = enrich_kwargs(dpe, "dpe", **kwargs)
        return super().to_dot(**kwargs)

    def delta_word(self, q: int, w: str) -> int:
        """
        Transition function, allowing to move from a state ``q``
        to the state reached by consuming each character of a word
        ``w``, if any. See also the :py:meth:`Automaton.delta` method.

        Args:
            q (int): The vertex descriptor of a state of this
                :py:class:`Automaton` instance.
            w (str): The word.

        Returns:
            The reached state (if any), :py:data:`BOTTOM` otherwise.
        """
        for a in w:
            if q is BOTTOM:
                return q
            q = self.delta(q, a)
        return q

    def accepts(self, w: str) -> bool:
        """
        Tests whether this :py:class:`Automaton` instance accepts a word,
        meaning there exist a state reached from its initial state by
        consuming successively each character of the input word.

        Args:
            w (str): The input word.

        Returns:
            ``True`` if the automaton accepts ``w``
            ``False`` otherwise.
        """
        q0 = self.initial()
        q = self.delta_word(q0, w)
        return q is not BOTTOM and self.is_final(q)

    @staticmethod
    def is_finite() -> bool:
        """
        Tests whether this :py:class:`Automaton` instance is finite or not.

        Returns:
            ``True``.
        """
        return True  # By design of Automaton.

    @staticmethod
    def is_deterministic() -> bool:
        """
        Tests whether this :py:class:`Automaton` instance is
        deterministic or not.

        Returns:
            ``True``.
        """
        return True  # By design of Automaton.

    def is_complete(self) -> bool:
        """
        Tests whether this :py:class:`Automaton` instance is complete or not,
        i.e., if each state of this automaton is has
        for each symbol `a` of its alphabet a ``a``-successor.

        Returns:
            ``True`` if this :py:class:`Automaton` is complete,
            ``False`` otherwise.
        """
        alpha = self.alphabet()
        for q in self.vertices():
            if self.sigma(q) != alpha:
                return False
        return True

    def delta_best_effort(self, w: str) -> tuple:
        """
        Transition function, allowing to move from the initial state
        to the state reached by consuming each character of a word ``w``,
        while possible.
        See also :py:meth:`Automaton.delta_word`.

        Args:
            w (str): The word.

        Returns:
            The reached state in best effort.
        """
        q = self.initial()
        if not w:
            return (q, 0)
        for (i, a) in enumerate(w):
            r = self.delta(q, a)
            if r is BOTTOM:
                return (q, i)
            q = r
        return (q, i + 1)

    def automaton_insert_string(self, w: str) -> int:
        """
        Updates this :py:class:`Automaton` instance by adding states
        and transition so that it accepts a word ``w``.

        Args:
            w (str): The word.

        Returns:
            The reached state in best effort.
        """
        (q, i) = self.delta_best_effort(w)
        for a in w[i:]:
            r = self.add_vertex()
            self.add_edge(q, r, a)
            q = r
        self.set_final(q)


# ------------------------------------------------------------------
# Methods wrappers. This is to reuse the same naming as in the BGL
# but in python.
# ------------------------------------------------------------------

def accepts(w: str, g: Automaton) -> bool:
    """
    Tests whether an automaton accepts a word,
    meaning there exist a state reached from its initial state by
    consuming successively each character of the input word.
    See also :py:meth:`Automaton.accepts` and :py:func:`accepts_debug`.

    Args:
        w (str): The input word.
        g (Automaton): The considered automaton.

    Returns:
        ``True`` if the automaton accepts ``w``
        ``False`` otherwise.
    """
    return g.accepts(w)


def accepts_debug(w: str, g: Automaton) -> bool:
    """
    Tests whether an automaton accepts a word, by printing for
    each consumed symbol the reached state.

    Args:
        w (str): The input word.
        g (Automaton): The considered automaton.

    Returns:
        ``True`` if the automaton accepts ``w``
        ``False`` otherwise.
    """
    q = initial(g)
    print(f"w = {w} q0 = {q}")
    for (i, a) in enumerate(w):
        print(f"w[{i}] = {a}, {q} -> {delta(q, a, g)}")
        if q is BOTTOM:
            return False
        q = delta(q, a, g)
    return is_final(q, g)


def add_edge(q: int, r: int, a: str, g: Automaton) -> tuple:
    """
    Adds a transition to an :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.add_edge`.

    Args:
        q (int): The vertex descriptor of source state of the new transition.
        r (int): The vertex descriptor of target state of the new transition.
        a (str): The label of the new transition.
        g (Automaton): The considered automaton.

    Returns:
        A tuple ``(e, success)`` where ``e`` is an :py:class:`EdgeDescriptor`
        compliant with this :py:class:`Automaton` class and ``success == True``
        if successful, ``(None, False)`` otherwise.
    """
    return g.add_edge(q, r, a)


def edge(q: int, r: int, a: str, g: Automaton) -> tuple:
    """
    Retrieves the edge from a state ``q`` to state ``r`` in
    a :py:class:`Automaton` instance, if any.
    See also :py:meth:`Automaton.edge`.

    Args:
        q (int): The source of the edge.
        r (int): The target of the edge.
        g (Automaton): The considered automaton.

    Returns:
        ``(e, True)`` if it exists a single edge from ``q`` to ``r``,
        ``(None, False)`` otherwise.
    """
    return g.edge(q, r, a)


def sigma(q: int, g: Automaton) -> set:
    """
    Computes sub-alphabet related to a given state of a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.sigma`.

    Args:
        q (int): The vertex descriptor of the considered state.
        g (Automaton): The considered automaton.

    Returns:
        The corresponding set of symbols.
    """
    return g.sigma(q)


def alphabet(g: Automaton) -> set:
    """
    Computes the (minimal) alphabet related to a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.alphabet`.

    Args:
        g (Automaton): The considered automaton.

    Returns:
        The corresponding set of symbols.
    """
    return g.alphabet()


def is_initial(q: int, g: Automaton) -> bool:
    """
    Tests whether state is the initial state of a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.is_initial`.

    Args:
        q (int): The vertex descriptor of the considered state.
        g (Automaton): The considered automaton.

    Returns:
        ``True`` if ``q`` is the initial state,
        ``None`` otherwise.
    """
    return g.is_initial(q)


def initial(g: Automaton) -> int:
    """
    Returns the vertex descriptor of the initial state of a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.initial`.

    Args:
        g (Automaton): The considered automaton.

    Returns:
        The vertex descriptor of the initial state if set,
        ``None`` otherwise.
    """
    return g.initial()


def is_final(q: int, g: Automaton) -> bool:
    """
    Tests whether state is a final state of a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.is_final`.

    Args:
        q (int): The vertex descriptor of the considered state.
        g (Automaton): The considered automaton.

    Returns:
        ``True`` if ``q`` is a final state,
        ``None`` otherwise.
    """
    return g.is_final(q)


def label(e: EdgeDescriptor, g: Automaton) -> str:
    """
    Retrieves the symbol assigned to a transition of a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.label`.

    Args:
        e (EdgeDescriptor): The edge descriptor of the considered
            transition.
        g (Automaton): The considered automaton.

    Returns:
        The symbol assigned to the considered transition.
    """
    return g.label(e)


def set_initial(q: int, g: Automaton, is_initial: bool = True):
    """
    Sets the status of a state as the initial state of a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.set_initial`.

    Args:
        q (int): The vertex descriptor of the new initial state.
        g (Automaton): The considered automaton.
        is_initial (bool): Pass ``True`` if ``q`` must be the
            new initial state, ``False`` otherwise.
    """
    g.set_initial(q, is_initial)


def set_final(q: int, g: Automaton, is_final: bool = True):
    """
    Sets the status of a state as the final state of this
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.set_final`.

    Args:
        q (int): The vertex descriptor of the new final state.
        g (Automaton): The considered automaton.
        is_final (bool): Pass ``True`` if ``q`` must be the
            new final state, ``False`` otherwise.
    """
    g.set_final(q, is_final)


def finals(g: Automaton) -> set:
    """
    Returns the vertex descriptors of the final states of a
    :py:class:`Automaton` instance.
    See also :py:meth:`Automaton.finals`.

    Args:
        g (Automaton): The considered automaton.

    Returns:
        The vertex descriptors of the final state if set,
        ``None`` otherwise.
    """
    return g.finals()


def delta(q: int, a: str, g: Automaton) -> int:
    """
    Transition function, allowing to move from a state ``q`` to its
    ``a``-successor, if any.
    See also :py:meth:`Automaton.delta`.

    Args:
        q (int): The vertex descriptor of a state of this
            :py:class:`Automaton` instance.
        a (str): The symbol.
        g (Automaton): The considered automaton.

    Returns:
        The reached state (if any), :py:data:`BOTTOM` otherwise.
    """
    return g.delta(q, a)


def delta_word(q: int, w: str, g: Automaton) -> int:
    """
    Transition function, allowing to move from a state ``q``
    to the state reached by consuming each character of a word ``w``, if any.
    See also :py:meth:`Automaton.delta_word` and :py:func:`delta_best_effort`.

    Args:
        q (int): The vertex descriptor of a state of this
            :py:class:`Automaton` instance.
        w (str): The word.
        g (Automaton): The considered automaton.

    Returns:
        The reached state (if any), :py:data:`BOTTOM` otherwise.
    """
    return g.delta_word(q, w)


def is_finite(g) -> bool:
    """
    Tests whether an :py:class:`Automaton` instance is finite or not.
    See also :py:meth:`Automaton.is_finite`.

    Returns:
        ``True``.
    """
    return g.is_finite()


def is_deterministic(g) -> bool:
    """
    Tests whether an :py:class:`Automaton` instance is deterministic or not.
    See also :py:meth:`Automaton.is_deterministic`.

    Returns:
        ``True``.
    """
    return g.is_deterministic()


def is_complete(g) -> bool:
    """
    Tests whether this :py:class:`Automaton` instance is complete or not,
    i.e., if each state of this automaton is has
    for each symbol `a` of its alphabet a ``a``-successor.

    Returns:
        ``True`` if this :py:class:`Automaton` is complete,
        ``False`` otherwise.
    """
    return g.is_complete()


# --------------------------------------------------
# Extra methods
# --------------------------------------------------

def is_minimal(g) -> bool:
    return NotImplementedError()


def make_automaton(
    transitions: list,
    q0n: int = 0,
    pmap_vfinal: ReadPropertyMap = None,
    Constructor=Automaton
):
    """
    Makes an automaton of type `AutomatonClass`
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
        q0n (int): The identifier in transitions of the
            initial state.
        pmap_vfinal (ReadPropertyMap): A property map
            which maps each state identifier with a boolean indicating
            whether the state is final (``True``) or not (``False``).
        Constructor: The class use to allocate the automaton.
            Defaults to :py:class:`Automaton`.

    Example:
        >>> from collections import defaultdict
        >>> from pybgl import (
        ...      Automaton, make_assoc_property_map, make_automaton
        ... )
        >>> transitions = [("root", "sink", "a"), ("root", "sink", "b")]
        >>> map_vfinal = defaultdict(bool, {"root": False, "sink": True})
        >>> g = make_automaton(
        ...     transitions, "root",
        ...     make_assoc_property_map(map_vfinal)
        ... )

    Returns:
        The corresponding automaton.
    """
    if not pmap_vfinal:
        pmap_vfinal = make_assoc_property_map(defaultdict(bool))
    vertex_names = sorted(
        list(
            {qn for (qn, rn, a) in transitions} |
            {rn for (qn, rn, a) in transitions}
        )
    )
    map_vertices = {
        qn: q
        for (q, qn) in enumerate(vertex_names)
    }
    g = Constructor(len(vertex_names))
    for (qn, rn, a) in transitions:
        q = map_vertices[qn]
        r = map_vertices[rn]
        g.add_edge(q, r, a)
    if g.has_vertex():
        q0 = map_vertices[q0n]
        g.set_initial(q0)
    for q in g.vertices():
        qn = vertex_names[q]
        if pmap_vfinal[qn]:
            g.set_final(q)
    return g


def delta_best_effort(g: Automaton, w: str) -> tuple:
    """
    Transition function, allowing to move from the initial state
    to the state reached by consuming each character of a word ``w``,
    while possible.
    See also :py:meth:`Automaton.delta_word`.

    Args:
        w (str): The word.
        g (Automaton): The considered automaton.

    Returns:
        The reached state in best effort.
    """
    return g.delta_best_effort(w)


def automaton_insert_string(g: Automaton, w: str) -> int:
    """
    Updates an :py:class:`Automaton` instance by adding states
    and transition so that it accepts a word ``w``.

    Args:
        g (Automaton): The considered automaton.
        w (str): The word.

    Returns:
        The reached state in best effort.
    """
    g.automaton_insert_string(w)
