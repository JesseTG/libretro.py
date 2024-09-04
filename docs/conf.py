# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "libretro.py"
copyright = "2024, Jesse Talavera"
author = "Jesse Talavera"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []
keep_warnings = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
# html_static_path = ["_static"]


# -- Options for autodoc extension -------------------------------------------

autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
autodoc_class_signature = "separated"  # Separate class and constructor signatures
autodoc_default_options = {
    "member-order": "bysource",
    "special-members": "__init__",  # Don't document any __dunder__ methods except these
    "undoc-members": True,  # Generate documentation for members without docstrings
    "inherited-members": "Protocol,int",  # Don't show inherited members from these classes
    "show-inheritance": True,  # Show the base class(es) of a class
    "members": True,
}
autosummary_generate = True

# -- Options for extlinks extension ------------------------------------------

extlinks = {"issue": ("https://github.com/JesseTG/libretro.py/issues/%s", "issue %s")}
extlinks_detect_hardcoded_links = True

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "moderngl": ("https://moderngl.readthedocs.io/en/stable", None),
}
