import re
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from click import BadArgumentUsage, FileError
from typer import Argument, Option

from libretro import DEFAULT_DRIVER_MAP, Core, HardwareContext


def load_core(value: str):
    try:
        return Core(value)
    except FileNotFoundError as e:
        raise FileError(value, "File not found") from e
    except OSError as e:
        raise FileError(value, f"{e}") from e
    except ValueError as e:
        raise BadArgumentUsage(f"{e}") from e


def option_callback(value: list[str] | None):
    if value is None:
        return None

    for v in value:
        if not re.match(r"^[a-zA-Z0-9_\-]+=.+$", v):
            raise BadArgumentUsage(f"Invalid option format: {v}")

    return value


CoreArg = Annotated[
    Core,
    Argument(
        parser=load_core,
        help="Path to the libretro core to load. Must be a complete path, not a short name.",
        show_default=False,
        metavar="CORE",
    ),
]

ContentArg = Annotated[
    list[Path],
    Argument(
        exists=True,
        resolve_path=True,
        help="Path to the content file(s) to load.",
        metavar="CONTENT",
    ),
]

SubsystemOption = Annotated[
    str | None,
    Option(
        "--subsystem",
        "-s",
        help="Identifier of the subsystem to use when loading the content. Error if not defined by the core.",
        metavar="IDENT",
    ),
]

VerboseOption = Annotated[int, Option("--verbose", "-v", count=True)]

FrameCountOption = Annotated[
    int,
    Option(
        "--frames",
        "-n",
        help="The number of frames to run the core for. May exit earlier if the core exits explicitly; this is not necessarily an error.",
        min=0,
    ),
]

CoreOptionsOption = Annotated[
    list[str] | None,
    Option(
        "--option",
        "-O",
        callback=option_callback,
        help="Set an option for the core. Format: 'option=value'. May be specified multiple times.",
    ),
]


class SoftwareVideoDriverType(StrEnum):
    """
    This is what the video driver option should be matched against
    """

    DEFAULT = "default"
    OPENGL = "opengl"
    OPENGL_CORE = "opengl-core"
    OPENGLES2 = "opengles2"
    OPENGLES3 = "opengles3"
    OPENGLES = "opengles"
    VULKAN = "vulkan"
    D3D9 = "d3d9"
    D3D10 = "d3d10"
    D3D11 = "d3d11"
    D3D12 = "d3d12"


class _AvailableSoftwareVideoDriverType(StrEnum):
    """
    Created so that available choices will be listed on --help
    to reflect the available video drivers.
    """

    DEFAULT = SoftwareVideoDriverType.DEFAULT

    if HardwareContext.OPENGL in DEFAULT_DRIVER_MAP:
        OPENGL = SoftwareVideoDriverType.OPENGL

    if HardwareContext.OPENGL_CORE in DEFAULT_DRIVER_MAP:
        OPENGL_CORE = SoftwareVideoDriverType.OPENGL_CORE

    if HardwareContext.OPENGLES2 in DEFAULT_DRIVER_MAP:
        OPENGLES2 = SoftwareVideoDriverType.OPENGLES2

    if HardwareContext.OPENGLES3 in DEFAULT_DRIVER_MAP:
        OPENGLES3 = SoftwareVideoDriverType.OPENGLES3

    if HardwareContext.OPENGLES_VERSION in DEFAULT_DRIVER_MAP:
        OPENGLES = SoftwareVideoDriverType.OPENGLES

    if HardwareContext.VULKAN in DEFAULT_DRIVER_MAP:
        VULKAN = SoftwareVideoDriverType.VULKAN

    if HardwareContext.D3D9 in DEFAULT_DRIVER_MAP:
        D3D9 = SoftwareVideoDriverType.D3D9

    if HardwareContext.D3D10 in DEFAULT_DRIVER_MAP:
        D3D10 = SoftwareVideoDriverType.D3D10

    if HardwareContext.D3D11 in DEFAULT_DRIVER_MAP:
        D3D11 = SoftwareVideoDriverType.D3D11

    if HardwareContext.D3D12 in DEFAULT_DRIVER_MAP:
        D3D12 = SoftwareVideoDriverType.D3D12


VideoDriverOption = Annotated[
    _AvailableSoftwareVideoDriverType,
    Option(
        "--software-video",
        "-S",
        help="The video driver to use for software rendering.",
        show_choices=True,
    ),
]

WindowOption = Annotated[
    bool,
    Option(
        "--window",
        "-w",
        help="Run the core with a visible window if supported by the active video driver. Useful for RenderDoc and other debugging tools.",
    ),
]

__all__ = [
    "CoreArg",
    "VerboseOption",
    "ContentArg",
    "SubsystemOption",
    "FrameCountOption",
    "CoreOptionsOption",
    "VideoDriverOption",
    "SoftwareVideoDriverType",
    "WindowOption",
]
