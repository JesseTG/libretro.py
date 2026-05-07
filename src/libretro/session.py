"""
High-level harness that drives a :class:`.Core` through its libretro lifecycle.

.. seealso::

    :mod:`libretro.builder`
        The :class:`.SessionBuilder` factory used to construct a configured :class:`.Session`.
"""

import warnings
from collections.abc import Sequence
from copy import deepcopy
from ctypes import CDLL
from os import PathLike
from types import TracebackType
from typing import override

from libretro.api import (
    API_VERSION,
    AvEnableFlags,
    Content,
    HardwareContext,
    Port,
    SavestateContext,
    SubsystemContent,
    retro_subsystem_info,
    retro_system_av_info,
    retro_system_content_info_override,
)
from libretro.core import Core, CoreInterface
from libretro.drivers import (
    AudioDriver,
    CameraDriver,
    CompositeEnvironmentDriver,
    ContentDriver,
    FileSystemDriver,
    InputDriver,
    LedDriver,
    LocationDriver,
    LogDriver,
    MessageDriver,
    MicrophoneDriver,
    MidiDriver,
    OptionDriver,
    PathDriver,
    PerfDriver,
    PowerDriver,
    RumbleDriver,
    SensorDriver,
    TimingDriver,
    UserDriver,
    VideoDriver,
)
from libretro.drivers.types import Pollable
from libretro.error import (
    CallbackException,
    CallbackExceptionGroup,
    CoreShutDownException,
)


