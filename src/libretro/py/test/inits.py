import typer

import libretro

from ._common import CoreArg


def main(core: CoreArg):
    """
    Loads and initializes a libretro core,
    then unloads it without loading content or running frames.
    Exits with 0 if these steps were successful.
    """

    builder = libretro.builder.defaults(core).with_content_driver(None)
    with builder.build() as _:
        # retro_set_*, retro_init, retro_deinit, etc. are called implicitly
        pass


if __name__ == "__main__":
    typer.run(main)
