# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "libretro.py"

author = "Jesse Talavera"
copyright = f"2024-%Y {author}"
# It me

manpages_url = "https://man7.org/linux/man-pages/man{section}/{page}.{section}.html"
# To allow cross-references to man pages

toc_object_entries_show_parents = "hide"
# Just show method/field names on the right sidebar instead of the whole name (it looks nicer)

python_display_short_literal_types = True
# "A" | "B" | "C" looks nicer than Literal["A", "B", "C"]

add_module_names = False
modindex_common_prefix = ["libretro.", "libretro.api.", "libretro.drivers."]
# The modules all start with "libretro.something",
# using the full path everywhere is too verbose

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.prettyspecialmethods",
    "sphinx_click",
]

templates_path = ["_templates"]
keep_warnings = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]


# -- Options for autodoc extension -------------------------------------------

autodoc_typehints = "none"
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
autodoc_class_signature = "separated"  # Separate class and constructor signatures
autodoc_default_options = {
    "member-order": "bysource",
    "special-members": "__init__,__call__,__getitem__,__setitem__,__delitem__,__iter__,__enter__,__exit__,__deepcopy__,__copy__,__len__,__contains__,__del__",  # Don't document any __dunder__ methods except these
    "undoc-members": True,  # Generate documentation for members without docstrings
    "inherited-members": "Protocol,int",  # Don't show inherited members from these classes
    "show-inheritance": True,  # Show the base class(es) of a class
    "members": True,
}
autosummary_generate = True

# -- Options for extlinks extension ------------------------------------------

extlinks = {
    "python-issue": ("https://github.com/python/cpython/issues/%s", "Python issue %s"),
    "issue": ("https://github.com/JesseTG/libretro.py/issues/%s", "issue %s"),
}
extlinks_detect_hardcoded_links = True

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "moderngl": ("https://moderngl.readthedocs.io/en/stable", None),
}

nitpick_ignore_regex = {
    ("c:.*", "(retro|RETRO)_.+"),
}
# We don't have an intersphinx mapping for libretro.h's API docs,
# so cross-references won't work right now.
