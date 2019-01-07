#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Jupyter ipython notebook utilities.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

from pybgl.html                 import html
from pybgl.graphviz             import dotstr_to_html

def in_ipynb() -> bool:
    """
    Tests whether the code is running inside a Jupyter Notebook.
    Returns:
        True iff the code is running inside a Jupyter Notebook.
    """
    try:
        return str(type(get_ipython())) == "<class 'ipykernel.zmqshell.ZMQInteractiveShell'>"
    except NameError:
        return False

def ipynb_display_graph(g):
    """
    Display a Graph in a Jupyter Notebook.
    """
    html(dotstr_to_html(g.to_dot()))

def display_svg(svg, filename_svg):
    with open(filename_svg, "w") as f:
        print(svg, file = f)
        html("<a href='%s' target='_blank'>View</a>" % filename_svg)
    html(svg)


