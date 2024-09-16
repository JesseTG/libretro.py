import typer

from libretro import Content, SessionBuilder, SubsystemContent

from ._common import (
    ContentArg,
    CoreArg,
    CoreOptionsOption,
    FrameCountOption,
    SubsystemOption,
)

_EMPTY = []


def main(
    libretro: CoreArg,
    subsystem: SubsystemOption = None,
    content_paths: ContentArg = None,
    frames: FrameCountOption = 60,
    options: CoreOptionsOption = _EMPTY,
):
    """
    Loads a libretro core with zero or more content files
    and runs it for a fixed number of frames.

    Exits with 0 if no errors are raised during this time.
    """

    assert _EMPTY == []

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

    core_options: dict[str, str] = (
        {k: v for k, v in (opt.split("=", 1) for opt in options)} if options else dict()
    )

    # TODO: Allow an initial video driver to be specified
    # TODO: Allow a window to be created for the session

    builder = SessionBuilder.defaults(libretro).with_content(content).with_options(core_options)

    with builder.build() as session:
        for i in range(frames):
            session.run()


if __name__ == "__main__":
    typer.run(main)
