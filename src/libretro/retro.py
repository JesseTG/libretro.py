from ctypes import CDLL
from collections.abc import *
from typing import *

from .audio import AudioState
from .core import Core
from .environment import Environment
from .input import InputState
from .video import VideoState
from .defs import *



# TODO: Add ability to pass custom callbacks and content
def load_environment(
        core: str | CDLL,
        content: Optional[Content | Sequence[Content]] = None
) -> Environment:
    """
    Load a libretro core from a file and sets all the required retro_ callbacks.
    Does not call retro_init or retro_load_game.

    Parameters:
        core: The shared library that contains the core.
          Can be a path to a file or a CDLL instance.

    Returns:
        An environment object that can be used to manage the core's life and execution.

    Raises:
        ValueError: If `core` is missing a required symbol.
    """
    audio = AudioState()
    input_state = InputState()
    video = VideoState()
    env = Environment(core, audio, input_state, video)

    env.core.set_video_refresh(env.video.refresh)
    env.core.set_audio_sample(env.audio.audio_sample)
    env.core.set_audio_sample_batch(env.audio.audio_sample_batch)
    env.core.set_input_poll(env.input.poll)
    env.core.set_input_state(env.input.state)
    env.core.set_environment(env.environment)

    return env


def init_environment(path: str) -> Environment:
    pass
