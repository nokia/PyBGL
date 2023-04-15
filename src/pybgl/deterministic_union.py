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

from pybgl.automaton import Automaton, EdgeDescriptor
from .parallel_breadth_first_search import \
    ParallelBreadthFirstSearchVisitor, \
    parallel_breadth_first_search
from .product_mixin import ProductMixin

class DeterministicUnionVisitor(ParallelBreadthFirstSearchVisitor, ProductMixin):
    def __init__(self, g12 :Automaton):
        super().__init__(g12, lambda a, b: a or b)
    def examine_edge(self, e1 :EdgeDescriptor, g1 :Automaton, e2 :EdgeDescriptor, g2 :Automaton, a :chr):
        self.add_product_edge(e1, g1, e2, g2)

def deterministic_union(
    g1  :Automaton,
    g2  :Automaton,
    g12 :Automaton = None,
    vis :DeterministicUnionVisitor = None
):
    if not g12:
        g12 = Automaton()
    if not vis:
        vis = DeterministicUnionVisitor(g12)
    parallel_breadth_first_search(g1, g2, vis = vis)
    return g12


