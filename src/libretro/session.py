from typing import *

from ._libretro import retro_environment_t
from .core import Core
from .callback.audio import AudioCallbacks
from .environment import EnvironmentCallbackProtocol
from .callback.input import InputCallbacks
from .callback.video import VideoCallbacks


class Session:
    def __init__(
            self,
            core: Core | str,
            audio: AudioCallbacks,
            input_state: InputCallbacks,
            video: VideoCallbacks,
            environment: EnvironmentCallbackProtocol,
            content: str | Sequence[str] | None = None,
    ):
        if core is None:
            raise ValueError("Core cannot be None")

        if isinstance(core, Core):
            self._core = core
        else:
            self._core = Core(core)

        self._audio = audio
        self._input = input_state
        self._video = video
        self._environment = environment
        self._content = content

    def __enter__(self):
        self._core.set_video_refresh(self._video.refresh)
        self._core.set_audio_sample(self._audio.audio_sample)
        self._core.set_audio_sample_batch(self._audio.audio_sample_batch)
        self._core.set_input_poll(self._input.poll)
        self._core.set_input_state(self._input.state)
        self._core.set_environment(retro_environment_t(self._environment.__call__))

        self._core.init()
        # TODO: Call retro_load_game or retro_load_game_special here (even if there's no content)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._core.unload_game()
        self._core.deinit()
        del self._core
        return False

    @property
    def core(self) -> Core:
        return self._core

    @property
    def audio(self) -> AudioCallbacks:
        return self._audio

    @property
    def input(self) -> InputCallbacks:
        return self._input

    @property
    def video(self) -> VideoCallbacks:
        return self._video


def default_session(
        core: str,
        content: str | Sequence[str] | None = None
        ) -> Session:
    """
    Returns a Session with default state objects.
    """
    pass