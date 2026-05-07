# Contributing to libretro.py

This document tells you everything you need to know
to submit contributions to `libretro.py`.
It outlines steps for setting up your development environment
and guidelines for submitting pull requests.

# Getting Started

You can install everything you need to contribute to libretro.py with the following steps:

```bash
git clone https://github.com/JesseTG/libretro.py  # Clone the repository
cd libretro.py  # Enter the project directory
python -m venv ./venv  # Create a virtual environment where dependencies will be installed
pip install -v -e .  # Install the project in editable mode
```

Or, if you have `just` installed...

```bash
git clone https://github.com/JesseTG/libretro.py  # Clone the repository
cd libretro.py  # Enter the project directory
just install # Install libretro.py in editable mode and all its dependencies in the current environment
```

# Documentation Style

This section is the single source of truth for libretro.py's documentation style.
It applies to all docstrings,
to every reStructuredText file under [`docs/`](docs/),
and to every Markdown file in the repository
(where applicable).
It is intended for both human authors
and coding agents.

## Audience & Tone

libretro.py's intended audience primarily comprises:

- libretro core authors who use libretro.py as a Python test harness for their C/C++ core
- Python tooling authors who build libretro frontends, fuzzers, or analysis tools on top of it

The documentation may be read and contributed to
by users with different levels of proficiency in Python and C/C++,
so don't assume knowledge of advanced techniques in either language.

## Style

- Keep docstrings concise.
  Long-form architectural prose belongs in module-level docstrings
  on package `__init__.py` files,
  or in the narrative guide pages under [`docs/guide/`](docs/guide/).
- Follow the configured `ruff` linting rules for docstrings.
  Listen to what the linter tells you.

## libretro.h vs. libretro.py

- Although `libretro.h` is the canonical definition of libretro's behavior,
  the Python API defined by libretro.py should be
  treated as the primary subject for our purposes.
- When a Python symbol mirrors a C symbol,
  add a single short sentence of the form
  *"Corresponds to* :c:type:`retro_audio_callback` *in libretro.h."*
- Don't fabricate C counterparts for purely Python-side abstractions
  such as :class:`.Session`, :class:`.SessionBuilder`, or driver protocol classes.

## Syntax and Rendering

- All docstrings and narrative guides in [`docs/guide/`](docs/guide/) use reStructuredText, suitable for Sphinx.
- Use admonition **directives** — `.. note::`, `.. warning::`, `.. important::`, `.. seealso::` -  for callouts.
  Never use field-list aliases like `:note:`, `:warning:`, or `:value:`;
  Sphinx renders these as raw field labels rather than admonitions.
- Write `.. seealso::` with no space before the `::`.
  `.. seealso ::` (with a leading space) is non-canonical
  and inconsistent with every other directive in the codebase.
- Use the singular `:return:` and the plural `:raises:`.
  Avoid `:returns:` and `:raise:`;
  the former are minority spellings inherited from earlier conventions.
