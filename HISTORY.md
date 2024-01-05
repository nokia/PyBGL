## 0.0.1 (2018-09-12): First release

* Initial commit.

## 0.9.2 (2018-10-25)

* Added many graph structures and algorithms.

## 0.10.0 (2023-04-26)

* Added many language theory data structures and algorithms.
* Enabled CI.
* Improved documentation and tests.
* Improved code style (`flake8`).
* Progessively removing graph primitives function to remove every `import *`.

## 0.10.1 (2023-01-02)

* Migrated sphinx theme to pydata.
* Improved documentation, code style, `flake8` errors.
* Exposed some missing classes:
  * `DirectedGraph`;
  * `UndirectedGraph`;
  * `dotstr_to_html`;
  * `enrich_kwargs`;
  * `run_graphviz`;
  * `make_node_automaton`.
* Bug fix `*_copy`, `GraphView.*_degree`.
* The Graphviz-related function now correctly forward the kwargs arguments (e.g. `engine=`):
  * `ipynb_display_graph`;
  * `graph_to_html`;
  * `dotstr_to_html`;
  * `write_graphviz`;
  * `run_graphviz`.
* `pybgl.AssocPropertyMap` can now only wrap a `defaultdict` (not a `dict`).

## 0.10.2 (2023-01-02)

* Migrated from `bumpversion` to `poetry-bumpversion`.

## 0.10.3 (2023-01-05)

* Exposed additional symbols:
  * `BOTTOM`;
  * `EPSILON`;
  * `MAP_OPERATORS_ALG`;
  * `MAP_OPERATORS_RE`;
  * `compare_to_key`;
  * `RpnDequeAlg`;
  * `RpnDequeAst`;
  * `re_escape`;
  * `read_graphviz`.
* Bug fix:
  * `read_graphviz`;
  * `write_graphviz`;
  * `Trie.__init__` (kwargs forwarding).
* Flake8 tests/
* Improved documentation and tests.
* Cleaned the `revuz_minimize` function.
* Renamed attributes prefixed by `m_` and remove the corresponding properties.
* Improved the `make_*automaton` functions.
  * Renamed constructor argument to `Constructor`.
  * Bug fix for the empty automaton.
  * `pmap_vlabel` is now optional.
* Reverted from `poetry-bumpversion` to `bumpversion` (installation issues under debian).
