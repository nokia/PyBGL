#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from .incidence_graph import IncidenceGraph


def reverse_graph(g: IncidenceGraph):
    """
    Flips each arc involved in a graph.

    Args:
        g (IncidenceGraph): The input graph, updated in place.

    Returns:
        The flipped graph.
    """
    def swap(g, a, b):
        a_bak = getattr(g, a)
        setattr(g, a, getattr(g, b))
        setattr(g, b, a_bak)

    assert g.in_edges
    swap(g, "source", "target")
    swap(g, "in_edges", "out_edges")


def reverse_dict(d: dict) -> dict:
    """
    Reverses a dictionary (swap its key and its values).
    Note that (key, value) pair may disappear if the values
    are not unique.

    Args:
        d (dict): The input dictionary.

    Returns:
        The reversed dictionary.
    """
    return {v: k for (k, v) in d.items()}