class Session[
    _Audio: AudioDriver,
    _Input: InputDriver,
    _Video: VideoDriver,
    _Content: ContentDriver | None,
    _Message: MessageDriver | None,
    _Option: OptionDriver | None,
    _Path: PathDriver | None,
    _Rumble: RumbleDriver | None,
    _Sensor: SensorDriver | None,
    _Camera: CameraDriver | None,
    _Log: LogDriver | None,
    _Perf: PerfDriver | None,
    _Location: LocationDriver | None,
    _User: UserDriver | None,
    _Vfs: FileSystemDriver | None,
    _Led: LedDriver | None,
    _Midi: MidiDriver | None,
    _Timing: TimingDriver | None,
    _Mic: MicrophoneDriver | None,
    _Power: PowerDriver | None,
](
    CompositeEnvironmentDriver[
        _Audio,
        _Input,
        _Video,
        _Content,
        _Message,
        _Option,
        _Path,
        _Rumble,
        _Sensor,
        _Camera,
        _Log,
        _Perf,
        _Location,
        _User,
        _Vfs,
        _Led,
        _Midi,
        _Timing,
        _Mic,
        _Power,
    ]
):
    """
    A configured libretro core paired with the drivers that satisfy its environment calls.

    Use :class:`Session` as a context manager:
    entering it loads the core (and game, if any) and wires up callbacks;
    exiting it unloads the game and deinitializes the core.
    Each constructor argument selects which driver implementation to use for one libretro subsystem;
    most are optional and default to :obj:`None`,
    in which case the matching env-call returns failure.

    .. seealso::

        :class:`.SessionBuilder`
            Fluent builder that constructs a :class:`Session` with sensible defaults.
    """

    def __init__(
        self,
        /,
        core: Core | CDLL | str | PathLike[str] | PathLike[bytes],
        game: Content | SubsystemContent | None,
        audio: _Audio,
        input: _Input,
        video: _Video,
        content: _Content = None,
        overscan: bool | None = None,
        message: _Message = None,
        options: _Option = None,
        path: _Path = None,
        rumble: _Rumble = None,
        sensor: _Sensor = None,
        camera: _Camera = None,
        log: _Log = None,
        perf: _Perf = None,
        location: _Location = None,
        user: _User = None,
        vfs: _Vfs = None,
        led: _Led = None,
        av_enable: AvEnableFlags | None = None,
        midi: _Midi = None,
        timing: _Timing = None,
        preferred_hw: HardwareContext | None = None,
        driver_switch_enable: bool | None = None,
        savestate_context: SavestateContext | None = None,
        jit_capable: bool | None = None,
        mic: _Mic = None,
        device_power: _Power = None,
    ):
        """
        Initialize the session with a core, optional game content, and driver implementations.

        :param core: The libretro core to load.
            Accepts a :class:`.Core`, an already-loaded :class:`ctypes.CDLL`,
            or a path to a shared library on disk.
        :param game: The content to pass to ``retro_load_game`` (or ``retro_load_game_special``),
            or :obj:`None` to load the core without content.
        :param audio: Required audio driver.
        :param input: Required input driver.
        :param video: Required video driver.
        :param content: Optional content driver
            that resolves :class:`.Content` references to loaded files.
        :param overscan: Initial value for the ``overscan`` env-call response,
            or :obj:`None` to leave it unset.
        :param message: Optional driver that handles ``RETRO_ENVIRONMENT_SET_MESSAGE``.
        :param options: Optional core-options driver.
        :param path: Optional driver that supplies system/save/asset directory paths.
        :param rumble: Optional rumble driver.
        :param sensor: Optional motion-sensor driver.
        :param camera: Optional camera driver.
        :param log: Optional log driver.
        :param perf: Optional performance-counter driver.
        :param location: Optional geolocation driver.
        :param user: Optional driver that exposes username and language to the core.
        :param vfs: Optional virtual filesystem driver.
        :param led: Optional LED driver.
        :param av_enable: Initial value for the ``audio_video_enable`` env-call response,
            or :obj:`None` to leave it unset.
        :param midi: Optional MIDI driver.
        :param timing: Optional timing driver.
        :param preferred_hw: Initial value for the ``preferred_hw_render`` env-call response,
            or :obj:`None` to leave it unset.
        :param driver_switch_enable: Whether ``RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE``
            should report driver-switch support, or :obj:`None` to leave it unset.
        :param savestate_context: Initial value for the ``savestate_context`` env-call response,
            or :obj:`None` to leave it unset.
        :param jit_capable: Initial value for the ``jit_capable`` env-call response,
            or :obj:`None` to leave it unset.
        :param mic: Optional microphone driver.
        :param device_power: Optional driver that reports device battery state.
        :raises TypeError: If ``core`` is not a :class:`.Core`,
            :class:`ctypes.CDLL`, or a filesystem path.
        """
        super().__init__(
            audio=audio,
            input=input,
            video=video,
            content=content,
            overscan=overscan,
            message=message,
            options=options,
            path=path,
            rumble=rumble,
            sensor=sensor,
            camera=camera,
            log=log,
            perf=perf,
            location=location,
            user=user,
            vfs=vfs,
            led=led,
            av_enable=av_enable,
            midi=midi,
            timing=timing,
            preferred_hw=preferred_hw,
            driver_switch_enable=driver_switch_enable,
            savestate_context=savestate_context,
            jit_capable=jit_capable,
            mic=mic,
            device_power=device_power,
        )
        match core:
            case Core():
                self._core = core
            case CDLL():
                self._core = Core(core)
            case str() | PathLike() as corepath:
                self._core = Core(corepath)
            case _:
                raise TypeError(
                    f"Expected core to be a Core, CDLL, or str; got {type(core).__name__}"
                )

        self._game = game

        self._content = content
        self._system_av_info: retro_system_av_info | None = None
        self._pending_callback_exceptions: list[Exception] = []
        self._is_exited = False

    def __enter__(self):
        """
        Initialize the core, register callbacks, and load content.

        :return: This session, suitable for use inside a ``with`` block.
        :raises RuntimeError: If the core's API version is incompatible,
            its system info is incomplete,
            or content loading fails.
        """
        api_version = self._core.api_version()
        self._raise_pending_exceptions("retro_api_version")

        if api_version != API_VERSION:
            raise RuntimeError(
                f"libretro.py is only compatible with API version {API_VERSION}, but the core uses {api_version}"
            )

        self._core.set_video_refresh(self.video_refresh)
        self._raise_pending_exceptions("retro_set_video_refresh")
        self._core.set_audio_sample(self.audio_sample)
        self._raise_pending_exceptions("retro_set_audio_sample")
        self._core.set_audio_sample_batch(self.audio_sample_batch)
        self._raise_pending_exceptions("retro_set_audio_sample_batch")
        self._core.set_input_poll(self.input_poll)
        self._raise_pending_exceptions("retro_set_input_poll")
        self._core.set_input_state(self.input_state)
        self._raise_pending_exceptions("retro_set_input_state")
        self._core.set_environment(self.environment)
        self._raise_pending_exceptions("retro_set_environment")

        system_info = self._core.get_system_info()
        self._raise_pending_exceptions("retro_get_system_info")

        if system_info.library_name is None:
            raise RuntimeError("Core did not provide a library name")

        if system_info.library_version is None:
            raise RuntimeError("Core did not provide a library version")

        if system_info.valid_extensions is None:
            raise RuntimeError("Core did not provide valid extensions")

        self._core.init()
        self._raise_pending_exceptions("retro_init")

        if self._content is None:
            # Do nothing, we're testing something that doesn't need to load a game
            return self

        self._content.system_info = deepcopy(system_info)

        loaded = False
        with self._content.load(self._game) as (subsystem, content):
            match subsystem, content:
                case (_, None | []):
                    loaded = self._core.load_game(None)
                    self._raise_pending_exceptions("retro_load_game")
                case None, [info]:
                    # Loading exactly one regular content file
                    loaded = self._core.load_game(info.info)
                    self._raise_pending_exceptions("retro_load_game")
                case None, [*_]:
                    raise RuntimeError(
                        "Content driver returned multiple files, but not a subsystem that uses them all"
                    )
                case retro_subsystem_info(), [*infos]:
                    game_infos = tuple(i.info for i in infos)
                    loaded = self._core.load_game_special(subsystem.id, game_infos)
                    self._raise_pending_exceptions("retro_load_game_special")
                case _, _:
                    raise RuntimeError("Failed to load content")

        if not loaded:
            raise RuntimeError("Failed to load game")

        self._system_av_info = self._core.get_system_av_info()
        self._raise_pending_exceptions("retro_get_system_av_info")

        self._video.system_av_info = self._system_av_info
        if self._audio is not self._video:
            # Handle the case where the audio and video drivers are the same object
            # (e.g. a driver that implements both interfaces)
            # to avoid calling side effects twice on the same driver.
            self._audio.system_av_info = self._system_av_info

        return self

    def __exit__(self, exc_type: type[Exception], exc_val: Exception, exc_tb: TracebackType):
        """
        Unload the game and deinitialize the core, propagating exceptions unless the core shut down.

        :return: :obj:`True` if a :class:`.CoreShutDownException` should be suppressed.
        """
        if self._content is not None:
            self._core.unload_game()
            self._raise_pending_exceptions("retro_unload_game")

        self._core.deinit()
        self._raise_pending_exceptions("retro_deinit")

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
        """
        The active :class:`.CoreInterface` for this session.

        :raises CoreShutDownException: If the session has exited or the core has shut down.
        """
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        return self._core

    @property
    def is_exited(self) -> bool:
        """Whether this session has exited its ``with`` block."""
        return self._is_exited

    @property
    def system_directory(self) -> bytes | None:
        """
        The system directory the path driver advertises to the core.

        :obj:`None` if no path driver was configured.
        """
        if self._path is None:
            return None

        return self._path.system_dir

    @property
    def system_dir(self) -> bytes | None:
        """Alias for :attr:`system_directory`."""
        return self.system_directory

    @property
    def save_directory(self) -> bytes | None:
        """
        The save directory the path driver advertises to the core.

        :obj:`None` if no path driver was configured.
        """
        if self._path is None:
            return None

        return self._path.save_dir

    @property
    def save_dir(self) -> bytes | None:
        """Alias for :attr:`save_directory`."""
        return self.save_directory

    @property
    def max_users(self) -> int | None:
        """The maximum number of input ports the input driver advertises."""
        return self._input.max_users

    @property
    def content_info_overrides(
        self,
    ) -> Sequence[retro_system_content_info_override] | None:
        """
        Content-info overrides registered by the core, exposed by the content driver.

        :obj:`None` if no content driver was configured.
        """
        if self._content is None:
            return None

        return self._content.overrides

    def run(self) -> None:
        """
        Advance the core by one frame.

        Polls per-frame drivers, ticks the timing driver, and calls ``retro_run``.

        :raises CoreShutDownException: If the session has exited or the core has shut down.
        """
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        if self._video.needs_reinit:
            self._video.reinit()

        # TODO: In RetroArch, retro_audio_callback.set_state is called on the main thread,
        # just before starting the audio thread and just after stopping it.
        # TODO: In RetroArch, retro_audio_callback.callback is called on the audio thread.
        # TODO: In RetroArch, an audio thread is started if the core registers an audio callback

        if isinstance(self._mic, Pollable):
            # TODO: Call all pollable drivers
            self._mic.poll()

        if self._timing is not None:
            self._timing.frame_time(None)
            # TODO: Get the time elapsed since the last frame and pass it to frame_time
            # or if throttle_state is set, use that to determine the time elapsed

        # TODO: self._environment.audio.report_buffer_status()
        # TODO: self._environment.camera.poll() (see runloop_iterate in runloop.c, lion)
        # TODO: Ensure that input is not polled more than once per frame
        self._core.run()
        self._raise_pending_exceptions("retro_run")

    def reset(self) -> None:
        """
        Reset the running core, equivalent to flipping the emulated power switch.

        :raises CoreShutDownException: If the session has exited or the core has shut down.
        """
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        self._core.reset()
        self._raise_pending_exceptions("retro_reset")

    def set_controller_port_device(self, port: Port, device: int) -> None:
        """
        Bind a controller class to an input port.

        :param port: The input port to update.
        :param device: The ``RETRO_DEVICE_*`` controller class to assign to ``port``.
        :raises CoreShutDownException: If the session has exited or the core has shut down.
        """
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        self._core.set_controller_port_device(port, device)
        self._raise_pending_exceptions("retro_set_controller_port_device", port, device)

    def cheat_reset(self) -> None:
        """
        Clear all cheats currently registered with the core.

        :raises CoreShutDownException: If the session has exited or the core has shut down.
        """
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        self._core.cheat_reset()
        self._raise_pending_exceptions("retro_cheat_reset")

    def cheat_set(self, index: int, enabled: bool, code: bytes | bytearray | str) -> None:
        """
        Register or update a single cheat with the core.

        :param index: The cheat slot to set.
        :param enabled: Whether the cheat is active.
        :param code: The cheat code in the core's expected format.
        :raises CoreShutDownException: If the session has exited or the core has shut down.
        """
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        self._core.cheat_set(index, enabled, code)
        self._raise_pending_exceptions("retro_cheat_set", index, enabled, code)

    @override
    def _handle_callback_exception(self, exception: Exception) -> None:
        warnings.warn(f"Exception raised in libretro.py callback: {exception}")
        # TODO: Look at the warnings module to see how I can improve the warning message
        self._pending_callback_exceptions.append(exception)

    def _raise_pending_exceptions(self, function: str, *args: object) -> None:
        match self._pending_callback_exceptions:
            # If there are no pending exceptions, do nothing
            case []:
                return
            # If there is exactly one pending exception, raise it directly to preserve the original traceback
            case [exception]:
                self._pending_callback_exceptions.clear()
                raise CallbackException(
                    f"Exception raised in libretro.py callbacks during {function}", *args
                ) from exception
            # If there are multiple pending exceptions, raise them as an ExceptionGroup
            case [*exceptions]:
                self._pending_callback_exceptions.clear()
                raise CallbackExceptionGroup(
                    f"Exceptions raised in libretro.py callbacks during {function}",
                    exceptions,
                    *args,
                )


__all__ = [
    "Session",
]
