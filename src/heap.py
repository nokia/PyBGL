#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2021, Nokia"
__license__    = "BSD-3"

import heapq

class Comparable(object):
    """
    Wrapper used to define a custom pre-order for a given instance.
    """
    # Inspired from functools.cmp_to_key and:
    # https://stackoverflow.com/questions/8875706/heapq-with-custom-compare-predicate
    # The objects to be sorted are wrapped in a K instance
    # that implements the < operator called by the sorting function.
    def __init__(self, obj :object, preorder :callable = None):
        """
        Constructor.
        Args:
            obj: An `Element` instance.
            preorder: A `callable` acting as a preorder.
        Example:
            x = Comparable(5, lambda a, b: a >= b)
        """
        self.obj = obj
        assert preorder
        self.preorder = preorder
    def __lt__(self, other) -> bool:
        return not self.preorder(other.obj, self.obj)
    def __le__(self, other) -> bool:
        return self.preorder(self.obj, other.obj)
    def __eq__(self, other) -> bool:
        return (
            self.preorder(self.obj, other.obj) and
            self.preorder(other.obj, self.obj)
        )
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    def __gt__(self, other) -> bool:
        return not self.preorder(self.obj, other.obj)
    def __ge__(self, other) -> bool:
        return self.preorder(other.obj, self.obj)
    def __str__(self) -> str:
        return "Comparable(%s)" % self.obj
    def __repr__(self) -> str:
        return "Comparable(%r)" % self.obj

def compare_to_key(preorder :callable):
    """
    Convert a preorder to a key callback (used e.g. by sort functions in python).
    Args:
        preorder: A `callable(Element, Element)` that is preorder over the space of Elements.
    Example:
        key = compare_to_key(lambda a, b: a >= b)
    """
    return lambda x: Comparable(x, preorder)

class Heap:
    def __init__(self, elements :iter = None, to_comparable :callable = None):
        """
        `Heap` constructor.
        Args:
            elements: An `iter` over elements used to initialize this `Heap`.
            to_comparable: A `callable` used to define the preorder used to sort
                elements pushed in this `Heap`.
        Example:
            heap = Heap([4, 2, 2, 1, 3], key=compare_to_key(lambda a, b: a >= b))
        """
        self.to_comparable = (
            to_comparable if to_comparable is not None
            else (lambda x: x)
        )
        self.index = 0
        if elements:
            # We could use this heapsort as defined in this link, but sorted() is stable
            # https://docs.python.org/3/library/heapq.html
            self._data = list(
                (self.to_comparable(element), i, element)
                for (i, element) in enumerate(elements)
            )
            # Note that self._data is not sorted.
            # https://stackoverflow.com/questions/1046683/does-pythons-heapify-not-play-well-with-list-comprehension-and-slicing
            heapq.heapify(self._data) # Or self._data = sorted(self._data)
            self.index = len(self._data) # Tie-break on insertion order.
        else:
            self._data = list()
    def push(self, element :object):
        heapq.heappush(self._data, (self.to_comparable(element), self.index, element))
        self.index += 1
    def decrease_key(self, element :object):
        for (i, (_, index, x)) in enumerate(self._data):
            if element == x:
                self._data[i] = (self.to_comparable(element), index, element)
                heapq.heapify(self._data)
    def pop(self) -> tuple:
        return heapq.heappop(self._data)[2]
    def __iter__(self) -> iter:
        return (x[2] for x in heapq.nsmallest(len(self), self._data))
    def __str__(self) -> str:
        return self.__repr__()
    def __repr__(self) -> str:
        return f"Heap({(list(self))})"
    def __bool__(self) -> bool:
        return bool(self._data)
    def __len__(self) -> int:
        return len(self._data)
