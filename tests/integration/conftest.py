"""
Pytest fixtures and configuration shared by every integration test.

Every test in ``tests/integration/`` runs in a fresh subprocess via
``pytest-isolated`` so that loading and unloading a libretro core (which
involves global C state inside the loaded shared library) never bleeds
between tests.

Integration tests follow a single pattern: load a real compiled sample
core, wire it to the libretro.py drivers under test through a
:class:`~libretro.session.Session`, run a few frames, then assert on what
the drivers observed. libretro.py *is* the mock, so nothing here is faked.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from libretro.core import Core


def pytest_collection_modifyitems(items: Iterable[pytest.Item]) -> None:
    """Apply ``@pytest.mark.isolated`` to every test collected from this package."""
    isolated = pytest.mark.isolated
    for item in items:
        item.add_marker(isolated)


type SampleCoreLoader = Callable[[str, str], "Core"]


@pytest.fixture
def load_core() -> SampleCoreLoader:
    """
    Return a loader that resolves a bundled sample core by ``(category, name)``.

    The loader skips the test (rather than failing) when the sample core
    isn't bundled on the running platform — for example, the OpenGL cores
    on a headless Windows MSVC build, or every core on the
    ``py3-none-any`` fallback wheel.
    """

    def _load(category: str, name: str) -> Core:
        module = pytest.importorskip(f"libretro.samples.{category}")
        try:
            return getattr(module, name)
        except ImportError as exc:
            pytest.skip(f"Sample core libretro.samples.{category}.{name} unavailable: {exc}")

    return _load
