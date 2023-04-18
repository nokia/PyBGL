#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

import sys

INFINITY = sys.maxsize

class BinaryRelation:
    """
    :py:class:`BinaryRelation` is the base class to implement
    a functor wrapping a binary relation.
    """
    def __call__(self, x: object, y: object) -> bool:
        """
        Fonctor method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``True`` if x and y satisfy the wrapped binary relation.
        """
        raise NotImplementedError()

class Less(BinaryRelation):
    """
    :py:class:`Less` is the functor that wraps the ``<``
    binary relation.
    """
    def __call__(self, x: object, y: object) -> bool:
        """
        Fonctor method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``True`` if ``x < y``, ``False`` otherwise.
        """
        return x < y

class GreaterThan(BinaryRelation):
    """
    :py:class:`Less` is the functor that wraps the ``>``
    binary relation.
    """
    def __call__(self, x, y) -> bool:
        """
        Fonctor method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``True`` if ``x > y``, ``False`` otherwise.
        """
        return x > y

class BinaryOperator:
    """
    :py:class:`BinaryOperator` is the base class to implement
    a functor wrapping a binary operator.
    """
    pass

class ClosedOperator(BinaryOperator):
    def __init__(self, absorbing: object):
        """
        Constructor.

        Args:
            absorbing (object): The object representing the absorbing
                for this binary operation.
        """
        self.absorbing = absorbing

    def impl(self, x: object, y: object) -> object:
        """
        Implementation method. Must be overladed.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``True`` if ``x < y``, ``False`` otherwise.
        """
        raise NotImplementedError()

    def __call__(self, x: object, y: object) -> object:
        """
        Fonctor method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``self.impl(x, y)`` if ``x`` and ``y`` are not :py:attr:`self.absorbing`,
            :py:attr:`self.absorbing` otherwise.
        """
        return self.absorbing if x == self.absorbing or y == self.absorbing else self.impl(x, y)

class ClosedPlus(ClosedOperator):
    """
    :py:class:`BinaryOperator` is the base class to implement
    a ``+`` operator in ``(R^+, +)`` group.
    """
    def __init__(self, absorbing: float = INFINITY):
        """
        Constructor.

        Args:
            absorbing (object): The absorbing of ``+``.
        """
        super().__init__(absorbing)

    def impl(self, x: float, y: float) -> object:
        """
        Implementation method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``x + y`` if ``x`` and ``y`` are not :py:attr:`self.absorbing`,
            :py:attr:`self.absorbing` otherwise.
        """
        return x + y

class ClosedTime(ClosedOperator):
    """
    :py:class:`BinaryOperator` is the base class to implement
    a ``*`` operator in ``([0, 1], *)`` group.
    """
    def __init__(self, absorbing: float = INFINITY):
        """
        Constructor.

        Args:
            absorbing (object): The absorbing of ``*``.
        """
        super().__init__(absorbing)

    def impl(self, x: object, y: object) -> object:
        """
        Implementation method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``x * y`` if ``x`` and ``y`` are not :py:attr:`self.absorbing`,
            :py:attr:`self.absorbing` otherwise.
        """
        return x * y

class ClosedMax(ClosedOperator):
    """
    :py:class:`BinaryOperator` is the base class to implement
    a ``max`` operator in (R^+, max) group.
    """
    def __init__(self, absorbing: float = INFINITY):
        """
        Constructor.

        Args:
            absorbing (object): The absorbing of ``max``.
        """
        super().__init__(absorbing)

    def impl(self, x: object, y: object) -> object:
        """
        Implementation method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``max(x, y)`` if ``x`` and ``y`` are not :py:attr:`self.absorbing`,
            :py:attr:`self.absorbing` otherwise.
        """
        return max(x, y)

class ClosedMin(ClosedOperator):
    """
    :py:class:`BinaryOperator` is the base class to implement
    a ``min`` operator in ``([0, 1], min)`` group.
    """
    def __init__(self, absorbing: float = 0):
        """
        Constructor.

        Args:
            absorbing (object): The absorbing of ``min``.
        """
        super().__init__(absorbing)

    def impl(self, x: object, y: object) -> object:
        """
        Implementation method.

        Args:
            x (object): The left operand.
            y (object): The right operand.

        Returns:
            ``min(x, y)`` if ``x`` and ``y`` are not :py:attr:`self.absorbing`,
            :py:attr:`self.absorbing` otherwise.
        """
        return min(x, y)
