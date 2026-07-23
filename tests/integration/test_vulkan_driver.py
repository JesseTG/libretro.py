"""Integration tests for the Vulkan driver against the ``vulkan_rendering`` sample core."""

from __future__ import annotations

import pytest

from libretro.api.video import HardwareContext
from libretro.session import Session

from .conftest import SampleCoreLoader

pytestmark = pytest.mark.vulkan

# The sample core clears its framebuffer to (0.8, 0.6, 0.2, 1.0)
# before drawing a triangle over it
CLEAR_COLOR = (204, 153, 51, 255)


def test_vulkan_core_renders_and_screenshots(load_core: SampleCoreLoader) -> None:
    pytest.importorskip("vulkan", reason="the libretro.py[vulkan] extra is not installed")
    core = load_core("video", "vulkan_rendering")

    with Session(core, None) as session:
        for _ in range(3):
            session.run()

        video = session.video
        assert video.active_context == HardwareContext.VULKAN

        shot = video.screenshot()
        assert shot is not None
        assert (shot.width, shot.height) == (320, 240)

        # The top-left corner is outside the triangle, so it must be the clear color
        corner = tuple(shot.data[:4])
        assert all(abs(a - b) <= 2 for a, b in zip(corner, CLEAR_COLOR)), corner

        # The frame must not be a single flat color:
        # the triangle covers a significant part of it
        data = bytes(shot.data)
        differing = sum(1 for i in range(0, len(data), 4) if data[i : i + 4] != bytes(corner))
        assert differing > 1000, differing
