"""Unit tests for :mod:`libretro.api.av`."""

# pyright: reportUnknownMemberType=false
# pytest.approx doesn't have full type annotations,
# so that sets off this pyright check

from __future__ import annotations

import copy
from ctypes import addressof

import pytest

from libretro.api.av import (
    AvEnableFlags,
    Region,
    retro_game_geometry,
    retro_system_av_info,
    retro_system_timing,
)


def test_retro_game_geometry_init_with_kwargs() -> None:
    geom = retro_game_geometry(
        base_width=320,
        base_height=240,
        max_width=640,
        max_height=480,
        aspect_ratio=4.0 / 3.0,
    )
    assert geom.base_width == 320
    assert geom.base_height == 240
    assert geom.max_width == 640
    assert geom.max_height == 480
    assert geom.aspect_ratio == pytest.approx(4.0 / 3.0)


def test_retro_game_geometry_defaults_are_zero() -> None:
    geom = retro_game_geometry()
    assert geom.base_width == 0
    assert geom.base_height == 0
    assert geom.max_width == 0
    assert geom.max_height == 0
    assert geom.aspect_ratio == 0.0


def test_retro_game_geometry_deepcopy() -> None:
    geom = retro_game_geometry(base_width=320, base_height=240, max_width=320, max_height=240)
    dup = copy.deepcopy(geom)
    assert dup is not geom, "Expected two separate retro_game_geometry objects"
    assert addressof(geom) != addressof(dup), (
        "Expected both objects to refer to different C addresses"
    )
    assert dup.base_width == geom.base_width
    assert dup.base_height == geom.base_height


def test_retro_game_geometry_base_size_property() -> None:
    geom = retro_game_geometry(base_width=256, base_height=224, max_width=256, max_height=224)
    assert geom.base_size == (256, 224)


def test_retro_game_geometry_max_size_property() -> None:
    geom = retro_game_geometry(base_width=256, base_height=224, max_width=512, max_height=448)
    assert geom.max_size == (512, 448)


def test_retro_system_timing_init_and_readback() -> None:
    timing = retro_system_timing(fps=59.94, sample_rate=48000.0)
    assert timing.fps == pytest.approx(59.94)
    assert timing.sample_rate == pytest.approx(48000.0)


def test_retro_system_timing_deepcopy() -> None:
    timing = retro_system_timing(fps=60.0, sample_rate=44100.0)
    dup = copy.deepcopy(timing)
    assert addressof(timing) != addressof(dup)
    assert dup is not timing
    assert dup.fps == timing.fps
    assert dup.sample_rate == timing.sample_rate


def test_retro_system_av_info_holds_nested_structs() -> None:
    geom = retro_game_geometry(base_width=160, base_height=144, max_width=160, max_height=144)
    timing = retro_system_timing(fps=59.7, sample_rate=22050.0)
    av = retro_system_av_info(geom, timing)
    assert av.geometry.base_width == 160
    assert av.timing.sample_rate == pytest.approx(22050.0)


def test_retro_system_av_info_deepcopy_preserves_subobjects() -> None:
    geom = retro_game_geometry(base_width=320, base_height=240, max_width=320, max_height=240)
    timing = retro_system_timing(fps=60.0, sample_rate=32000.0)
    av = retro_system_av_info(geom, timing)
    dup = copy.deepcopy(av)
    assert dup is not av
    assert dup.geometry.base_width == 320
    assert dup.timing.fps == pytest.approx(60.0)


def test_region_enum_round_trips_underlying_ints() -> None:
    assert int(Region.NTSC) == 0
    assert int(Region.PAL) == 1


def test_av_enable_flags_combine() -> None:
    combined = AvEnableFlags.VIDEO | AvEnableFlags.AUDIO
    assert AvEnableFlags.VIDEO in combined
    assert AvEnableFlags.AUDIO in combined
    assert AvEnableFlags.FAST_SAVESTATES not in combined


def test_av_enable_flags_all_contains_every_named_flag() -> None:
    for flag in AvEnableFlags:
        assert flag in AvEnableFlags.ALL
