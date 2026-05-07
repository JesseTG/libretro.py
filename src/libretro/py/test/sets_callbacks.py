"""Test scenario that loads a libretro core and registers the basic ``retro_set_*`` callbacks."""

import typer

from ._common import CoreArg


def main(libretro: CoreArg):
    """
    Load a libretro core and sets its basic callbacks
    (e.g. retro_set_environment, retro_set_video_refresh, etc.).
    Exits with 0 upon success.
    """
    libretro.set_video_refresh(lambda _data, _width, _height, _pitch: None)
    libretro.set_audio_sample(lambda _left, _right: None)
    libretro.set_audio_sample_batch(lambda _data, _frames: 0)
    libretro.set_input_poll(lambda: None)
    libretro.set_input_state(lambda _port, _device, _index, _id: 0)
    libretro.set_environment(lambda _cmd, _data: False)


if __name__ == "__main__":
    typer.run(main)
