#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict
from .automaton import *
# from .automaton import BOTTOM, DirectedGraph, EdgeDescriptor
from .graphviz import enrich_kwargs
from .property_map import (
    ReadWritePropertyMap,
    make_assoc_property_map,
    make_func_property_map
)


EPSILON = "\u03b5"


class Nfa(DirectedGraph):
    """
    The :py:class:`Nfa` implements a
    `Non-deterministic Finite Automaton
    <https://en.wikipedia.org/wiki/Nondeterministic_finite_automaton>`__.
    """
    def __init__(
        self,
        num_vertices: int = 0,
        initials: set = None,
        pmap_vfinal: ReadWritePropertyMap = None,
        epsilon: str = EPSILON
    ):
        """
        Constructor.

        Args:
            num_vertices (int): Pass the (initial) number of vertices.
            initials (str): The vertex descriptors of the initial states.
            pmap_vfinal (ReadPropertyMap): A :py:class:`ReadPropertyMap`
                that maps a vertex descriptor with a boolean which
                equals ``True`` if the vertex is a final state
                ``None`` otherwise.
            epsilon (str): The symbol assigned to the epsilon-transition.
        """
        super().__init__(num_vertices)
        self.initials = initials if initials else {0}
        if not pmap_vfinal:
            self.map_vfinal = defaultdict(bool)
            self.pmap_vfinal = make_assoc_property_map(self.map_vfinal)
        else:
            self.pmap_vfinal = pmap_vfinal
        self.epsilon = epsilon

    def delta_one_step(self, qs: iter, a: str) -> set:
        """
        Determines the target states reached by consuming a symbol
        from a subset of states.
        This function is an implementation detail of
        the :py:meth:`Nfa.delta` method.

        Args:
            qs (iter): The subset of states.
            a (str): The consumed symbol.

        Returns:
            The set of reached states.
        """
        sets = [
            set(self.adjacencies.get(q, dict()).get(a, dict()).keys())
            for q in qs
        ]
        return set.union(*sets) if sets else set()

    def delta_epsilon(self, qs: set) -> set:
        """
        Determines the states reached without consuming any symbol
        from a subset of states.

        Args:
            qs (iter): The subset of states.

        Returns:
            The set of reached states.
        """
        ret = set()
        qs_new = set(qs)
        while qs_new:
            ret |= qs_new
            qs_new = self.delta_one_step(qs_new, self.epsilon)
            qs_new -= ret
        return ret

    def delta(self, q: int, a: str) -> set:
        """
        Transition function, allowing to move from a state ``q`` to its
        ``a``-successor, if any.
        See also :py:meth:`Nfa.delta_word`.

        Args:
            q (int): The vertex descriptor of a state of this
                :py:class:`Nfa` instance.
            a (str): The symbol.

        Returns:
            The reached states
        """
        qs = self.delta_epsilon({q})
        qs = self.delta_one_step(qs, a)
        qs = self.delta_epsilon(qs)
        return qs

    def sigma(self, q: int) -> set:
        """
        Computes sub-alphabet related to a given state of this
        :py:class:`Nfa` instance.

        Args:
            q (int): The vertex descriptor of the considered state.

        Returns:
            The corresponding set of symbols.
        """
        qs = self.delta_epsilon({q})
        return (
            set() if q is BOTTOM else
            {
                a
                for q in qs
                for a in self.adjacencies.get(q, dict()).keys()
                if a != self.epsilon
            }
        )

    def add_edge(self, q: int, r: int, a: str) -> tuple:
        """
        Adds a transition to this :py:class:`Nfa` instance.

        Args:
            q (int): The vertex descriptor of source state of the
                new transition.
            r (int): The vertex descriptor of target state of the
                new transition.
            a (str): The symbol labeling this transition.

        Returns:
            A tuple ``(e, success)`` where ``e`` is an
            :py:class:`EdgeDescriptor` compliant with this :py:class:`Nfa`
            class and ``success == True`` if successful,
            ``(None, False)`` otherwise.
        """
        arn = self.adjacencies.get(q)
        if arn is None:
            arn = self.adjacencies[q] = dict()
        rn = arn.get(a)
        if rn is None:
            rn = self.adjacencies[q][a] = dict()
        s = rn.get(r)
        if s is None:
            s = rn[r] = set()
        n = len(s) + 1
        s.add(n)
        return (EdgeDescriptor(q, r, (a, n)), True)

    def remove_edge(self, e: EdgeDescriptor):
        """
        Removes a transition from this :py:class:`Nfa` instance.

        Args:
            e (EdgeDescriptor): The edge descriptor of the transition
                to be removed.
        """
        q = self.source(e)
        r = self.target(e)
        (a, n) = e.distinguisher
        try:
            del self.adjacencies[q][a][r]
        except KeyError:
            pass

    def out_edges(self, q: int):
        """
        Retrieves an iterator over the out-edges of a state ``q``
        involved in this :py:class:`Nfa` instance.

        Args:
            u (int): The source state.

        Returns:
            An iterator over the out-edges of ``u``.
        """
        return (
            EdgeDescriptor(q, r, (a, n))
            for (a, rn) in self.adjacencies.get(q, dict()).items()
            for (r, n) in rn.items()
        )

    def edges(self):
        """
        Retrieves an iterator over the transitions involved in this
        :py:class:`Nfa` instance.

        Returns:
            An iterator over the transitions.
        """
        return (
            EdgeDescriptor(q, r, (a, n))
            for (q, arn) in self.adjacencies.items()
            for (a, rn) in arn.items()
            for (r, n) in rn.items()
        )

    def alphabet(self) -> set:
        """
        Computes the (minimal) alphabet related to this
        :py:class:`Nfa` instance.

        Returns:
            The corresponding set of symbols.
        """
        return {
            a
            for (q, arn) in self.adjacencies.items()
            for a in arn.keys()
            if a != self.epsilon
        }

    def set_initial(self, q: int, is_initial: bool = True):
        """
        Sets the status of a state as an initial state of this
        :py:class:`Nfa` instance.

        Args:
            q (int): The vertex descriptor of the new initial state.
            is_initial (bool): Pass ``True`` if ``q`` must be the
                new initial state, ``False`` otherwise.
        """
        if is_initial:
            self.initials.add(q)
        else:
            self.initials.discard(q)

    def initials(self) -> set:
        """
        Retrieves the initial states of this :py:class:`Nfa` instance.

        Returns:
            The initial states of the NFA.
        """
        return self.initials

    def is_initial(self, q: int) -> bool:
        """
        Tests whether state is an initial state of this
        :py:class:`Nfa` instance.

        Args:
            q (int): The vertex descriptor of the considered state.

        Returns:
            ``True`` if ``q`` is the initial state,
            ``None`` otherwise.
        """
        return q in self.initials

    def set_initials(self, q0s: set):
        """
        Sets the initial states of this :py:class:`Nfa` instance.

        Args:
            q0s (iter): The new set of initial states.
        """
        self.initials = {q0 for q0 in q0s}

    def label(self, e: EdgeDescriptor) -> str:
        """
        Retrieves the symbol assigned to a transition of this
        :py:class:`Nfa` instance.

        Args:
            e (EdgeDescriptor): The edge descriptor of the considered
                transition.

        Returns:
            The symbol assigned to the considered transition.
        """
        (a, n) = e.distinguisher
        return a

    def set_final(self, q: int, is_final: bool = True):
        """
        Sets the status of a state as a final state of this
        :py:class:`Nfa` instance.

        Args:
            q (int): The vertex descriptor of the new initial state.
            is_initial (bool): Pass ``True`` if ``q`` must be the
                new initial state, ``False`` otherwise.
        """

        self.pmap_vfinal[q] = is_final

    def is_final(self, q: int) -> bool:
        """
        Tests whether state is a final state of this
        :py:class:`Nfa` instance.

        Args:
            q (int): The vertex descriptor of the considered state.

        Returns:
            ``True`` if ``q`` is the final state,
            ``None`` otherwise.
        """
        return self.pmap_vfinal[q]

    def to_dot(self, **kwargs) -> str:
        """
        Exports this :py:class:`Nfa` instance to a Graphviz string.
        See the :py:func:`to_dot` function.

        Returns:
            The corresponding graphviz string.
        """
        dpv = {
            "shape":  make_func_property_map(
                lambda u: "doublecircle" if self.is_final(u) else "circle"
            ),
        }
        dpe = {
            "label":  make_func_property_map(
                lambda e: (
                    "<i>\u03b5</i>" if self.label(e) == self.epsilon
                    else self.label(e)
                )
            )
        }
        kwargs = enrich_kwargs(dpv, "dpv", **kwargs)
        kwargs = enrich_kwargs(dpe, "dpe", **kwargs)
        return super().to_dot(**kwargs)

    def accepts(self, w: str) -> True:
        """
        Tests whether this :py:class:`Nfa` instance accepts a word,
        meaning there exist a state reached from its initial state by
        consuming successively each character of the input word.

        Args:
            w (str): The input word.

        Returns:
            ``True`` if the automaton accepts ``w``
            ``False`` otherwise.
        """
        return any(
            self.is_final(q)
            for q in self.delta_word(w)
        )

    def delta_word(self, w) -> set:
        """
        Transition function, allowing to move from an initial state
        to the state reached by consuming each character of a word ``w``,
        if any. See also the :py:meth:`Nfa.delta` method.

        Args:
            w (str): The word.

        Returns:
            The reached states
        """
        qs = set(self.initials)
        qs = self.delta_epsilon(qs)
        for a in w:
            if not qs:
                break
            qs = set.union(*[self.delta(q, a) for q in qs])
        return qs

    def finals(self) -> iter:
        """
        Retrieves the final states of this :py:class:`Nfa` instance.

        Returns:
            The final initial states of the NFA.
        """
        return (q for q in self.vertices() if self.is_final(q))

    def is_epsilon_transition(self, e: EdgeDescriptor) -> bool:
        """
        Tests whether a transition is labeled by the empty word.

        Args:
            e (EdgeDescriptor): The edge descriptor of the transition.
            nfa (Nfa): A non-deterministic automaton.

        Returns:
            ``True`` if the transition is labeled by the empty word,
            ``False`` otherwise.
        """
        return self.label(e) == self.epsilon


