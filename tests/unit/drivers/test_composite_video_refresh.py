"""Unit tests for :class:`CompositeEnvironmentDriver`'s ``video_refresh``."""

from __future__ import annotations

from ctypes import addressof, c_char
from typing import override

import pytest

from libretro.ctypes import c_void_ptr
from libretro.drivers import (
    ArrayAudioDriver,
    ArrayVideoDriver,
    CompositeEnvironmentDriver,
    FrameBufferSpecial,
    IterableInputDriver,
)

WIDTH = 4
HEIGHT = 2
PITCH = WIDTH * 4


class RecordingVideoDriver(ArrayVideoDriver):
    """An :class:`ArrayVideoDriver` that remembers what it was handed."""

    def __init__(self) -> None:
        super().__init__()
        self.frames: list[memoryview[int] | FrameBufferSpecial] = []

    @override
    def refresh(
        self, data: memoryview[int] | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        self.frames.append(data)
        super().refresh(data, width, height, pitch)


@pytest.fixture
def video() -> RecordingVideoDriver:
    return RecordingVideoDriver()


@pytest.fixture
def env(video: RecordingVideoDriver) -> CompositeEnvironmentDriver:
    return CompositeEnvironmentDriver(
        audio=ArrayAudioDriver(),
        input=IterableInputDriver(),
        video=video,
    )


@pytest.mark.parametrize(
    "null", [c_void_ptr(None), c_void_ptr(0)], ids=["c_void_ptr(None)", "c_void_ptr(0)"]
)
def test_a_null_framebuffer_is_a_frame_dupe(
    env: CompositeEnvironmentDriver, video: RecordingVideoDriver, null: c_void_ptr
) -> None:
    """A core may pass ``NULL`` to ``retro_video_refresh_t`` to repeat the last frame.

    ``ctypes`` reports a ``NULL`` ``c_void_p``'s ``value`` as ``None`` rather
    than ``0`` -- for a pointer built from either spelling -- so matching only
    on ``0`` sent every dupe to the fallback branch, which raised
    :class:`TypeError` out of the core's own callback.
    """
    assert null.value is None, "a NULL c_void_p reports its value as None"

    env.video_refresh(null, WIDTH, HEIGHT, PITCH)

    assert video.frames == [FrameBufferSpecial.DUPE]


def test_a_real_framebuffer_is_still_passed_through(
    env: CompositeEnvironmentDriver, video: RecordingVideoDriver
) -> None:
    """The ordinary case: a pointer to pixels arrives as a view of those pixels."""
    pixels = bytearray(range(PITCH * HEIGHT))
    block = (c_char * len(pixels)).from_buffer(pixels)

    env.video_refresh(c_void_ptr(addressof(block)), WIDTH, HEIGHT, PITCH)

    assert len(video.frames) == 1
    frame = video.frames[0]
    assert isinstance(frame, memoryview)
    assert bytes(frame) == bytes(pixels)
