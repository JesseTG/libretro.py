from .audio import AudioState
from .core import Core
from .environment import Environment
from .input import InputState
from .video import VideoState


def load_core(path: str) -> Environment:
    """
    Load a libretro core from a file and sets all the required retro_ callbacks.

    Parameters:
        path: The path to the core shared library.

    Returns:
        An environment object that can be used to manage the core's life and execution.

    Throws:
        ValueError: If the core is missing a required symbol.
    """
    audio = AudioState()
    input_state = InputState()
    video = VideoState()
    env = Environment(path, audio, input_state, video)

    env.core.set_video_refresh(env.video.refresh)
    env.core.set_audio_sample(env.audio.audio_sample)
    env.core.set_audio_sample_batch(env.audio.audio_sample_batch)
    env.core.set_input_poll(env.input.poll)
    env.core.set_input_state(env.input.state)
    env.core.set_environment(env.environment)

    return env
