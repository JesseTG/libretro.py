from collections.abc import Callable, Sequence
from copy import deepcopy
from ctypes import CDLL
from os import PathLike
from types import TracebackType
from typing import AnyStr, Type

from _ctypes import CFuncPtr

from libretro._utils import Pollable
from libretro.api import (
    API_VERSION,
    AvEnableFlags,
    Content,
    SerializationQuirks,
    SubsystemContent,
    Subsystems,
    retro_controller_info,
    retro_fastforwarding_override,
    retro_get_proc_address_interface,
    retro_input_descriptor,
    retro_memory_map,
    retro_proc_address_t,
    retro_subsystem_info,
    retro_system_av_info,
    retro_system_content_info_override,
    retro_throttle_state,
)
from libretro.api._utils import as_bytes
from libretro.core import Core, CoreInterface
from libretro.drivers import (
    AudioDriver,
    CompositeEnvironmentDriver,
    ContentDriver,
    FileSystemInterface,
    InputDriver,
    LedDriver,
    LoadedContentFile,
    LogDriver,
    MessageInterface,
    MidiDriver,
    OptionDriver,
    RumbleInterface,
    VideoDriver,
)
from libretro.error import CoreShutDownException


class Session:
    def __init__(
        self,
        core: Core | CDLL | str | PathLike,
        content: Content | SubsystemContent | None,
        environment: CompositeEnvironmentDriver,
    ):
        match core:
            case Core():
                self._core = core
            case CDLL(dll):
                self._core = Core(dll)
            case str(path) | PathLike(path):
                self._core = Core(path)
            case _:
                raise TypeError(
                    f"Expected core to be a Core, CDLL, or str; got {type(core).__name__}"
                )

        self._content = content

        if not isinstance(environment, CompositeEnvironmentDriver):
            raise TypeError(
                f"Expected environment to be CompositeEnvironmentDriver; got {type(environment).__name__}"
            )

        self._environment = environment

        self._content = content
        self._system_av_info: retro_system_av_info | None = None

        self._pending_callback_exceptions: list[BaseException] = []
        self._is_exited = False

    def __enter__(self):
        api_version = self._core.api_version()
        if api_version != API_VERSION:
            raise RuntimeError(
                f"libretro.py is only compatible with API version {API_VERSION}, but the core uses {api_version}"
            )

        self._core.set_video_refresh(self._environment.video_refresh)
        self._core.set_audio_sample(self._environment.audio_sample)
        self._core.set_audio_sample_batch(self._environment.audio_sample_batch)
        self._core.set_input_poll(self._environment.input_poll)
        self._core.set_input_state(self._environment.input_state)
        self._core.set_environment(self._environment.environment)
        system_info = self._core.get_system_info()

        if system_info.library_name is None:
            raise RuntimeError("Core did not provide a library name")

        if system_info.library_version is None:
            raise RuntimeError("Core did not provide a library version")

        if system_info.valid_extensions is None:
            raise RuntimeError("Core did not provide valid extensions")

        self._core.init()

        if not self._environment.content:
            # Do nothing, we're testing something that doesn't need to load a game
            return self

        self._environment.content.system_info = deepcopy(system_info)

        loaded: bool = False
        with self._environment.content.load(self._content) as (subsystem, content):
            subsystem: retro_subsystem_info | None
            content: Sequence[LoadedContentFile] | None
            match subsystem, content:
                case (_, None | []):
                    loaded = self._core.load_game(None)
                case None, [info]:
                    # Loading exactly one regular content file
                    info: LoadedContentFile
                    loaded = self._core.load_game(info.info)
                case None, [*_]:
                    raise RuntimeError(
                        "Content driver returned multiple files, but not a subsystem that uses them all"
                    )
                case retro_subsystem_info(), [*infos]:
                    infos: Sequence[LoadedContentFile]
                    game_infos = tuple(i.info for i in infos)
                    loaded = self._core.load_game_special(subsystem.id, game_infos)
                case _, _:
                    raise RuntimeError("Failed to load content")

        if not loaded:
            raise RuntimeError("Failed to load game")

        self._system_av_info = self._core.get_system_av_info()
        self._environment.video.system_av_info = self._system_av_info
        self._environment.audio.system_av_info = self._system_av_info

        return self

    def __exit__(self, exc_type: type[Exception], exc_val: Exception, exc_tb: TracebackType):
        if self._content is not None:
            self._core.unload_game()

        self._core.deinit()
        del self._core
        self._is_exited = True
        return isinstance(exc_val, CoreShutDownException)
        # Returning True from a context manager suppresses the exception
        # and continues from the end of the `with` block.
        # If the core shut down then core methods should raise a CoreShutDownException.
        # If exc_val is None, then there never was an exception.
        # If exc_val is any other error, then it should be propagated after cleaning up the core.

    @property
    def core(self) -> CoreInterface:
        if self._is_exited or self._environment.is_shutdown:
            raise CoreShutDownException()

        return self._core

    @property
    def environment(self) -> CompositeEnvironmentDriver:
        return self._environment

    @property
    def audio(self) -> AudioDriver:
        return self._environment.audio

    @property
    def input(self) -> InputDriver:
        return self._environment.input

    @property
    def video(self) -> VideoDriver:
        return self._environment.video

    @property
    def content(self) -> ContentDriver:
        return self._environment.content

    @property
    def message(self) -> MessageInterface | None:
        return self._environment.message

    @property
    def is_shutdown(self) -> bool:
        return self._environment.is_shutdown

    @property
    def is_exited(self) -> bool:
        return self._is_exited

    @property
    def system_directory(self) -> bytes | None:
        return self._environment.path.system_dir

    @property
    def system_dir(self) -> bytes | None:
        return self.system_directory

    @property
    def input_descriptors(self) -> Sequence[retro_input_descriptor] | None:
        return self._environment.input.descriptors

    @property
    def options(self) -> OptionDriver:
        return self._environment.options

    @property
    def support_no_game(self) -> bool | None:
        return self._environment.content.support_no_game

    @property
    def rumble(self) -> RumbleInterface | None:
        return self._environment.input.rumble

    @property
    def log(self) -> LogDriver | None:
        return self._environment.log

    @property
    def save_directory(self) -> bytes | None:
        return self._environment.path.save_dir

    @property
    def save_dir(self) -> bytes | None:
        return self.save_directory

    @property
    def proc_address_callback(self) -> retro_get_proc_address_interface | None:
        return self._environment.proc_address_callback

    def get_proc_address(
        self, sym: AnyStr, funtype: Type[CFuncPtr] | None = None
    ) -> retro_proc_address_t | Callable | None:
        if not self.proc_address_callback or not sym:
            return None

        name = as_bytes(sym)

        proc = self.proc_address_callback.get_proc_address(name)

        if not proc:
            return None

        if funtype:
            return funtype(proc)

        return proc

    @property
    def subsystems(self) -> Subsystems | None:
        return self._environment.content.subsystem_info

    @property
    def controller_info(self) -> Sequence[retro_controller_info] | None:
        return self._environment.input.controller_info

    @property
    def memory_maps(self) -> retro_memory_map | None:
        return self._environment.memory_maps

    @property
    def support_achievements(self) -> bool | None:
        return self._environment.support_achievements

    @property
    def av_enable(self) -> AvEnableFlags:
        return self._environment.av_enable

    @property
    def midi(self) -> MidiDriver:
        return self._environment.midi

    @property
    def serialization_quirks(self) -> SerializationQuirks | None:
        return self._environment.serialization_quirks

    @property
    def vfs(self) -> FileSystemInterface:
        return self._environment.vfs

    @property
    def led(self) -> LedDriver:
        return self._environment.led

    @property
    def max_users(self) -> int | None:
        return self._environment.input.max_users

    @property
    def content_info_overrides(
        self,
    ) -> Sequence[retro_system_content_info_override] | None:
        return self._environment.content.overrides

    def run(self) -> None:
        if self._is_exited or self._environment.is_shutdown:
            raise CoreShutDownException()

        if self._environment.video.needs_reinit:
            self._environment.video.reinit()

        # TODO: In RetroArch, retro_audio_callback.set_state is called on the main thread,
        # just before starting the audio thread and just after stopping it.
        # TODO: In RetroArch, retro_audio_callback.callback is called on the audio thread.
        # TODO: In RetroArch, an audio thread is started if the core registers an audio callback

        if isinstance(self._environment.microphones, Pollable):
            self._environment.microphones.poll()

        if self._environment.timing:
            self._environment.timing.frame_time(None)
            # TODO: Get the time elapsed since the last frame and pass it to frame_time
            # or if throttle_state is set, use that to determine the time elapsed

        # TODO: self._environment.audio.report_buffer_status()
        # TODO: self._environment.camera.poll() (see runloop_iterate in runloop.c, lion)
        # TODO: Ensure that input is not polled more than once per frame
        self._core.run()

    def reset(self) -> None:
        if self._is_exited or self._environment.is_shutdown:
            raise CoreShutDownException()

        self._core.reset()


__all__ = [
    "Session",
    "CoreShutDownException",
]
