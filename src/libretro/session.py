from typing import *

from ._libretro import retro_game_info
from .core import Core
from .callback.audio import AudioCallbacks, AudioState
from libretro.callback.environment import EnvironmentCallbacks, Environment
from .callback.input import InputCallbacks, GeneratorInputState
from .callback.video import VideoCallbacks, SoftwareVideoState


class SpecialContent(NamedTuple):
    type: int
    content: Sequence[str]


class Session:
    def __init__(
            self,
            core: Core | str,
            audio: AudioCallbacks,
            input_state: InputCallbacks,
            video: VideoCallbacks,
            environment: EnvironmentCallbacks,
            content: str | SpecialContent | None = None,
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
        self._core.set_environment(self._environment.environment)

        self._core.init()
        loaded: bool = False
        match self._content:
            case str(content):
                loaded = self._core.load_game(content)
            case SpecialContent(content_type, content):
                loaded = self._core.load_game_special(content_type, content)
            case None:
                if not self._environment.support_no_game:
                    raise RuntimeError("No content provided")

                loaded = self._core.load_game(retro_game_info())

        if not loaded:
            raise RuntimeError("Failed to load game")

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

    @property
    def environment(self) -> EnvironmentCallbacks:
        return self._environment


def default_session(
        core: str,
        content: str | SpecialContent | None = None,
        audio: AudioCallbacks | None = None,
        input_state: InputCallbacks | None = None,
        video: VideoCallbacks | None = None,
        environment: EnvironmentCallbacks | None = None,
        ) -> Session:
    """
    Returns a Session with default state objects.
    """

    return Session(
        core=core,
        audio=audio or AudioState(),
        input_state=input_state or GeneratorInputState(),
        video=video or SoftwareVideoState(),
        environment=environment or Environment(),
        content=content
    )