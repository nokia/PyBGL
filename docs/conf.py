#!/usr/bin/env python
#
# Documentation build configuration file, based on the output of
# sphinx-quickstart
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
import pybgl

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.

needs_sphinx = "1.4"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "sphinx.ext.viewcode",
    "sphinx_mdinclude",  # https://pypi.org/project/sphinx_mdinclude/
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
]

# https://github.com/JamesALeedham/Sphinx-Autosummary-Recursion/blob/master/docs/conf.py
# Turn on sphinx.ext.autosummary
autosummary_generate = True
# Add __init__ doc (ie. params) to class summaries
autoclass_content = "both"
# Pass False to remove 'view source code' of the rst.
html_show_sourcelink = False
# If no docstring, inherit from base class
autodoc_inherit_docstrings = True
# Enable 'expensive' imports for sphinx_autodoc_typehints
set_type_checking_flag = True
# Continue through Jupyter errors
nbsphinx_allow_errors = True
# Sphinx-native method. Not as good as sphinx_autodoc_typehints
# autodoc_typehints = "description"
# Remove namespaces from class/method signatures
add_module_names = False


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = [".rst", ".md"]
source_suffix = [".rst", ".md", ".ipynb"]

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "pybgl"
doc_title = project + " documentation"
module_name = "pybgl"
copyright = "2024, Nokia"
author = "Marc-Olivier Buob"
description = (
    "PyBGL is a pure python3 graph library inspired from the BGL "
    "(Boost Graph Library). It gathers algorithms from the graph "
    "theory, language theory and dynamic programming background."
)
category = ""

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = pybgl.__version__
# The full version, including alpha/beta/rc tags.
release = pybgl.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "modules.rst"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# See https://sphinx-copybutton.readthedocs.io/en/latest/use.html
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "alabaster"
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/nokia/pybgl",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/pybgl",
            "icon": "fa-custom fa-pypi",
        },
    ],
    "header_links_before_dropdown": 5,
    "show_nav_level": 2,
    "show_toc_level": 2,
    "navigation_depth": 2,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]


# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = module_name + "_doc"


# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ("letterpaper" or "a4paper").
    #
    # "papersize": "letterpaper",

    # The font size ("10pt", "11pt" or "12pt").
    #
    # "pointsize": "10pt",

    # Additional stuff for the LaTeX preamble.
    #
    # "preamble": "",

    # Latex figure (float) alignment
    #
    # "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        module_name + ".tex",
        doc_title,
        author,
        "manual"
    ),
]


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        master_doc,
        module_name,
        doc_title,
        [author],
        1
    )
]


# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        module_name,
        doc_title,
        author,
        module_name,
        description,
        category
    ),
]
