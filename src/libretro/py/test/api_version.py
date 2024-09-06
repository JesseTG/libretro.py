from typing import Annotated

import typer
from typer import Option

from ._common import CoreArg


def main(libretro: CoreArg, api_version: Annotated[int, Option(min=0)] = 1):
    """
    Loads a libretro core and validates the version it returns.
    Exits with 0 upon success.
    """

    core_version = libretro.api_version()

    if core_version != api_version:
        raise ValueError(f"Core version mismatch: expected {api_version}, got {core_version}")


if __name__ == "__main__":
    typer.run(main)
