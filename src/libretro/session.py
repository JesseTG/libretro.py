import warnings
from collections.abc import Sequence
from copy import deepcopy
from ctypes import CDLL
from os import PathLike
from types import TracebackType
from typing import override

from libretro.api import API_VERSION, AvEnableFlags
from libretro.api import Content as GameContent
from libretro.api import (
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
    Audio: AudioDriver = AudioDriver,
    Input: InputDriver = InputDriver,
    Video: VideoDriver = VideoDriver,
    Content: ContentDriver | None = ContentDriver | None,
    Message: MessageDriver | None = MessageDriver | None,
    Option: OptionDriver | None = OptionDriver | None,
    Path: PathDriver | None = PathDriver | None,
    Rumble: RumbleDriver | None = RumbleDriver | None,
    Sensor: SensorDriver | None = SensorDriver | None,
    Camera: CameraDriver | None = CameraDriver | None,
    Log: LogDriver | None = LogDriver | None,
    Perf: PerfDriver | None = PerfDriver | None,
    Location: LocationDriver | None = LocationDriver | None,
    User: UserDriver | None = UserDriver | None,
    Vfs: FileSystemDriver | None = FileSystemDriver | None,
    Led: LedDriver | None = LedDriver | None,
    Midi: MidiDriver | None = MidiDriver | None,
    Timing: TimingDriver | None = TimingDriver | None,
    Mic: MicrophoneDriver | None = MicrophoneDriver | None,
    Power: PowerDriver | None = PowerDriver | None,
](
    CompositeEnvironmentDriver[
        Audio,
        Input,
        Video,
        Content,
        Message,
        Option,
        Path,
        Rumble,
        Sensor,
        Camera,
        Log,
        Perf,
        Location,
        User,
        Vfs,
        Led,
        Midi,
        Timing,
        Mic,
        Power,
    ]
):
    def __init__(
        self,
        /,
        core: Core | CDLL | str | PathLike[str] | PathLike[bytes],
        game: GameContent | SubsystemContent | None,
        audio: Audio,
        input: Input,
        video: Video,
        content: Content = None,
        overscan: bool | None = None,
        message: Message = None,
        options: Option = None,
        path: Path = None,
        rumble: Rumble = None,
        sensor: Sensor = None,
        camera: Camera = None,
        log: Log = None,
        perf: Perf = None,
        location: Location = None,
        user: User = None,
        vfs: Vfs = None,
        led: Led = None,
        av_enable: AvEnableFlags | None = None,
        midi: Midi = None,
        timing: Timing = None,
        preferred_hw: HardwareContext | None = None,
        driver_switch_enable: bool | None = None,
        savestate_context: SavestateContext | None = None,
        jit_capable: bool | None = None,
        mic: Mic = None,
        device_power: Power = None,
    ):
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
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        return self._core

    @property
    def is_exited(self) -> bool:
        return self._is_exited

    @property
    def system_directory(self) -> bytes | None:
        if self._path is None:
            return None

        return self._path.system_dir

    @property
    def system_dir(self) -> bytes | None:
        return self.system_directory

    @property
    def save_directory(self) -> bytes | None:
        if self._path is None:
            return None

        return self._path.save_dir

    @property
    def save_dir(self) -> bytes | None:
        return self.save_directory

    @property
    def max_users(self) -> int | None:
        return self._input.max_users

    @property
    def content_info_overrides(
        self,
    ) -> Sequence[retro_system_content_info_override] | None:
        if self._content is None:
            return None

        return self._content.overrides

    def run(self) -> None:
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
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        self._core.reset()
        self._raise_pending_exceptions("retro_reset")

    def set_controller_port_device(self, port: Port, device: int) -> None:
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        self._core.set_controller_port_device(port, device)
        self._raise_pending_exceptions("retro_set_controller_port_device", port, device)

    def cheat_reset(self) -> None:
        if self._is_exited or self.is_shutdown:
            raise CoreShutDownException()

        self._core.cheat_reset()
        self._raise_pending_exceptions("retro_cheat_reset")

    def cheat_set(self, index: int, enabled: bool, code: bytes | bytearray | str) -> None:
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
