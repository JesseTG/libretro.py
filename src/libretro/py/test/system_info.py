import typer

from ._common import CoreArg


def main(libretro: CoreArg):
    """
    Loads a libretro core and displays its system info.
    Exits with 0 upon success.
    """

    system_info = libretro.get_system_info()

    print(f"library_name:", system_info.library_name.decode())
    print(f"library_version:", system_info.library_version.decode())
    print(f"block_extract:", system_info.block_extract)
    print(f"need_fullpath:", system_info.need_fullpath)
    print(f"valid_extensions:", system_info.valid_extensions.decode())


if __name__ == "__main__":
    typer.run(main)
