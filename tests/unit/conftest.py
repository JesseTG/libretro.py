"""
Pytest configuration shared by every unit test.

Unit tests run in-process (no ``isolated`` marker) because they don't load
libretro cores. They exercise the ``ctypes``-backed types in
``libretro.api`` and ``libretro.ctypes`` and complete in well under a
second each.
"""

from __future__ import annotations
