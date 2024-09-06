from typing import Annotated

from typer import Argument, Option

from libretro import Core

CoreArg = Annotated[
    Core,
    Argument(
        parser=Core,
        help="Path to the libretro core to load. Must be a complete path, not a short name.",
        show_default=False,
        metavar="core",
    ),
]

VerboseOption = Annotated[int, Option("--verbose", "-v", count=True)]

__all__ = ["CoreArg"]
