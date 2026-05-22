"""
Pytest fixtures and configuration shared by every integration test.

Every test in ``tests/integration/`` runs in a fresh subprocess via
``pytest-isolated`` so that loading and unloading a libretro core (which
involves global C state inside the loaded shared library) never bleeds
between tests.
"""

from __future__ import annotations

from collections.abc import Iterable

import pytest


def pytest_collection_modifyitems(items: Iterable[pytest.Item]) -> None:
    """Apply ``@pytest.mark.isolated`` to every test collected from this package."""
    isolated = pytest.mark.isolated
    for item in items:
        item.add_marker(isolated)
