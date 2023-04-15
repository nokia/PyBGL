#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

class AggregatedVisitor:
    """
    The :py:class:`AggregatedVisitor` allows to pack several visitors
    to a given algorithm designed to take a (single) visitor in parameter.
    """
    def __init__(self, visitors: list = None):
        """
        Constructor.

        Args:
            visitors (list): A list of visitors exposing the same callbacks.
        """
        self.m_visitors = visitors if visitors else list()

    def __getattr__(self, method_name: str):
        """
        Handle call to a given callback and dispatch it to each
        nested visitor.

        Args:
            method_name (str): A string corresponding to the name of a
                method implemented in each nested visitor.
        """
        def wrapper(*args, **kwargs):
            for vis in self.m_visitors:
                getattr(vis, method_name)(*args)
        return wrapper

    @staticmethod
    def type_to_key(vis: object) -> str:
        """
        Builds the key corresponding to a visitor.

        Args:
            vis (object): A visitor instance.

        Returns:
            The corresponding key (built according to its type).
        """
        return str(type(vis)).split("'")[1]

    def keys(self) -> set:
        """
        Retrieves the set of keys identifying the visitors nested
        in this :py:class:`AggregatedVisitor` instance.

        Returns:
            The set of keys that could be used with self.get()
        """
        return {
            AggregatedVisitor.type_to_key(vis)
            for vis in self.m_visitors
        }

    def get(self, key: str, ret_if_not_found = None) -> object:
        """
        Retrieves a visitor identified by a given key from
        this :py:class:`AggregatedVisitor` instance.

        Args:
            key (str): The key identifying a visitor.
            ret_if_not_found: The value to be returned if not found.

        Returns:
            The corresponding visitor if found, ``None`` otherwise.
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
