import typer

from libretro import (
    DEFAULT_DRIVER_MAP,
    Content,
    HardwareContext,
    ModernGlVideoDriver,
    SessionBuilder,
    SubsystemContent,
)

from ._common import (
    ContentArg,
    CoreArg,
    CoreOptionsOption,
    FrameCountOption,
    SoftwareVideoDriverType,
    SubsystemOption,
    VideoDriverOption,
    WindowOption,
)

_EMPTY = []


def main(
    libretro: CoreArg,
    subsystem: SubsystemOption = None,
    content_paths: ContentArg = None,
    frames: FrameCountOption = 60,
    options: CoreOptionsOption = (),
    software_video: VideoDriverOption = SoftwareVideoDriverType.DEFAULT,
    windowed: WindowOption = False,
):
    """
    Loads a libretro core with zero or more content files
    and runs it for a fixed number of frames.

    Exits with 0 if no errors are raised during this time.
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

    core_options: dict[str, str] = (
        {k: v for k, v in (opt.split("=", 1) for opt in options)} if options else dict()
    )

    driver_map = dict(DEFAULT_DRIVER_MAP)
    if windowed and HardwareContext.OPENGL in driver_map:
        init_with_window = lambda: ModernGlVideoDriver(window="default")
        driver_map[HardwareContext.OPENGL] = init_with_window
        driver_map[HardwareContext.OPENGL_CORE] = init_with_window

    match software_video:
        case SoftwareVideoDriverType.OPENGL:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.OPENGL]
        case SoftwareVideoDriverType.OPENGL_CORE:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.OPENGL_CORE]
        case SoftwareVideoDriverType.OPENGLES2:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.OPENGLES2]
        case SoftwareVideoDriverType.OPENGLES3:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.OPENGLES3]
        case SoftwareVideoDriverType.OPENGLES:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.OPENGLES_VERSION]
        case SoftwareVideoDriverType.VULKAN:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.VULKAN]
        case SoftwareVideoDriverType.D3D9:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.D3D9]
        case SoftwareVideoDriverType.D3D10:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.D3D10]
        case SoftwareVideoDriverType.D3D11:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.D3D11]
        case SoftwareVideoDriverType.D3D12:
            driver_map[HardwareContext.NONE] = driver_map[HardwareContext.D3D12]

    # TODO: Allow a window to be created for the session

    builder = (
        SessionBuilder.defaults(libretro)
        .with_content(content)
        .with_options(core_options)
        .with_video(driver_map)
    )

    with builder.build() as session:
        for i in range(frames):
            session.run()


if __name__ == "__main__":
    typer.run(main)
