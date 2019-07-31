#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Class allowing to aggregate a list of compatible visitors
# into a single visitor.
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

__author__     = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__      = "marc-olivier.buob@nokia-bell-labs.com"
__copyright__  = "Copyright (C) 2018, Nokia"
__license__    = "BSD-3"

class AggregatedVisitor:
    def __init__(self, visitors = list()):
        """
        Constructor.
        Args:
            visitors: A list of visitors exposing the same callbacks.
        """
        self.m_visitors = visitors

    def __getattr__(self, method_name :str):
        """
        Handle call to a given callback and dispatch it to each
        nested visitor.
        Args:
            method_name: A string corresponding to the name of a
                method implemented in each nested visitor.
        """
        def wrapper(*args, **kwargs):
            for vis in self.m_visitors:
                getattr(vis, method_name)(*args)
        return wrapper

    @staticmethod
    def type_to_key(vis):
        return ("%s" % type(vis)).split("'")[1]

    def keys(self) -> set:
        """
        Returns:
            The set of keys that could be used with self.get()
        """
        return {AggregatedVisitor.type_to_key(vis) for vis in self.m_visitors}

    def get(self, key, ret_if_not_found = None):
        """
        Retrieve a specific visitor.
        """
        for vis in self.m_visitors:
            if AggregatedVisitor.type_to_key(vis) == key:
                return vis
        print(
            "AggregatedVisitor: key %s not found: valid keys are: %s" % (
                key,
                {"%s" % AggregatedVisitor.type_to_key(vis) for vis in self.m_visitors}
            )
        )
        return ret_if_not_found
