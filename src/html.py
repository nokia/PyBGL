#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# HTML utilities.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

def html(s :str):
    """
    Evaluate HTML code in a Jupyter Notebook.
    Args:
        s: A str containing HTML code.
    """
    from IPython.display import display, HTML
    chart = HTML(s)
    # or chart = charts.plot(...)
    display(chart)

def beside(contents1 :str, contents2 :str, title :str = "", title1 :str = "", title2 :str = "") -> str:
    """
    Export two HTML contents so that they are displayed beside.
    Args:
        contents1: A `str` containing the content displayed on the right.
        contents2: A `str` containing the content displayed on the left.
        title: A `str` containing the title of the figure.
        title1: A `str` containing the caption of the left content.
        title2: A `str` containing the caption of the right content.
    Returns:
        The corresponding HTML `str` instance.
    """
    return """
        %(title)s
        <div style="display: table; width:100%%">
            <div style="display: table-row">
                <div style="width: 50%%; padding: 2%%; display: table-cell;">
                    <b>%(title1)s</b>
                    <pre>%(contents1)s</pre>
                </div>
                <div style="width: 50%%; padding: 2%%; display: table-cell;">
                    <b>%(title2)s</b>
                    <pre>%(contents2)s</pre>
                </div>
            </div>
        </div>
        """ % {
            "title"     : title,
            "title1"    : title1,
            "title2"    : title2,
            "contents1" : contents1,
            "contents2" : contents2
        }
