import typer

from ._common import CoreArg


# noinspection PyUnusedLocal
def main(libretro: CoreArg):
    """
    Loads a libretro core.
    Exits with 0 if the core loaded and exposes the required symbols.
    Does not call any functions.
    """
    pass
    # Core will be loaded with the parser defined in CoreArg;
    # if it succeeds, nothing happens.
    # If it fails, an exception will be raised.


if __name__ == "__main__":
    typer.run(main)
