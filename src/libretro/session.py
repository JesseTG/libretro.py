from typing import *

from libretro import Core, retro_environment_t
from libretro.callback.audio import AudioState
from libretro.environment import EnvironmentCallbackProtocol
from libretro.callback.input import InputState
from libretro.callback.video import VideoState


class Session:
    def __init__(
            self,
            core: Core | str,
            audio: AudioState,
            input_state: InputState,
            video: VideoState,
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
    def audio(self) -> AudioState:
        return self._audio

    @property
    def input(self) -> InputState:
        return self._input

    @property
    def video(self) -> VideoState:
        return self._video


def default_session(
        core: str,
        content: str | Sequence[str] | None = None
        ) -> Session:
    """
    Returns a Session with default state objects.
    """
    pass