- Apply semantic line breaks per [sembr.org](https://sembr.org)
  in all docstrings, RST files, and Markdown files.
  Break after sentences and after independent clauses;
  do not break inside hyperlinks, hyphenated words, or inline code.

## Cross-References

- Cross-reference standard library types,
  [`moderngl`](https://moderngl.readthedocs.io/en/stable) types,
  and other libretro.py types via Sphinx roles.
  The existing `intersphinx_mapping` in [`docs/conf.py`](docs/conf.py)
  resolves them automatically.
- Default to the **short relative form for symbols defined in libretro.py**:
  `` :class:`.AudioDriver` ``,
  `` :meth:`.Core.run` ``,
  Every public symbol in libretro.py is re-exported under `libretro.*`,
  so the leading dot resolves unambiguously.
- Use the **tilde-prefixed full form** —
  `` :class:`~libretro.api.audio.retro_audio_callback` ``, `` :func:`copy.deepcopy` `` —
  when referring to a type from the standard library or a third-party library,
  when the relative form would be ambiguous across packages,
  or when a docstring needs to disambiguate two symbols with the same short name.
  Sphinx renders the tilde form as the bare symbol name,
  so the reader sees `retro_audio_callback` rather than the full dotted path.
- Never use bare backticks for symbol references —
  `` `AudioDriver` `` produces a default-role reference that breaks Sphinx cross-referencing
  in subtle ways.
  Reserve double backticks for inline literals
  that don't have an appropriate RST role.
- Use the [Sphinx C domain](https://www.sphinx-doc.org/en/master/usage/domains/c.html)
  when referring to symbols defined in `libretro.h`.


## Module Docstrings

- Every public module starts with a one-sentence summary of its purpose,
  as if completing the sentence "This module contains..."
- Every module's docstring includes at least one `.. seealso::` link
  to its companion module on the other side of the API/driver split:
  modules under `libretro.api` link to the matching `libretro.drivers.*` package and vice versa.
- Section-headed module docstrings —
  the kind that use `===` and `---` underlines —
  are reserved for package `__init__.py` files
  that establish broad conventions across an entire subpackage.
  See [`src/libretro/api/__init__.py`](src/libretro/api/__init__.py)
  and [`src/libretro/drivers/__init__.py`](src/libretro/drivers/__init__.py) for examples.
  All other modules use plain summary docstrings without section underlines.

## Class Docstrings

- Class docstrings start with a one-sentence summary in the indicative mood,
  as if completing the sentence "The most important thing this class does is..."
- After the one-sentence summary,
  a class docstring proceeds with a short paragraph describing
  lifecycle, threading model, or libretro phase constraints
  where any of those are non-obvious.
- For driver protocol classes
  (the `*Driver` classes in `libretro.drivers`),
  include a `.. seealso::` to the corresponding `libretro.api.*` module.
- For :class:`ctypes.Structure` subclasses that mirror libretro.h,
  include a `.. seealso::` to the corresponding `:c:type:`
  and a short *"Corresponds to … in libretro.h."* line.
- Document `__init__` parameters in the `__init__` docstring,
  not in the class docstring.
  Sphinx is configured with `autodoc_class_signature = "separated"`,
  so the two render together.

## Method and Function Docstrings

- Write summaries for method and function docstrings as a one-sentence summary
  in the imperative mood (*"Render a single..."*, not *"Renders a single..."*).
- An optional short paragraph describing libretro semantics —
  when the frontend would call this method,
  which libretro phase it belongs to,
  threading expectations,
  ownership of buffers passed across the boundary —
  written for a reader who already understands the C API.
- Document every parameter (`:param name:`),
  the return value (`:return:`),
  and every raised exception (`:raises ExceptionType:`).
  Driver methods that surface the `UnsupportedEnvCall` failure mode
  must declare it explicitly.
- Include a `.. seealso::` block linking to:
  the matching C callback type (e.g. :class:`.retro_audio_sample_t`),
  the matching environment-call constant where one exists,
  or the matching method on `Core` / `Session` for protocol methods.

## Doctests

- Include a doctest only when it demonstrates non-obvious behavior:
  round-tripping with `copy.deepcopy`,
  the sequence protocol on a struct that wraps a C array,
  ctypes marshalling of a tagged union.
  Skip doctests for plain constructor + assertion patterns.
- Doctests must be **connected to the surrounding prose**.
  Introduce them with a sentence ending in a colon,
  not as detached examples.
  See [`src/libretro/api/audio.py`](src/libretro/api/audio.py)
  for the canonical example of this pattern.
- Every doctest must pass under
  `python -m pytest --doctest-modules src/libretro`.

## Module-Level Constants and Type Aliases

- Every public module-level constant gets a docstring
  describing its meaning,
  its valid range or set of values,
  and the units where applicable
  (milliseconds, samples, bytes, etc.).
- Every public type alias gets a one-line docstring.
  When the alias resolves to a `ctypes` union,
  mention what kinds of Python values are convertible
  and under what conditions.
