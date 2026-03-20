import typer

from ._common import CoreArg


def main(libretro: CoreArg):
    """
    Loads a libretro core and displays its system info.
    Exits with 0 upon success.
    """

    system_info = libretro.get_system_info()

    library_name = system_info.library_name
    library_version = system_info.library_version
    block_extract = system_info.block_extract
    need_fullpath = system_info.need_fullpath
    valid_extensions = system_info.valid_extensions

    print(f"library_name:", "NULL" if library_name is None else library_name.decode())
    print(f"library_version:", "NULL" if library_version is None else library_version.decode())
    print(f"block_extract:", block_extract)
    print(f"need_fullpath:", need_fullpath)
    print(f"valid_extensions:", "NULL" if valid_extensions is None else valid_extensions.decode())


if __name__ == "__main__":
    typer.run(main)
