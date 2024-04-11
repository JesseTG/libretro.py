import os
import sys
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'libretro.py'
copyright = '2024, Jesse Talavera'
author = 'Jesse Talavera'

sys.path.insert(0, os.path.abspath(".."))
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.duration',
]

templates_path = ['_templates']
exclude_patterns = []
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': True,
    'undoc-members': True,
    'members': True,
}
autosummary_generate = ["index.rst"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

def source_read_handler(app, what, name, obj, options, signature, return_annotation):
    if what == 'module':
        print(f"{name}: {obj}")

def setup(app):
    app.connect('autodoc-process-signature', source_read_handler)