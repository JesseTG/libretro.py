"""Load a :term:`core` into memory without calling any of its functions."""

from typer.main import get_command

from ._common import CoreArg, prepare


# noinspection PyUnusedLocal
def main(libretro: CoreArg):
    """
    Load a libretro core.
    Exits with 0 if the core loaded and exposes the required symbols.
    Does not call any functions.
    """
    pass
    # Core will be loaded with the parser defined in CoreArg;
    # if it succeeds, nothing happens.
    # If it fails, an exception will be raised.


app = prepare(main)
command = get_command(app)

if __name__ == "__main__":
    app()
