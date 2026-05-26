"""Unit tests for :mod:`libretro.api.netpacket`."""

from __future__ import annotations

import copy

from libretro.api import BROADCAST, NetpacketFlags, retro_netpacket_callback


def test_retro_netpacket_callback_defaults_all_null() -> None:
    cb = retro_netpacket_callback()
    assert not cb.start
    assert not cb.receive
    assert not cb.stop
    assert not cb.poll
    assert not cb.connected
    assert not cb.disconnected
    assert cb.protocol_version is None


def test_retro_netpacket_callback_kwarg_init() -> None:
    cb = retro_netpacket_callback(protocol_version=b"v1")
    assert cb.protocol_version == b"v1"


def test_retro_netpacket_callback_deepcopy() -> None:
    cb = retro_netpacket_callback(protocol_version=b"v1")
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert dup.protocol_version == cb.protocol_version


def test_netpacket_flags_values() -> None:
    assert NetpacketFlags.UNRELIABLE == 0
    assert NetpacketFlags.RELIABLE == 1
    assert NetpacketFlags.UNSEQUENCED == 2
    assert NetpacketFlags.FLUSH_HINT == 4


def test_broadcast_constant_is_uint16_max() -> None:
    assert BROADCAST == 0xFFFF
