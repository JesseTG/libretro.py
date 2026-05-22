"""
Shared helpers that resolve sample-core names to on-disk shared libraries.

Each subpackage of :mod:`libretro.samples` re-exports the sample cores
in its category through a module-level ``__getattr__`` that delegates here.
Cores are loaded on first access and cached for the lifetime of the process.
"""

from __future__ import annotations

import importlib
import sys
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libretro.core import Core


def _shared_library_suffix() -> str:
    """
    Return the shared-library suffix for the current platform,
    including the leading dot.

    :return: ``".dll"`` on Windows, ``".dylib"`` on macOS, ``".so"`` elsewhere.
    """
    if sys.platform == "win32":
        return ".dll"
    if sys.platform == "darwin":
        return ".dylib"
    return ".so"


def _locate(category: str, name: str) -> Path | None:
    """
    Search the :obj:`__path__` of ``libretro.samples.<category>`` for the shared
    library that backs the named sample core.

    :param category: One of ``audio``, ``input``, ``midi``, ``tests``, ``video``, ``custom``.
    :param name: The bare core name without the ``_libretro`` suffix or extension.
    :return: The first matching path, or :obj:`None` if no candidate exists.
    """
    filename = f"{name}_libretro{_shared_library_suffix()}"
    package = importlib.import_module(f"libretro.samples.{category}")
    # Editable installs of scikit-build-core projects extend ``__path__`` with
    # both the source tree and the install directory containing the compiled
    # artifacts; ``importlib.resources.files`` only returns the first entry,
    # so we look at the package's own ``__path__`` to multiplex across both.
    for root in package.__path__:
        candidate = Path(root) / filename
        if candidate.is_file():
            return candidate
    return None


@cache
def load_sample_core(category: str, name: str) -> Core:
    """
    Return the :class:`~libretro.core.Core` for the named sample,
    loading the underlying shared library on first call and caching the result.

    :param category: One of ``audio``, ``input``, ``midi``, ``tests``, ``video``, ``custom``.
    :param name: The bare core name (no ``_libretro`` suffix or extension).
    :return: A loaded :class:`~libretro.core.Core` ready for use.
    :raises ImportError: If the underlying shared library is not bundled with
        the installed wheel — for example,
        when libretro.py was installed from the ``py3-none-any`` fallback wheel,
        or on a platform we haven't built cores for.
    """
    from libretro.core import Core  # local import avoids a cycle with libretro.samples

    path = _locate(category, name)
    if path is None:
        filename = f"{name}_libretro{_shared_library_suffix()}"
        raise ImportError(
            f"Sample core 'libretro.samples.{category}.{name}' is not bundled "
            f"with this libretro.py installation "
            f"(looked for {filename} alongside libretro/samples/{category}/). "
            f"Install a platform-specific libretro.py wheel that includes "
            f"the sample cores for {sys.platform}.",
            name=f"libretro.samples.{category}.{name}",
        )

    return Core(path)
