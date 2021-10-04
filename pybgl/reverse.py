#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Class allowing to aggregate a list of compatible visitors
# into a single visitor.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.incidence_graph import IncidenceGraph

def reverse_graph(g :IncidenceGraph):
    def swap(g, a, b):
        a_bak = getattr(g, a)
        setattr(g, a, getattr(g, b))
        setattr(g, b, a_bak)

    assert g.in_edges
    swap(g, "source", "target")
    swap(g, "in_edges", "out_edges")

def reverse_dict(d :dict) -> dict:
    return {v : k for (k, v) in d.items()}
