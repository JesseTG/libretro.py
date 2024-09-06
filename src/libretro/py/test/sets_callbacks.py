import typer

from ._common import CoreArg


def main(libretro: CoreArg):
    """
    Loads a libretro core and sets its basic callbacks
    (e.g. retro_set_environment, retro_set_video_refresh, etc.).
    Exits with 0 upon success.
    """

    libretro.set_video_refresh(lambda data, width, height, pitch: None)
    libretro.set_audio_sample(lambda left, right: None)
    libretro.set_audio_sample_batch(lambda data, frames: 0)
    libretro.set_input_poll(lambda: None)
    libretro.set_input_state(lambda port, device, index, id: 0)
    libretro.set_environment(lambda cmd, data: False)


if __name__ == "__main__":
    typer.run(main)
