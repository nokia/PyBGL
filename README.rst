PyBGL
==============

.. _git: https://github.com/nokia/pybgl.git 
.. _wiki: https://github.com/nokia/pybgl/wiki
.. _BGL: https://www.boost.org/doc/libs/1_69_0/libs/graph/doc/
.. python3: http://python.org/

==================
Overview
==================

PyBGL is a pure python graph library inspired from the BGL_ (Boost Graph Library).

For more information, visit the wiki_.

==================
Dependencies
==================

PyBGL requires python3_.

For example, under Debian-based distribution, run:

.. code:: shell

  sudo apt-get update
  sudo apt-get install python3

==================
Installation steps
==================
From sources
------------------

- The sources are available on git_.

.. code:: shell

  mkdir ~/git
  cd ~/git
  git clone https://github.com/nokia/pybgl.git
  cd pybgl
  python3 setup.py build
  sudo python3 setup.py install

==================
Testing
==================

1. Test scripts are provided in ``tests/`` directory.
2. Install ``python3-pytest``. 
3. Run tests as follows:

.. code:: shell

  cd ~/git/pybgl/tests/
  pytest-3

==================
Packaging
==================

Install the packages needed to build ``.rpm`` and ``.deb`` packages:

- ``python3-setuptools``
- ``python3-stdeb`` for ``.deb`` packages
- ``rpm`` for ``.rpm`` packages

For example, under Debian-based distribution, run:

.. code:: shell

  sudo apt-get update
  sudo apt-get install python3-setuptools python3-stdeb rpm

To build ``.rpm`` package (in ``dist/``), run:

.. code:: shell

  cd ~/git/pybgl/tests/
  python3 setup.py bdist_rpm

To build ``.deb`` package (in ``deb_dist/``), run:

.. code:: shell

  python3 setup.py --command-packages=stdeb.command bdist_deb

