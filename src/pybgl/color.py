#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

"""
This module provides utilities related to colors, handy to convert HTML color
(HSV, HSL...) to the corresponding `Graphviz color <https://graphviz.org/>`__.
This module is complementary to `colorsys <https://docs.python.org/2/library/colorsys.html>`__.
"""

def hsv_to_hsl(h: float, s: float, v: float) -> tuple:
    """
    Computes an
    `HSV to HSL color conversion <https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion>`__.

    Args:
        h (float): the hue, in [0.0, 1.0].
        s (float): the saturation, in [0.0, 1.0].
        v (float): the value, [0.0, 1.0].

    Returns:
        The corresponding HSL normalized tuple.
    """
    l = v * (1 - s / 2)
    s = 0 if l == 0 or l == 1 else (v - l) / min(l, 1 - l)
    return (h, s, l)

def hsl_to_hsv(h: float, s: float, l: float) -> tuple:
    """
    Computes an
    `HSL to HSV color conversion <https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion>`__.

    Args:
        h (float): the hue, in [0.0, 1.0].
        s (float): the saturation, in [0.0, 1.0].
        l (float): the light, [0.0, 1.0].

    Returns:
        The corresponding HSv normalized tuple.
    """
    v = l + s * min(l, 1 - l)
    s = 0 if v == 0 else 2 * (1 - l/v)
    return (h, s, v)

def normalize_color_tuple(h: int, s: int, x: int) -> tuple:
    """
    Normalizes an HSV or HSL tuple.

    Args:
        h (int): The hue, in {0, ..., 360}.
        s (int): The saturation, in {0, ..., 100}.
        x (int): The value or the light, {0, ..., 100}.

    Returns:
        The corresponding normalized tuple.
    """
    return (h / 360, s / 100, x / 100)

#TODO rename to html_color_to_graphviz
def html_to_graphviz(color: str) -> str:
    """
    HTML to Graphviz color conversion.

    Args:
        color (str): An HTML color. `Examples:` ``"#40e0d0"``, ``"turquoise"``,
            ``"hsl(173, 71%, 56%)"``.

    Returns:
        The corresponding graphviz color. This is exactly ``color`` if it does not
        start with hsl.
    """
    if color.startswith("hsl"):
        j = color.find("(")
        k = color.rfind(")")
        (h, s, l) = [
            int(val.replace("%", ""))
            for val in color[j+1:k].split(",")
        ]
        (h, s, v) = hsl_to_hsv(*normalize_color_tuple(h, s, l))
        return ", ".join([
            str(x)
            for x in (h, s, v)
        ])
    else:
        return color
