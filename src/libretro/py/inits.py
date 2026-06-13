"""Initialize then deinitialize a :term:`core` without loading content or running frames."""

from typer.main import get_command

import libretro

from ._common import CoreArg, prepare


def main(core: CoreArg):
    """
    Load and initializes a libretro core,
    then unloads it without loading content or running frames.
    Exits with 0 if these steps were successful.
    """
    with libretro.Session(core, None, content=None) as _:
        # retro_set_*, retro_init, retro_deinit, etc. are called implicitly
        pass


app = prepare(main)
command = get_command(app)

if __name__ == "__main__":
    app()
