#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the pybgl project.
# https://github.com/nokia/pybgl

from collections import defaultdict

class PropertyMap:
    """
    The :py:class:`PropertyMap` expose the ``[]`` on top of an arbitrary object
    or function to map. They are used in pybgl to map a vertex or an edge
    with a given property. Hence, the property map class allows to decide how
    to organize the metadata related to a graph. One could decide to bundle
    the vertex properties (resp. properties) in a dedicated class or to use
    a default dictionary.

    An implemented property map must not raise an exception, in particular
    if they key is not found.
    """
    def __init__(self):
        """
        Constructor.
        """
        raise NotImplementedError(
            "PropertyMap is a virtual pure class. "
            "You must inherit ReadPropertyMap or ReadWritePropertyMap"
        )

    def __getitem__(self, k: object) -> object:
        """
        Method used to implement the ``[]`` operator (read access).

        Args:
            k (object): The key.

        Returns:
            The corresponding object or the default value.
        """
        raise NotImplementedError(
            "The PropertyMap class is a virtual pure. "
            "You must inherit ReadPropertyMap or ReadWritePropertyMap"
        )

    def __setitem__(self, k: object, v: object):
        """
        Sets the value related to a given key (write access).

        Args:
            k (object): The key.
            v (object): The new value.
        """
        raise NotImplementedError(
            "The PropertyMap class is a virtual pure. "
            "You must inherit ReadPropertyMap or ReadWritePropertyMap"
        )

    def __delitem__(self, k: object):
        """
        Delete a key from this :py:class:`PropertyMap` instance.
        """
        raise RuntimeError(
            "You are never supposed to delete a key from a PropertyMap"
        )

class ReadPropertyMap(PropertyMap):
    """
    The :py:class:`ReadPropertyMap` is the base class for any
    property map with read-only access.
    """
    def __init__(self):
        """
        Constructor.
        """
        raise NotImplementedError(
            "The ReadPropertyMap class is a virtual pure. "
            "You must inherit ReadPropertyMap and overload "
            "the __getitem__  method."
        )

    def __getitem__(self, k: object) -> object:
        """
        Method used to implement the ``[]`` operator (read access).

        Args:
            k (object): The key.

        Returns:
            The corresponding object or the default value.
        """
        raise NotImplementedError(
            "The ReadPropertyMap class is a virtual pure. "
            "You must inherit ReadPropertyMap and overload "
            "the __getitem__ method."
        )

    def __setitem__(self, k: object, v: object):
        """
        Sets the value related to a given key (write access).

        Args:
            k (object): The key.
            v (object): The new value.

        Raises:
            :py:class:`RuntimeError` as a :py:class:`ReadPropertyMap`
            is read-only.
        """
        raise RuntimeError("Setting a value in a ReadPropertyMap is not allowed.")

class FuncPropertyMap(ReadPropertyMap):
    """
    The :py:class:`FuncPropertyMap` is a :py:class:`ReadPropertyMap` which
    wraps a function.

    Use the :py:func:`make_func_property_map` function to create it.
    """
    def __init__(self, f: callable):
        """
        Constructor. You should never call it directly and use the
        :py:func:`make_func_property_map` instead.

        Args:
            f (callable): A function which takes a key in parameter and
                return the corresponding value.
        """
        self.m_f = f

    def __getitem__(self, k: object) -> object:
        """
        Overloads the :py:meth:`ReadPropertyMap.__getitem__` method.
        """
        return self.m_f(k)

def make_func_property_map(f: callable) -> FuncPropertyMap:
    """
    Makes a :py:class:`FuncPropertyMap` instance from a function.

    Example:
        >>> pmap = make_func_property_map(lambda x: x ** 2)
        >>> pmap[3]
        9

    Args:
        f (callable): A function which takes a key in parameter and
            return the corresponding value.

    Returns:
        The corresponding :py:class:`FuncPropertyMap` instance.
    """
    return FuncPropertyMap(f)

class IdentityPropertyMap(ReadPropertyMap):
    """
    The :py:class:`IdentityPropertyMap` is a :py:class:`ReadPropertyMap` which
    maps each key with itself.

    Use the :py:func:`identity_property_map` function to create it.
    """
    def __init__(self):
        """
        Constructor.
        """
        pass

    def __getitem__(self, k: object) -> object:
        """
        Overloads the :py:meth:`ReadPropertyMap.__getitem__` method.
        """
        return k

