import logging

from collections.abc import Iterable, Sequence
from logging import Logger
from types import TracebackType
from typing import Type, AnyStr, Any

from .api.av import *
from .api.content import *
from .api.environment import *
from .api.led import retro_led_interface, LedInterface, DictLedInterface
from .api.location import *
from .api.memory import retro_memory_map
from .api.microphone import *
from .api.midi import *
from .api.options import *
from .api.perf import *
from .api.power import retro_device_power, PowerState, DevicePower
from .api.savestate import *
from .api.throttle import *
from .api.log import *
from .api.message import retro_message, MessageInterface, LoggerMessageInterface, retro_message_ext
from .api.proc import retro_get_proc_address_interface, retro_proc_address_t
from .api.user import Language
from .api.vfs import retro_vfs_interface_info, FileSystemInterface, StandardFileSystemInterface, retro_vfs_interface
from .core import Core, CoreInterface
from .api.audio import *
from .api.input import *
from .api.video import *

from ._utils import *

Directory = str | bytes


class CoreShutDownException(Exception):
    def __init__(self, *args):
        super().__init__("Core has been shut down", *args)


def full_power() -> retro_device_power:
    return retro_device_power(PowerState.PLUGGED_IN, RETRO_POWERSTATE_NO_ESTIMATE, 100)


class Session:
    def __init__(
        self,
        core: Core | CDLL | str | PathLike,
        content: Content | SubsystemContent | None,
        environment: CompositeEnvironmentDriver
    ):
        match core:
            case Core():
                self._core = core
            case CDLL(dll):
                self._core = Core(dll)
            case str(path) | PathLike(path):
                self._core = Core(path)
            case _:
                raise TypeError(f"Expected core to be a Core, CDLL, or str; got {type(core).__name__}")

        self._content = content

        if not isinstance(environment, EnvironmentDriver):
            raise TypeError(f"Expected environment to be EnvironmentDriver; got {type(environment).__name__}")

        self._environment = environment

        self._content = content
        self._system_av_info: retro_system_av_info | None = None
        self._loaded_content: Sequence[LoadedContentFile] | None = None

        self._pending_callback_exceptions: list[BaseException] = []
        self._is_exited = False

    def __enter__(self):
        api_version = self._core.api_version()
        if api_version != RETRO_API_VERSION:
            raise RuntimeError(f"libretro.py is only compatible with API version {RETRO_API_VERSION}, but the core uses {api_version}")

        self._core.set_video_refresh(self._environment.video.refresh)
        self._core.set_audio_sample(self._environment.audio.sample)
        self._core.set_audio_sample_batch(self._environment.audio.sample_batch)
        self._core.set_input_poll(self._environment.input.poll)
        self._core.set_input_state(self._environment.input.state)
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
                    # TODO: Can a subsystem accept no-content?
                    loaded = self._core.load_game(None)
                case None, [info]:
                    # Loading exactly one regular content file
                    info: LoadedContentFile
                    loaded = self._core.load_game(info.info)
                case None, [*_]:
                    raise RuntimeError("Content driver returned multiple files, but not a subsystem that uses them all")
                case retro_subsystem_info(), [*infos]:
                    infos: Sequence[LoadedContentFile]
                    game_infos = tuple(i.info for i in infos)
                    loaded = self._core.load_game_special(subsystem.id, game_infos)
                case _, _:
                    raise RuntimeError("Failed to load content")

        if not loaded:
            raise RuntimeError("Failed to load game")

        self._loaded_content = content
        self._system_av_info = self._core.get_system_av_info()
        self._environment.video.set_system_av_info(self._system_av_info)

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

    def get_proc_address(self, sym: AnyStr, funtype: Type[ctypes._CFuncPtr] | None = None) -> retro_proc_address_t | Callable | None:
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

    @av_enable.setter
    def av_enable(self, value: AvEnableFlags):
        self._environment.av_enable = value

    @property
    def midi(self) -> MidiInterface:
        return self._environment.midi

    @property
    def serialization_quirks(self) -> SerializationQuirks | None:
        return self._environment.serialization_quirks

    @property
    def vfs(self) -> FileSystemInterface:
        return self._environment.vfs

    @property
    def led(self) -> LedInterface:
        return self._environment.led

    @property
    def max_users(self) -> int | None:
        return self._environment.input.max_users

    @max_users.setter
    def max_users(self, value: int):
        self._environment.input.max_users = value

    @property
    def fastforwarding_override(self) -> retro_fastforwarding_override | None:
        return self._environment.fastforwarding_override

    @property
    def content_info_overrides(self) -> Sequence[retro_system_content_info_override] | None:
        return self._environment.content.overrides

    @property
    def throttle_state(self) -> retro_throttle_state:
        return self._throttle_state


