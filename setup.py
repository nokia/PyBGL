#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Usage:
#     python3 setup.py install
#     python3 setup.py bdist_rpm

from setuptools import find_packages, setup

__version__        = (0, 9, 2)

README = ""
try:
    with open("README.rst") as f_readme:
        README = f_readme.read()
except:
    pass

HISTORY = ""
try:
    with open("HISTORY.rst") as f_history:
        HISTORY = f_history.read()
except:
    pass

LONG_DESCRIPTION = "%s\n\n%s" % (README, HISTORY)

# Copy is only triggered if the file does not yet exists.

setup(
    name             = "pybgl",
    version          = ".".join(["%s" % x for x in __version__]),
    description      = "pybgl",
    long_description = LONG_DESCRIPTION,
    author           = "Marc-Olivier Buob",
    author_email     = "marc-olivier.buob@nokia-bell-labs.com",
    url              = "http://github.com/nokia/pybgl",
    license          = "BSD-3",
    zip_safe         = False,
    packages         = ["pybgl"],
    package_dir      = {"pybgl" : "src"},
    requires         = ["typing"],
    test_suite       = "tests",
)
