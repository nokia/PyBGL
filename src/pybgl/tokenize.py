#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

class TokenizeVisitor:
    def on_unmatched(self, unmatched :str, start :int, end :int, s :str): pass
    def on_matched(self, matched :str, start :int, end :int, s :str): pass

def tokenize(tokenizer, s :str, vis :TokenizeVisitor = None):
    """
    Regexp-based string tokenizer. Useful to parse string
    when processing involve multiple regular expressions.
    See e.g. pybgl.graphiz.escape_html.
    """
    if vis is None:
        vis = TokenizeVisitor()
    start = 0
    for match in tokenizer.finditer(s):
        end = match.start()
        unmatched = s[start:end]
        if unmatched:
            vis.on_unmatched(unmatched, start, end, s)
        matched = match.group(0)
        if matched:
            vis.on_matched(matched, match.start(), match.end(), s)
        start = match.end()
    remaining = s[start:]
    if remaining:
        vis.on_unmatched(remaining, start, None, s)
