"""Unit tests for :mod:`libretro.api.microphone`."""

from __future__ import annotations

import copy

from libretro.api.microphone import (
    INTERFACE_VERSION,
    retro_close_mic_t,
    retro_get_mic_params_t,
    retro_get_mic_state_t,
    retro_microphone,
    retro_microphone_interface,
    retro_microphone_params,
    retro_open_mic_t,
    retro_read_mic_t,
    retro_set_mic_state_t,
)


def test_retro_microphone_handle_kwarg_init() -> None:
    mic = retro_microphone(id=0xDEADBEEF)
    assert mic.id == 0xDEADBEEF


def test_retro_microphone_handle_default_id_is_zero() -> None:
    mic = retro_microphone()
    assert mic.id == 0


def test_retro_microphone_params_kwarg_init() -> None:
    p = retro_microphone_params(rate=48000)
    assert p.rate == 48000


def test_retro_microphone_params_deepcopy() -> None:
    p = retro_microphone_params(rate=22050)
    dup = copy.deepcopy(p)
    assert dup is not p
    assert dup.rate == p.rate


# retro_microphone_interface.__init__ assigns None to CFUNCTYPE fields, which
# ctypes rejects at runtime. The default values cannot be used; callers must
# pass empty CFunctionType instances for every callback slot.
def test_retro_microphone_interface_default_init() -> None:
    retro_microphone_interface(INTERFACE_VERSION)


def test_retro_microphone_interface_with_empty_callbacks() -> None:
    iface = retro_microphone_interface(
        INTERFACE_VERSION,
        retro_open_mic_t(),
        retro_close_mic_t(),
        retro_get_mic_params_t(),
        retro_set_mic_state_t(),
        retro_get_mic_state_t(),
        retro_read_mic_t(),
    )
    assert iface.interface_version == INTERFACE_VERSION
    assert not iface.open_mic
    assert not iface.close_mic


def test_retro_microphone_interface_deepcopy_with_empty_callbacks() -> None:
    iface = retro_microphone_interface(
        INTERFACE_VERSION,
        retro_open_mic_t(),
        retro_close_mic_t(),
        retro_get_mic_params_t(),
        retro_set_mic_state_t(),
        retro_get_mic_state_t(),
        retro_read_mic_t(),
    )
    dup = copy.deepcopy(iface)
    assert dup is not iface
    assert dup.interface_version == iface.interface_version