def default_session(
        core: str | Core | CDLL | PathLike,
        content: Content | SubsystemContent | ContentDriver | None = None,
        content_driver: ContentDriver | None = None,
        audio: AudioDriver | None = None,
        input_state: InputDriver | InputStateIterator | InputStateGenerator | None = None,
        video: VideoDriver | None = None,
        options: OptionDriver | Mapping[AnyStr, AnyStr] | None = None,
        overscan: bool = False,
        message: MessageInterface | None = None,
        system_dir: Directory | None = None,
        rumble: RumbleInterface | None = None,
        sensor: SensorInterface | None = None,
        log_callback: LogDriver | str | Logger | None = None,
        perf: PerfDriver | None = None,
        location: LocationInterface | None = None,
        core_assets_dir: Directory | None = None,
        save_dir: Directory | None = None,
        username: str | bytes | None = "libretro.py",
        language: Language = Language.ENGLISH,
        vfs: FileSystemInterface | int | None = None,
        led: LedInterface | None = None,
        av_enable: AvEnableFlags = AvEnableFlags.AUDIO | AvEnableFlags.VIDEO,
        midi: MidiInterface | None = None,
        target_refresh_rate: float = 60.0,
        preferred_hw: HardwareContext | None = HardwareContext.NONE,
        driver_switch_enable: bool = False,
        max_users: int = 8,
        throttle_state: retro_throttle_state | None = None,
        savestate_context: SavestateContext = SavestateContext.NORMAL,
        jit_capable: bool = True,
        mic_interface: MicrophoneDriver | MicrophoneInputIterator | MicrophoneInputGenerator | None = None,
        device_power: DevicePower | retro_device_power = full_power,
        playlist_dir: Directory | None = None,
        ) -> Session:
    """
    Returns a Session with default state objects.
    """

    core_impl: Core
    match core:
        case str(path) | PathLike(path) | CDLL(path):
            # Load a private copy of the core
            core_impl = Core(path)
        case Core() as c:
            # Use the provided core
            core_impl = c
        case _:
            raise TypeError(f"Expected core to be a string, path, Core, or CDLL; got {type(core).__name__}")

    logger = logging.getLogger('libretro')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    input_impl: InputDriver | None = None
    if isinstance(input_state, InputDriver):
        input_impl = input_state
    elif isinstance(input_state, Iterable):
        input_impl = GeneratorInputDriver(input_state)
    elif isinstance(input_state, Callable):
        input_impl = GeneratorInputDriver(input_state)

    options_impl: OptionDriver
    match options:
        case OptionDriver():
            options_impl = options
        case map if isinstance(map, Mapping):
            options_impl = DictOptionDriver(2, True, map)
        case None:
            options_impl = DictOptionDriver()
        case _:
            raise TypeError(f"Expected options to be an OptionState or a Mapping, not {type(options).__name__}")

    vfs_impl: FileSystemInterface
    match vfs:
        case FileSystemInterface() as v:
            vfs_impl = v
        case None:
            vfs_impl = StandardFileSystemInterface(logger=logger)
        case 1 | 2 | 3 as version:
            vfs_impl = StandardFileSystemInterface(version, logger=logger)
        case int() as i:
            raise ValueError(f"Expected a VFS version of 1, 2, or 3; got {i}")
        case _:
            raise TypeError(f"Expected vfs to be a FileSystemInterface or None, not {type(vfs).__name__}")

    mic_impl: MicrophoneDriver
    match mic_interface:
        case MicrophoneDriver() as m:
            mic_impl = m
        case m if callable(m):
            mic_impl = GeneratorMicrophoneDriver(m)
        case None:
            mic_impl = GeneratorMicrophoneDriver()
        case _:
            raise TypeError(f"Expected mic_interface to be a MicrophoneDriver or None, not {type(mic_interface).__name__}")

    power_impl: DevicePower
    match device_power:
        case retro_device_power() as p:
            power_impl = lambda: p
        case p if callable(p):
            power_impl = p
        case _:
            raise TypeError(f"Expected device_power to be a retro_device_power or a callable that returns one, not {type(device_power).__name__}")

    return Session(
        core=core_impl,
        audio=audio or ArrayAudioDriver(),
        input_state=input_impl or GeneratorInputDriver(),
        video=video or PillowVideoDriver(),
        content=content,
        content_driver=content_driver or StandardContentDriver(),
        overscan=overscan,
        message=message or LoggerMessageInterface(1, logger),
        options=options_impl,
        system_dir=system_dir,
        rumble=rumble or DefaultRumbleInterface(),
        sensor=sensor or GeneratorSensorInterface(),
        log_callback=log_callback or UnformattedLogDriver(),
        perf=perf or DefaultPerfDriver(),
        location=location or GeneratorLocationInterface(),
        core_assets_dir=core_assets_dir,
        save_dir=save_dir,
        username=username,
        language=language,
        vfs=vfs_impl,
        led=led or DictLedInterface(),
        av_enable=av_enable,
        midi=midi or GeneratorMidiInterface(),
        target_refresh_rate=target_refresh_rate,
        preferred_hw=preferred_hw,
        driver_switch_enable=driver_switch_enable,
        max_users=max_users,
        throttle_state=throttle_state or retro_throttle_state(ThrottleMode.NONE, 1.0),
        savestate_context=savestate_context,
        jit_capable=jit_capable,
        mic_interface=mic_impl,
        device_power=power_impl,
        playlist_dir=playlist_dir
    )


__all__ = [
    'Session',
    'default_session',
    'CoreShutDownException',
]
