#!/usr/bin/env pytest-3
# -*- coding: utf-8 -*-

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2020, Nokia"
__license__    = "BSD-3"

from pybgl.graphviz import graphviz_escape_html

def test_graphviz_escape_html():
    assert graphviz_escape_html("<table><tr><td>foo</td></tr></table>") == "<table><tr><td>foo</td></tr></table>"
    assert graphviz_escape_html("<b>foo</b>") == "<b>foo</b>"
    assert graphviz_escape_html("<") == "&#60;"
    assert graphviz_escape_html(">") == "&#62;"
    assert graphviz_escape_html("\n") == "\\n"
    assert graphviz_escape_html("\t") == "\\t"
    assert graphviz_escape_html("[") == "&#91;"
    assert graphviz_escape_html("]") == "&#93;"
    assert graphviz_escape_html("{") == "&#123;"
    assert graphviz_escape_html("}") == "&#125;"
    assert graphviz_escape_html("<foo>") == "&#60;foo&#62;"
    assert graphviz_escape_html("<b>foo</b><bar>") == "<b>foo</b>&#60;bar&#62;"
