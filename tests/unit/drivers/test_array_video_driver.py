"""Unit tests for :class:`ArrayVideoDriver`'s frame buffer."""

from __future__ import annotations

import pytest

from libretro.api import retro_game_geometry, retro_system_av_info, retro_system_timing
from libretro.api.video import PixelFormat
from libretro.drivers import ArrayVideoDriver, FrameBufferSpecial

WIDTH = 4
HEIGHT = 2
PITCH = WIDTH * 4


def av_info(width: int, height: int) -> retro_system_av_info:
    geometry = retro_game_geometry(
        base_width=width, base_height=height, max_width=width, max_height=height
    )
    return retro_system_av_info(geometry, retro_system_timing(fps=60.0, sample_rate=44100))


def xrgb8888_frame(width: int, height: int) -> bytes:
    """Return a frame with distinct pixels, stored as blue, green, red, and an unused byte."""
    return bytes(
        channel for i in range(width * height) for channel in (3 * i, 3 * i + 1, 3 * i + 2, 0)
    )


def rgba(frame: bytes) -> bytes:
    """Return the RGBA pixels that :meth:`.ArrayVideoDriver.screenshot` makes from a frame."""
    return bytes(
        channel
        for i in range(0, len(frame), 4)
        for channel in (frame[i + 2], frame[i + 1], frame[i], 255)
    )


@pytest.fixture
def video() -> ArrayVideoDriver:
    driver = ArrayVideoDriver()
    driver.pixel_format = PixelFormat.XRGB8888
    return driver


def test_reinit_allocates_a_black_frame(video: ArrayVideoDriver) -> None:
    """Setting the AV info reinitializes the driver with a zero-filled frame buffer."""
    video.system_av_info = av_info(WIDTH, HEIGHT)
    assert not video.needs_reinit

    video.refresh(FrameBufferSpecial.DUPE, WIDTH, HEIGHT, PITCH)

    screenshot = video.screenshot()
    assert screenshot is not None
    assert bytes(screenshot.data) == bytes((0, 0, 0, 255)) * WIDTH * HEIGHT


def test_a_larger_frame_grows_the_buffer(video: ArrayVideoDriver) -> None:
    """A frame larger than the AV info's maximum geometry replaces the buffer."""
    video.system_av_info = av_info(1, 1)
    frame = xrgb8888_frame(WIDTH, HEIGHT)

    video.refresh(memoryview(frame), WIDTH, HEIGHT, PITCH)

    screenshot = video.screenshot()
    assert screenshot is not None
    assert (screenshot.width, screenshot.height) == (WIDTH, HEIGHT)
    assert bytes(screenshot.data) == rgba(frame)


def test_the_first_frame_is_kept_without_reinit(video: ArrayVideoDriver) -> None:
    """A frame that arrives before any AV info is stored, not just used to size the buffer."""
    frame = xrgb8888_frame(WIDTH, HEIGHT)

    video.refresh(memoryview(frame), WIDTH, HEIGHT, PITCH)

    screenshot = video.screenshot()
    assert screenshot is not None
    assert bytes(screenshot.data) == rgba(frame)
