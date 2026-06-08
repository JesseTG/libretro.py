"""Compatibility shims for features that depend on the running Python version."""

import sys

if sys.version_info >= (3, 13):
    from typing import TypeVar
    from warnings import deprecated
else:
    # typing.TypeVar gained PEP 696 ``default`` support in 3.13;
    # fall back to the backport on older interpreters.
    from typing_extensions import TypeVar, deprecated

__all__ = ("TypeVar", "deprecated")
