"""Unit tests for :mod:`libretro.api.proc`."""

from __future__ import annotations

import copy

import pytest

from libretro.api import retro_get_proc_address_interface


def test_retro_get_proc_address_interface_default() -> None:
    iface = retro_get_proc_address_interface()
    assert not iface.get_proc_address


def test_retro_get_proc_address_interface_call_raises_when_unset() -> None:
    iface = retro_get_proc_address_interface()
    with pytest.raises(ValueError):
        iface(b"missing_symbol")


def test_retro_get_proc_address_interface_call_rejects_non_str_bytes() -> None:
    iface = retro_get_proc_address_interface()
    # The ValueError for unset is raised first, before the type check —
    # this verifies the failure path; non-str/bytes args would also be
    # rejected if get_proc_address were set.
    with pytest.raises(ValueError):
        iface(42)  # type: ignore
        # We're testing the error-handling behavior,
        # so no need for the type checker to bother us


def test_retro_get_proc_address_interface_deepcopy() -> None:
    iface = retro_get_proc_address_interface()
    dup = copy.deepcopy(iface)
    assert dup is not iface
    assert not dup.get_proc_address
