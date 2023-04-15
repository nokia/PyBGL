#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

import heapq

class Comparable(object):
    """
    Wrapper used to define a custom pre-order for a given object.

    This class is inspired from ``functools.cmp_to_key`` and
    `this discussion <https://stackoverflow.com/questions/8875706/heapq-with-custom-compare-predicate>`__. The objects to be sorted are wrapped in an instance
    that implements the ``<`` operator called by the sorting function.
    """
    def __init__(self, obj: object, preorder: callable = None):
        """
        Constructor.

        Example:
            >>> x = Comparable(5, lambda a, b: a >= b)

        Args:
            obj: An `Element` instance.
            preorder: A `callable` acting as a preorder.
        """
        self.obj = obj
        assert preorder
        self.preorder = preorder

    def __lt__(self, other: object) -> bool:
        """
        Implements the `<` comparison according to the chosen preorder.

        Args:
            other (object): The object compared to ``self``.

        Returns:
            ``True`` if ``self < other`` according to the chosen preorder.
        """
        return not self.preorder(other.obj, self.obj)

    def __le__(self, other: object) -> bool:
        """
        Implements the `<=` comparison according to the chosen preorder.

        Args:
            other (object): The object compared to ``self``.

        Returns:
            ``True`` if ``self <= other`` according to the chosen preorder.
        """
        return self.preorder(self.obj, other.obj)

    def __eq__(self, other: object) -> bool:
        """
        Implements the `==` comparison according to the chosen preorder.

        Args:
            other (object): The object compared to ``self``.

        Returns:
            ``True`` if ``self == other`` according to the chosen preorder.
        """
        return (
            self.preorder(self.obj, other.obj) and
            self.preorder(other.obj, self.obj)
        )

    def __ne__(self, other: object) -> bool:
        """
        Implements the `!=` comparison according to the chosen preorder.

        Args:
            other (object): The object compared to ``self``.

        Returns:
            ``True`` if ``self != other`` according to the chosen preorder.
        """
        return not self.__eq__(other)

    def __gt__(self, other: object) -> bool:
        """
        Implements the `>` comparison according to the chosen preorder.

        Args:
            other (object): The object compared to ``self``.

        Returns:
            ``True`` if ``self > other`` according to the chosen preorder.
        """
        return not self.preorder(self.obj, other.obj)

    def __ge__(self, other: object) -> bool:
        """
        Implements the `>=` comparison according to the chosen preorder.

        Args:
            other (object): The object compared to ``self``.

        Returns:
            ``True`` if ``self >= other`` according to the chosen preorder.
        """
        return self.preorder(other.obj, self.obj)

    def __str__(self) -> str:
        """
        Exports this :py:class:`Comparable` to its string representation.

        Returns:
            The corresponding string.
        """
        return "Comparable(%s)" % self.obj

    def __repr__(self) -> str:
        """
        Exports this :py:class:`Comparable` to its string representation.

        Returns:
            The corresponding string.
        """
        return "Comparable(%r)" % self.obj

def compare_to_key(preorder: callable):
    """
    Convert a preorder to a key callback (used e.g. by sort functions in python).

    Example:
        >>> key = compare_to_key(lambda a, b: a >= b)

    Args:
        preorder: A `callable(Element, Element)` that is preorder
            over the space of Elements.
    """
    return lambda x: Comparable(x, preorder)

class Heap:
    """
    The :py:class:`Heap` class implements a heap using an arbitrary preorder.
    It answers the limitation of :py:func:``heappop`` and :py:func:`heappush`
    which assume that the heap is ordered according to ``<=``.
    """
    def __init__(self, elements: iter = None, to_comparable: callable = None):
        """
        Constructor.

        Example:
            >>> heap = Heap(
            ...     [4, 2, 2, 1, 3],
            ...     to_comparable=lambda x: Comparable(x, lambda a, b: a >= b)
            ... )
            >>> heap
            Heap([4, 3, 2, 2, 1])

        Args:
            elements (iter): The elements used to initialize this `Heap`.
            to_comparable (callable): A `callable` used to define the preorder used to sort
                elements pushed in this `Heap`.
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

    def push(self, element: object):
        """
        Pushes an element to this :py:class:`Heap` instance.

        Args:
            element (object): The object to be pushed.
        """
        heapq.heappush(self._data, (self.to_comparable(element), self.index, element))
        self.index += 1

    def decrease_key(self, element: object):
        for (i, (_, index, x)) in enumerate(self._data):
            if element == x:
                self._data[i] = (self.to_comparable(element), index, element)
                heapq.heapify(self._data)

    def pop(self) -> tuple:
        """
        Pops an element to this :py:class:`Heap` instance.

        Returns:
            The popped element.
        """
        return heapq.heappop(self._data)[2]

    def __iter__(self) -> iter:
        """
        Retrieves an iterator over the stored objects.

        Returns:
            An iterator over the stored objects.
        """
        return (x[2] for x in heapq.nsmallest(len(self), self._data))

    def __str__(self) -> str:
        """
        Converts this :py:class:`Heap` instance to its string representation.

        Returns:
            The corresponding string representation.
        """
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Converts this :py:class:`Heap` instance to its string representation.

        Returns:
            The corresponding string representation.
        """
        return f"Heap({(list(self))})"

    def __bool__(self) -> bool:
        """
        Implements the :py:func:`bool` cast operation, typically used to check
        whether this :py:class:`Heap` instance is empty or not.

        Returns:
            ``True`` if this :py:class:`Heap` is not empty,
            ``False`` otherwise.
        """
        return bool(self._data)

    def __len__(self) -> int:
        """
        Implements the :py:func:`len` operation, used to count the number
        of elements stored in this :py:class:`Heap` instance.

        Returns:
            The number of stored elements.
        """
        return len(self._data)
