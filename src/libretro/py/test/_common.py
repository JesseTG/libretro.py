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


CoreArg = Annotated[
    Core,
    Argument(
        parser=load_core,
        help="Path to the libretro core to load. Must be a complete path, not a short name.",
        show_default=False,
        metavar="core",
    ),
]

VerboseOption = Annotated[int, Option("--verbose", "-v", count=True)]

__all__ = ["CoreArg"]