def epsilon(nfa: Nfa) -> str:
    """
    Retrieves the symbol representing the empty word.

    Args:
        nfa (Nfa): A non-deterministic automaton.

    Returns:
        The symbol representing the empty word.
    """
    return nfa.epsilon


def is_epsilon_transition(e: EdgeDescriptor, nfa: Nfa) -> bool:
    """
    Tests whether a transition is labeled by the empty word.

    Args:
        e (EdgeDescriptor): The edge descriptor of the transition.
        nfa (Nfa): A non-deterministic automaton.

    Returns:
        ``True`` if the transition is labeled by the empty word,
        ``False`` otherwise.
    """
    return nfa.is_epsilon_transition(e)


def initials(nfa: Nfa) -> iter:
    """
    Retrieves the initial states of a NFA.

    Args:
        nfa (Nfa): A non-deterministic automaton.

    Returns:
        The initial states of the NFA.
    """
    return (q for q in nfa.initials)


def set_initials(q0s: iter, nfa: Nfa):
    """
    Sets the initial states of a NFA.

    Args:
        q0s (iter): The new set of initial states.
        nfa (Nfa): A non-deterministic automaton.
    """
    nfa.set_initials(q0s)


def delta_word(w: str, nfa: Nfa) -> set:
    """
    Adapts :py:func:`Automaton.delta_word` for NFAs.

    Args:
        w (str): The word to consume.
        nfa (Nfa): A non-deterministic automaton.

    Returns:
        The set of reached states.
    """
    return nfa.delta_word(w)
