import typer

from libretro import Content, SessionBuilder, SubsystemContent

from ._common import ContentArg, CoreArg, SubsystemOption


def main(
    libretro: CoreArg,
    subsystem: SubsystemOption = None,
    content_paths: ContentArg = None,
):
    """
    Loads a libretro core with zero or more content files.

    Exits with 0 if the core loaded the content successfully.

    Exits with failure if the core failed to load the content
    """

    content: Content | SubsystemContent | None
    match subsystem, content_paths:
        case None, [path]:
            # No subsystem, single content (most common case)
            content = path
        case None, None:
            # No subsystem, no content (ok if core uses RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME)
            content = None
        case str(subsystem), [*paths]:
            content = SubsystemContent(subsystem, paths)
        case _:
            raise ValueError("Invalid combination of subsystem and content")

    builder = SessionBuilder.defaults(libretro).with_content(content)

    with builder.build() as _:
        pass


if __name__ == "__main__":
    typer.run(main)
