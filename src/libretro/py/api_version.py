"""Validate a :term:`core`'s API version."""

from typing import Annotated

from typer import Option
from typer.main import get_command

from ._common import CoreArg, prepare


def main(libretro: CoreArg, api_version: Annotated[int, Option(min=0)] = 1):
    """
    Load a libretro core and validates the version it returns.
    Exits with 0 upon success.
    """
    core_version = libretro.api_version()

    if core_version != api_version:
        raise ValueError(f"Core version mismatch: expected {api_version}, got {core_version}")


app = prepare(main)
command = get_command(app)

if __name__ == "__main__":
    app()
