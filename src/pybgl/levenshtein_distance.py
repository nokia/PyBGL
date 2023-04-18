#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

def levenshtein_distance_naive(x :str, y :str) -> int:
    """
    Inefficient implementation of the
    `Levenshtein distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`__
    (no memoization).
    Prefer the :py:func:`levenshtein_distance` function.

    Args:
        x (str): The left operand.
        y (str): The right operand.

    Returns:
        The minimal number of insertion/deletion/substitution operations needed to
        transform `x` into `y`.
    """
    x_1 = x[1:]
    y_1 = y[1:]
    return (
        len(x) if not y else
        len(y) if not x else
        levenshtein_distance(x_1, y_1) if x[0] == y[0] else
        1 + min(
            levenshtein_distance(x_1, y),
            levenshtein_distance(x, y_1),
            levenshtein_distance(x_1, y_1),
        )
    )

class LevenshteinDistance:
    """
    The :py:class:`LevenshteinDistance` class is used to implement the memoization
    used by the :py:func:`levenshtein_distance` function.
    """
    def __init__(self, x: str, y: str):
        """
        Constructor.

        Args:
            x (str): The left operand.
            y (str): The right operand.
        """
        self.memoize = dict()
        self.x = x
        self.y = y

    def compute(self, i: int = 0, j: int = 0) -> int:
        """
        Computes the `Levenshtein distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`__, with memoization.

        Args:
            i (int): The current index in ``self.x``.
            j (int): The current index in ``self.y``.

        Returns:
            The minimal number of insertion/deletion/substitution operations needed to
            transform ``x`` into ``y``.
        """
        ret = self.memoize.get((i, j))
        if ret is None:
            ret = self.memoize[(i, j)] = (
                len(self.x) - i if not j < len(self.y) else
                len(self.y) - j if not i < len(self.x) else
                self.compute(i + 1, j + 1) if self.x[i] == self.y[j] else
                1 + min(
                    self.compute(i + 1, j),
                    self.compute(i, j + 1),
                    self.compute(i + 1, j + 1),
                )
            )
        return ret

def levenshtein_distance(x: str, y: str) -> int:
    """
    Computes the
    `Levenshtein distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`__,
    with memoization.

    Args:
        x (str): The left operand.
        y (str): The right operand.

    Returns:
        The minimal number of insertion/deletion/substitution operations needed to
        transform `x` into `y`.
    """
    return LevenshteinDistance(x, y).compute(0, 0)
