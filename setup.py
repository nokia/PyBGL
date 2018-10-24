#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Usage:
#     python3 setup.py install
#     python3 setup.py bdist_rpm
#

import os
from platform   import dist
from setuptools import find_packages, setup

__version__ = (0, 9, 2)

distribution, _, _ = dist()
ROOT_PATH          = os.path.abspath(os.path.dirname(__file__))
long_description   = open(os.path.join(ROOT_PATH, "README.rst")).read()
setup(
    name             = "pybgl",
    version          = ".".join(["%s" % x for x in __version__]),
    description      = "pybgl",
    long_description = long_description,
    author           = "Marc-Olivier Buob",
    author_email     = "marc-olivier.buob@nokia-bell-labs.com",
    url              = "https://github.com/nokia/PyBGL",
    license          = "BSD-3",
    zip_safe         = False,
    packages         = find_packages(),
    package_dir      = {'pybgl' : 'pybgl'},
    # Those python modules must be manually installed using easy_install
    #install_requires = ["cfgparse"],
    options = {
        'bdist_rpm':{
            'post_install'      : 'post_install',
            'post_uninstall'    : 'post_uninstall'
        }
    },
)
