"""
Integration tests for :class:`.ModernGlVideoDriver`, driven by ``hw_geometry_test``.

That core declares a maximum geometry eight times its base size on both axes,
resizes its output as it runs, and presents its frames through the hardware path
for one pass over its size schedule and the software path for the next.
Every frame is four quadrants of flat, distinct colour,
and every texel outside the frame carries a fifth colour
that a correct frontend never presents.

Counting colours in a screenshot is therefore enough to catch a frontend
that samples the wrong part of its render texture,
or that keeps drawing through the viewport it started with.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from libretro.drivers.video.driver import FrameBufferSpecial
from libretro.session import Session

from .conftest import SampleCoreLoader

if TYPE_CHECKING:
    import moderngl

    from libretro.core import Core
    from libretro.drivers.video.opengl.moderngl import ModernGlVideoDriver
else:
    # Skip this whole module unless the libretro.py[opengl] extra is installed.
    moderngl = pytest.importorskip("moderngl")
    ModernGlVideoDriver = pytest.importorskip(
        "libretro.drivers.video.opengl.moderngl"
    ).ModernGlVideoDriver

pytestmark = pytest.mark.opengl

# The four colours hw_geometry_test paints its quadrants,
# and the colour it paints everywhere else in the frontend's render texture.
_QUADRANTS = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255))
_SENTINEL = (255, 0, 255)

# The core walks four frame sizes, once on the hardware path
# and once on the software path, so eight frames covers each combination
# and both switches between the two paths.
_SIZE_COUNT = 4
_FRAME_COUNT = _SIZE_COUNT * 2

# A shader that can't be confused with the pass-through the driver ships:
# it drops the blue channel, turning the core's blue quadrant black
# and its white quadrant yellow.
# Pixels that reach the frame without passing through it keep their own colour.
_DROP_BLUE_FRAG = """\
#version 330

uniform sampler2D screenTexture;
in vec2 transformedTexCoord;
out vec4 pixelColor;

