"""Validate that a :term:`core` registers libretro's main ``retro_set_*`` callbacks."""

from typer.main import get_command

from ._common import CoreArg, prepare


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


app = prepare(main)
command = get_command(app)

if __name__ == "__main__":
    app()