def identity_property_map():
    """
    Creates a :py:class:`IdentityPropertyMap` instance.

    Example:
        >>> pmap = identity_property_map()
        >>> pmap[10]
        10
    """
    return IdentityPropertyMap()

class ConstantPropertyMap(ReadPropertyMap):
    """
    The :py:class:`ConstantPropertyMap` is a :py:class:`ReadPropertyMap` which
    maps any key with a single same value.

    Use the :py:func:`make_constant_property_map` function to create it.
    """
    def __init__(self, value: object):
        """
        Constructor.

        Args:
            value (object): The only value that is returned by this
                :py:class:`ConstantPropertyMap` instance.
        """
        self.m_value = value

    def __getitem__(self, k: object) -> object:
        """
        Overloads the :py:meth:`ReadPropertyMap.__getitem__` method.
        """
        return self.m_value

def make_constant_property_map(value) -> ConstantPropertyMap:
    return ConstantPropertyMap(value)

class ReadWritePropertyMap(PropertyMap):
    """
    The :py:class:`ReadWritePropertyMap` is the base class for any
    property map with read and write access.

    See also the :py:class:`IdentityPropertyMap` and
    :py:class:`FuncPropertyMap` classes.
    """
    def __init__(self):
        """
        Constructor.
        """
        raise NotImplementedError(
            "The ReadPropertyMap class is a virtual pure. "
            "You must inherit ReadPropertyMap and overload "
            "the __getitem__  method."
        )

    def __getitem__(self, k: object) -> object:
        """
        Overloads the :py:meth:`ReadPropertyMap.__getitem__` method.
        """
        raise NotImplementedError(
            "The ReadWritePropertyMap class is a virtual pure. "
            "You must inherit ReadWritePropertyMap and overload "
            "the __getitem__ and __setitem__ methods."
        )


    def __setitem__(self, k: object, v: object):
        """
        Overloads the :py:meth:`ReadPropertyMap.__setitem__` method.
        """
        raise NotImplementedError(
            "The ReadWritePropertyMap class is a virtual pure. "
            "You must inherit ReadWritePropertyMap and overload "
            "the __getitem__ and __setitem__ methods."
        )

class AssocPropertyMap(ReadWritePropertyMap):
    """
    The :py:class:`AssocPropertyMap` is a :py:class:`ReadWritePropertyMap`
    wrapping a :py:class:`defaultdict`.

    Use the :py:func:`make_assoc_property_map` function to create it.
    """
    def __init__(self, d: defaultdict):
        """
        Constructor.

        Args:
            d (defaultdict): The underlying dictionary.
        """
        if not isinstance(d, defaultdict):
            raise TypeError(f"{d} is not a defaultdict instance: {type(d)}")
        self.m_d = d

    def __getitem__(self, k: object) -> object:
        """
        Overloads the :py:meth:`ReadWritePropertyMap.__getitem__` method.
        """
        return self.m_d[k]

    def __setitem__(self, k: object, v: object):
        """
        Overloads the :py:meth:`ReadWritePropertyMap.__setitem__` method.
        """
        self.m_d[k] = v

def make_assoc_property_map(d: defaultdict):
    """
    Makes an :py:class:`AssocPropertyMap` instance.

    Args:
        d (defaultdict): The underlying dictionnary. Do pass
            a :py:class:`defaultdict` instance, not
            a :py:class:`dict` instance.

    Example:
        >>> from collections import defaultdict
        >>> d = defaultdict(int)
        >>> d['a'] = 7
        >>> pmap = make_assoc_property_map(d)
        >>> pmap['a'])
        7
        >>> pmap['a'] = 8
        >>> print(pmap['a'])
        8
        >>> print(pmap['b'])
        0
    """
    return AssocPropertyMap(d)

def get(pmap: PropertyMap, k: object) -> object:
    """
    Retrieves the value related to a key from a property map.

    Args:
        pmap (PropertyMap): A property map.
        k (object): The key.

    Returns:
        The corresponding value or the default value of the
        property map.
    """
    return pmap[k]

def put(pmap: ReadWritePropertyMap, k: object, v: object):
    """
    Sets the value related to a key from a property map.

    Args:
        pmap (PropertyMap): A property map.
        k (object): The key.
        v (object): The new value.
    """
    pmap[k] = v