void main() {
    vec3 pixel = texture(screenTexture, transformedTexCoord).rgb;
    pixelColor = vec4(pixel.r, pixel.g, 0.0, 1.0f);
}
"""

_SHADED_QUADRANTS = ((255, 0, 0), (0, 255, 0), (0, 0, 0), (255, 255, 0))


@dataclass(frozen=True)
class _Frame:
    """One presented frame, reduced to its dimensions and a colour census."""

    index: int
    width: int
    height: int
    kind: str
    counts: Mapping[tuple[int, int, int], int]

    @property
    def pixels(self) -> int:
        return self.width * self.height

    def count(self, colour: tuple[int, int, int]) -> int:
        return self.counts.get(colour, 0)


def _capture(core: Core, video: ModernGlVideoDriver) -> list[_Frame]:
    """
    Run ``core`` for :data:`_FRAME_COUNT` frames and return what the driver presented.

    ``refresh`` is wrapped rather than replaced,
    only so each frame can be labelled with the path it came in on;
    the real driver still does all the work.
    """
    kinds: list[str] = []
    refresh = video.refresh

    def record(
        data: memoryview[int] | FrameBufferSpecial, width: int, height: int, pitch: int
    ) -> None:
        match data:
            case FrameBufferSpecial.HARDWARE:
                kinds.append("hardware")
            case FrameBufferSpecial.DUPE:
                kinds.append("duped")
            case _:
                kinds.append("software")
        refresh(data, width, height, pitch)

    video.refresh = record

    frames: list[_Frame] = []
    with Session(core, None, video=video) as session:
        for index in range(_FRAME_COUNT):
            session.run()
            screenshot = video.screenshot()
            assert screenshot is not None, f"No frame to show after run #{index}"

            # The driver reads its framebuffer with four components
            # regardless of the pixel format it reports, so these bytes are RGBA.
            pixels = memoryview(screenshot.data).cast("B")
            assert len(pixels) == screenshot.width * screenshot.height * 4

            frames.append(
                _Frame(
                    index=index,
                    width=screenshot.width,
                    height=screenshot.height,
                    kind=kinds[-1],
                    counts=Counter(
                        (pixels[i], pixels[i + 1], pixels[i + 2]) for i in range(0, len(pixels), 4)
                    ),
                )
            )

    return frames


@pytest.fixture(autouse=True)
def require_gl_context() -> None:
    """
    Skip when this machine can't create an OpenGL context at all.

    Checked up front so that a failure *inside* the driver
    is reported as a failure rather than mistaken for a missing GPU.
    """
    try:
        moderngl.create_context(standalone=True).release()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Couldn't create an OpenGL context: {exc}")


@pytest.fixture
def frames(load_core: SampleCoreLoader, require_gl_context: None) -> list[_Frame]:  # noqa: ARG001
    """Every frame ``hw_geometry_test`` presents through a stock driver."""
    return _capture(load_core("custom", "hw_geometry_test"), ModernGlVideoDriver())


def test_the_core_covers_both_paths_and_several_frame_sizes(frames: list[_Frame]) -> None:
    """
    The run exercises what the other tests in this module assume it does.

    Without this, a core that stopped resizing or stopped using one of its two
    paths would quietly turn every other test here into a weaker one.
    """
    assert {frame.kind for frame in frames} == {"hardware", "software"}
    assert len({(frame.width, frame.height) for frame in frames}) == _SIZE_COUNT


def test_no_frame_shows_texels_the_core_never_drew(frames: list[_Frame]) -> None:
    """
    No presented frame contains the sentinel colour.

    Regression test: the driver used to sample its entire render texture,
    which is sized for the core's *maximum* geometry,
    into a viewport sized for the core's *base* geometry.
    That shrank each frame by ``base / max`` and padded it
    with texels the core never rendered to.
    """
    offenders = {frame.index: frame.count(_SENTINEL) for frame in frames if frame.count(_SENTINEL)}
    assert not offenders, f"Frames showing texels the core never drew: {offenders}"


def test_every_frame_is_four_equal_quadrants(frames: list[_Frame]) -> None:
    """
    Each frame is exactly one quarter of each quadrant colour.

    This is the strong form of "the whole frame arrived, at the right scale":
    it fails if any part of the frame is missing, duplicated, or resampled.
    """
    for frame in frames:
        quarter = frame.pixels // 4
        census = {colour: frame.count(colour) for colour in _QUADRANTS}
        assert census == dict.fromkeys(_QUADRANTS, quarter), (
            f"Frame #{frame.index} ({frame.kind}, {frame.width}x{frame.height}) "
            f"is not four equal quadrants: {census}"
        )


def test_hardware_frames_pass_through_the_shader_in_their_entirety(
    load_core: SampleCoreLoader,
) -> None:
    """
    Every pixel of a resized hardware frame goes through the driver's shader.

    The hardware path blits the core's texture into the display framebuffer
    before drawing the screen quad over it,
    so a viewport that lags behind the frame size leaves *unshaded* pixels
    standing rather than blank ones.
    With the driver's stock pass-through shader the two are identical
    and the fault is invisible, which is why this test supplies its own.
    """
    frames = _capture(
        load_core("custom", "hw_geometry_test"),
        ModernGlVideoDriver(fragment_shader=_DROP_BLUE_FRAG),
    )
    hardware = [frame for frame in frames if frame.kind == "hardware"]
    assert hardware, "The core presented no hardware frames"

    for frame in hardware:
        quarter = frame.pixels // 4
        census = {colour: frame.count(colour) for colour in _SHADED_QUADRANTS}
        assert census == dict.fromkeys(_SHADED_QUADRANTS, quarter), (
            f"Frame #{frame.index} ({frame.width}x{frame.height}) "
            f"did not come out of the shader intact: {census}"
        )
