#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

"""
This module provides utilities related to colors, handy to convert HTML color
(HSV, HSL...) to the corresponding `Graphviz color <https://graphviz.org/>`__.
This module is complementary to
`colorsys <https://docs.python.org/2/library/colorsys.html>`__.
"""


def hsv_to_hsl(hue: float, saturation: float, value: float) -> tuple:
    """
    Computes an
    `HSV to HSL color conversion
    <https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion>`__.

    Args:
        hue (float): The hue, in [0.0, 1.0].
        saturation (float): The saturation, in [0.0, 1.0].
        value (float): The value, [0.0, 1.0].

    Returns:
        The corresponding HSL normalized tuple.
    """
    lightness = value * (1 - saturation / 2)
    saturation = (
        0 if lightness == 0 or lightness == 1
        else (value - lightness) / min(lightness, 1 - lightness)
    )
    return (hue, saturation, lightness)


def hsl_to_hsv(hue: float, saturation: float, lightness: float) -> tuple:
    """
    Computes an
    `HSL to HSV color conversion
    <https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion>`__.

    Args:
        hue (float): The hue, in [0.0, 1.0].
        saturation (float): The saturation, in [0.0, 1.0].
        lightness (float): The lightness, [0.0, 1.0].

    Returns:
        The corresponding HSV normalized tuple.
    """
    value = lightness + saturation * min(lightness, 1 - lightness)
    saturation = (
        0 if value == 0
        else 2 * (1 - lightness / value)
    )
    return (hue, saturation, value)


def normalize_color_tuple(hue: int, saturation: int, x: int) -> tuple:
    """
    Normalizes an HSV or HSL tuple.

    Args:
        hue (int): The hue, in {0, ..., 360}.
        saturation (int): The saturation, in {0, ..., 100}.
        x (int): The value or the lightness, {0, ..., 100}.

    Returns:
        The corresponding normalized tuple.
    """
    return (hue / 360, saturation / 100, x / 100)


def html_color_to_graphviz(color: str) -> str:
    """
    HTML to Graphviz color conversion.

    Args:
        color (str): An HTML color. `Examples:` ``"#40e0d0"``, ``"turquoise"``,
            ``"hsl(173, 71%, 56%)"``.

    Returns:
        The corresponding graphviz color. This is exactly
        ``color`` if it does not start with hsl.
    """
    if color.startswith("hsl"):
        j = color.find("(")
        k = color.rfind(")")
        (hue, saturation, lightness) = [
            int(x.replace("%", ""))
            for x in color[j + 1: k].split(",")
        ]
        (hue, saturation, value) = hsl_to_hsv(
            *normalize_color_tuple(hue, saturation, lightness)
        )
        return ", ".join([
            str(x)
            for x in (hue, saturation, value)
        ])
    else:
        return color
