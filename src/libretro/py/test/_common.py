import re
from pathlib import Path
from typing import Annotated

from click import BadArgumentUsage, FileError
from typer import Argument, Option

from libretro import Core


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

__all__ = [
    "CoreArg",
    "VerboseOption",
    "ContentArg",
    "SubsystemOption",
    "FrameCountOption",
    "CoreOptionsOption",
]
