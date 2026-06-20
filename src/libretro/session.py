"""
High-level harness that drives a :class:`.Core` through its libretro lifecycle.

.. seealso::

    :mod:`libretro.builder`
        The :class:`.SessionBuilder` factory used to construct a configured :class:`.Session`.
"""

import warnings
from collections.abc import Callable, Generator, Iterable, Iterator, Mapping, Sequence
from copy import deepcopy
from ctypes import CDLL
from logging import Logger
from os import PathLike
from types import TracebackType
from typing import Generic, Literal, overload, override

from libretro.api import (
    API_VERSION,
    AvEnableFlags,
    Content,
    HardwareContext,
    Port,
    SavestateContext,
    SubsystemContent,
    ThrottleMode,
    retro_device_power,
    retro_subsystem_info,
    retro_system_av_info,
    retro_system_content_info_override,
    retro_throttle_state,
)
from libretro.compat import TypeVar
from libretro.core import Core, CoreInterface
from libretro.drivers import (
    ArrayAudioDriver,
    AudioDriver,
    CameraDriver,
    CompositeEnvironmentDriver,
    ConstantPowerDriver,
    ContentDriver,
    DefaultFileSystemDriver,
    DefaultPerfDriver,
    DefaultTimingDriver,
    DefaultUserDriver,
    DictLedDriver,
    DictOptionDriver,
    DictRumbleDriver,
    DriverMap,
    FileSystemDriver,
    GeneratorMicrophoneDriver,
    GeneratorMidiDriver,
    InputDriver,
    InputStateGenerator,
    InputStateIterable,
    InputStateIterator,
    IterableInputDriver,
    IterableSensorDriver,
    LedDriver,
    LocationDriver,
    LogDriver,
    LoggerMessageDriver,
    MessageDriver,
    MicrophoneDriver,
    MidiDriver,
    MultiVideoDriver,
    OptionDriver,
    PathDriver,
    PerfDriver,
    PowerDriver,
    RumbleDriver,
    SensorDriver,
    SensorStateGenerator,
    SensorStateIterable,
    SensorStateIterator,
    StandardContentDriver,
    TempDirPathDriver,
    TimingDriver,
    UnformattedLogDriver,
    UserDriver,
    VideoDriver,
)
from libretro.drivers.types import Pollable
from libretro.error import (
    CallbackException,
    CallbackExceptionGroup,
    CoreShutDownException,
)

type _RequiredFactory[T] = Callable[[], T]
type _OptionalFactory[T] = Callable[[], T | None]

type _RequiredArg[T] = T | _RequiredFactory[T]
type _OptionalArg[T] = T | _OptionalFactory[T] | None

type CoreArg = Core | str | PathLike[str] | PathLike[bytes] | CDLL | _RequiredFactory[Core]
type AudioDriverArg[A: AudioDriver] = _RequiredArg[A]
type InputDriverArg[T: InputDriver] = (
    _RequiredArg[T] | InputStateGenerator | InputStateIterable | InputStateIterator
)
type VideoDriverArg[T: VideoDriver] = _RequiredArg[T] | DriverMap
type ContentArg = Content | SubsystemContent | _OptionalFactory[Content | SubsystemContent] | None
type ContentDriverArg[C: ContentDriver | None] = _OptionalArg[C]
type BoolArg = _OptionalArg[bool]
type MessageDriverArg[M: MessageDriver | None] = _OptionalArg[M] | Logger
type OptionDriverArg[O: OptionDriver | None] = (
    _OptionalArg[O] | Mapping[str, str] | Mapping[bytes, bytes] | Literal[0, 1, 2]
)
type PathDriverArg[P: PathDriver | None] = P | Callable[[Core], P | None] | None
type RumbleDriverArg[R: RumbleDriver | None] = _OptionalArg[R]
type SensorDriverArg[S: SensorDriver | None] = (
    _OptionalArg[S] | SensorStateGenerator | SensorStateIterable | SensorStateIterator
)
type CameraDriverArg[C: CameraDriver | None] = _OptionalArg[C]
type LogDriverArg[L: LogDriverArg | None] = _OptionalArg[L] | Logger
type PerfDriverArg[P: PerfDriver | None] = _OptionalArg[P]
type LocationDriverArg[L: LocationDriver | None] = _OptionalArg[L]
type UserDriverArg[U: UserDriver | None] = _OptionalArg[U]
type FileSystemArg[F: FileSystemDriver | None] = _OptionalArg[F] | Literal[1, 2, 3]
type LedDriverArg[L: LedDriver | None] = _OptionalArg[L]
type AvEnableFlagsArg = _OptionalArg[AvEnableFlags]
type MidiDriverArg[M: MidiDriver | None] = _OptionalArg[M]
type TimingDriverArg[T: TimingDriver | None] = _OptionalArg[T]
type FloatArg = _OptionalArg[float | int]
type HardwareContextArg = _OptionalArg[HardwareContext]
type ThrottleStateArg = _OptionalArg[retro_throttle_state]
type SavestateContextArg = _OptionalArg[SavestateContext]
type MicDriverArg[M: MicrophoneDriver | None] = _OptionalArg[M]
type PowerDriverArg[P: PowerDriver | None] = _OptionalArg[P] | retro_device_power


def _to_audio_driver[A: AudioDriver](audio: AudioDriverArg[A]) -> A:
    match audio:
        case Callable():
            return audio()
        case AudioDriver():
            return audio
        case _:
            raise TypeError(
                f"Expected an AudioDriver or a Callable that returns one, got {type(audio)}"
            )


@overload
def _to_input_driver[I: InputDriver](input: I | Callable[[], I]) -> I: ...


@overload
def _to_input_driver(
    input: InputStateGenerator | InputStateIterable | InputStateIterator,
) -> IterableInputDriver: ...


def _to_input_driver[I: InputDriver](input: InputDriverArg[I]) -> I | IterableInputDriver:
    match input:
        case Generator():
            return IterableInputDriver(input)
        case Callable() as func:
            # Either a generator or a driver type;
            def _generate():
                match func():
                    case Generator() | Iterable() | Iterator() as gen:
                        return IterableInputDriver(gen)
                    case InputDriver() as driver:
                        return driver
                    case err:
                        raise TypeError(
                            f"Expected a generator, an iterable, an iterator, or an InputDriver from the callable, got {type(err).__name__}"
                        )

            return _generate()
        case InputDriver():
            return input
        case _:
            raise TypeError(
                f"Expected InputDriver or a callable that returns one, a callable or iterator that yields InputState, or DEFAULT; got {type(input).__name__}"
            )


@overload
def _to_video_driver[V: VideoDriver](video: Callable[[], V] | V) -> V: ...


@overload
def _to_video_driver[V: VideoDriver](video: DriverMap) -> MultiVideoDriver: ...


def _to_video_driver[V: VideoDriver](video: VideoDriverArg[V]) -> V | MultiVideoDriver:
    match video:
        case Callable():
            return video()
        case Mapping():
            if HardwareContext.NONE not in video:
                raise ValueError("A driver for HardwareContext.NONE is required")

            if not all(isinstance(k, HardwareContext) for k in video.keys()):
                raise TypeError("Each key in the provided driver map must be a HardwareContext")

            if not all(callable(v) for v in video.values()):
                raise TypeError(
                    "Each value in the provided driver map must be a callable that returns a VideoDriver"
                )

            return MultiVideoDriver(video)
        case VideoDriver():
            return video
        case _:
            raise TypeError(
                f"Expected a VideoDriver, a callable that returns one, or a map of HardwareContexts to Callables; got {type(video).__name__}"
            )


def _to_content_driver[C: ContentDriver](content: ContentDriverArg[C]) -> C | None:
    match content:
        case Callable():
            return content()
        case ContentDriver():
            return content
        case None:
            return None
        case _:
            raise TypeError(
                f"Expected ContentDriver, a callable that returns one, or None; got {type(content).__name__}"
            )


@overload
def _to_message_driver[M: MessageDriver](message: M | Callable[[], M]) -> M: ...


@overload
def _to_message_driver(message: None | Callable[[], None]) -> None: ...


@overload
def _to_message_driver[M: MessageDriver](message: Callable[[], M | None]) -> M | None: ...


@overload
def _to_message_driver(message: Logger) -> LoggerMessageDriver: ...


def _to_message_driver[M: MessageDriver](
    message: MessageDriverArg[M],
) -> M | LoggerMessageDriver | None:
    match message:
        case Callable():
            return message()
        case MessageDriver() | None:
            return message
        case Logger() as logger:
            return LoggerMessageDriver(logger=logger)
        case _:
            raise TypeError(
                f"Expected MessageInterface, a callable that returns one, or None; got {type(message).__name__}"
            )


@overload
def _to_option_driver[O: OptionDriver](options: O | Callable[[], O]) -> O: ...


@overload
def _to_option_driver(options: None | Callable[[], None]) -> None: ...


@overload
def _to_option_driver[O: OptionDriver](options: Callable[[], O | None]) -> O | None: ...


@overload
def _to_option_driver[O: OptionDriver](
    options: Mapping[str, str] | Mapping[bytes, bytes] | Literal[0, 1, 2],
) -> DictOptionDriver: ...


def _to_option_driver[O: OptionDriver](options: OptionDriverArg[O]) -> O | DictOptionDriver | None:
    match options:
        case Callable():
            return options()
        case OptionDriver() | None:
            return options
        case Mapping() as options:
            all_str = all(isinstance(k, str) and isinstance(v, str) for k, v in options.items())
            all_bytes = all(
                isinstance(k, bytes) and isinstance(v, bytes) for k, v in options.items()
            )
            if not (all_str or all_bytes):
                raise ValueError("All keys and values must be either str or bytes")

            return DictOptionDriver(2, True, options)
        case 0 | 1 | 2 as version:
            return DictOptionDriver(version)
        case _:
            raise TypeError(
                f"Expected an OptionDriver, a Callable that returns one, a Mapping, an API version, or None; got {type(options).__name__}"
            )


def _to_path_driver[P: PathDriver](path: PathDriverArg[P], core: Core) -> P | None:
    match path:
        case Callable():
            return path(core)
        case PathDriver() | None:
            return path
        case _:
            raise TypeError(
                f"Expected PathDriver, a callable that returns one, or None; got {type(path)}"
            )


def _to_rumble_driver[R: RumbleDriver](rumble: RumbleDriverArg[R]) -> R | None:
    match rumble:
        case Callable():
            return rumble()
        case RumbleDriver() | None:
            return rumble
        case _:
            raise TypeError(
                f"Expected RumbleDriver, a callable that returns one, or None; got {type(rumble).__name__}"
            )


@overload
def _to_sensor_driver[S: SensorDriver](sensor: S | Callable[[], S]) -> S: ...
@overload
def _to_sensor_driver(sensor: None | Callable[[], None]) -> None: ...
@overload
def _to_sensor_driver[S: SensorDriver](sensor: Callable[[], S | None]) -> S | None: ...


@overload
def _to_sensor_driver(
    sensor: SensorStateGenerator | SensorStateIterable | SensorStateIterator,
) -> IterableSensorDriver: ...


def _to_sensor_driver[S: SensorDriver](
    sensor: SensorDriverArg[S],
) -> S | None | IterableSensorDriver:
    match sensor:
        case Generator() | Iterable() | Iterator():
            return IterableSensorDriver(sensor)
        case Callable() as func:
            # Either a generator or a driver type
            def _generate():
                match func():
                    case Generator() | Iterable() | Iterator() as gen:
                        return IterableSensorDriver(gen)
                    case SensorDriver() as driver:
                        return driver
                    case err:
                        raise TypeError(
                            f"Expected a generator, an iterable, an iterator, or a SensorDriver from the callable, got {type(err).__name__}"
                        )

            return _generate()
        case SensorDriver() | None:
            return sensor
        case _:
            raise TypeError(
                f"Expected SensorDriver or a callable that returns one, a callable or iterator that yields SensorState; got {type(input).__name__}"
            )


def _to_camera_driver[C: CameraDriver](camera: CameraDriverArg[C]) -> C | None:
    match camera:
        case Callable():
            return camera()
        case CameraDriver() | None:
            return camera
        case _:
            raise TypeError(
                f"Expected a CameraDriver, a callable that returns one, or None; got {type(camera)}"
            )


@overload
def _to_log_driver[L: LogDriver](log: L | Callable[[], L]) -> L: ...


@overload
def _to_log_driver(log: None | Callable[[], None]) -> None: ...


@overload
def _to_log_driver[L: LogDriver](log: Callable[[], L | None]) -> L | None: ...


@overload
def _to_log_driver(log: Logger) -> UnformattedLogDriver: ...


def _to_log_driver[L: LogDriver](log: LogDriverArg[L]) -> L | None | UnformattedLogDriver:
    match log:
        case Callable():
            return log()
        case LogDriver() | None:
            return log
        case Logger():
            return UnformattedLogDriver(log)
        case _:
            raise TypeError(
                f"Expected LogDriver, a callable that returns one, or None; got {type(log).__name__}"
            )


def _to_perf_driver[P: PerfDriver](perf: PerfDriverArg[P]) -> P | None:
    match perf:
        case Callable():
            return perf()
        case PerfDriver() | None:
            return perf
        case _:
            raise TypeError(
                f"Expected PerfDriver, a callable that returns one, or None; got {type(perf)}"
            )


def _to_location_driver[L: LocationDriver](location: LocationDriverArg[L]) -> L | None:
    match location:
        case Callable():
            return location()
        case LocationDriver() | None:
            return location
        case _:
            raise TypeError(
                f"Expected LocationDriver, a callable that returns one, or None; got {type(location)}"
            )


def _to_user_driver[U: UserDriver](user: UserDriverArg[U]) -> U | None:
    match user:
        case Callable():
            return user()
        case UserDriver() | None:
            return user
        case _:
            raise TypeError(
                f"Expected UserDriver, a callable that returns one, or None; got {type(user).__name__}"
            )


@overload
def _to_vfs_driver[F: FileSystemDriver](vfs: F | Callable[[], F]) -> F: ...


@overload
def _to_vfs_driver[F: FileSystemDriver](vfs: None | Callable[[], None]) -> None: ...


@overload
def _to_vfs_driver[F: FileSystemDriver](vfs: Callable[[], F | None]) -> F | None: ...


@overload
def _to_vfs_driver(vfs: Literal[1, 2, 3]) -> DefaultFileSystemDriver: ...


def _to_vfs_driver[F: FileSystemDriver](
    vfs: FileSystemArg[F],
) -> F | DefaultFileSystemDriver | None:
    match vfs:
        case Callable():
            return vfs()
        case FileSystemDriver() | None:
            return vfs
        case 1 | 2 | 3:
            return DefaultFileSystemDriver(vfs)
        case _:
            raise TypeError(
                f"Expected FileSystemInterface, a callable that returns one, or None; got {type(vfs).__name__}"
            )


def _to_led_driver[L: LedDriver](led: LedDriverArg[L]) -> L | None:
    match led:
        case Callable():
            return led()
        case LedDriver() | None:
            return led
        case _:
            raise TypeError(
                f"Expected LedDriver, a callable that returns one, or None; got {type(led).__name__}"
            )


def _to_midi_driver[M: MidiDriver](midi: MidiDriverArg[M]) -> M | None:
    match midi:
        case Callable():
            return midi()
        case MidiDriver() | None:
            return midi
        case _:
            raise TypeError(
                f"Expected MidiDriver, a callable that returns one, or None; got {type(midi).__name__}"
            )


def _to_timing_driver[T: TimingDriver](timing: TimingDriverArg[T]) -> T | None:
    match timing:
        case Callable():
            return timing()
        case TimingDriver() | None:
            return timing
        case _:
            raise TypeError(
                f"Expected TimingDriver, a callable that returns one, DEFAULT, or None; got {type(timing).__name__}"
            )


def _to_mic_driver[M: MicrophoneDriver](mic: MicDriverArg[M]) -> M | None:
    match mic:
        case Callable():
            return mic()
        case MicrophoneDriver() | None:
            return mic
        case _:
            raise TypeError(
                f"Expected MicrophoneDriver, a callable that returns one, DEFAULT, or None; got {type(mic).__name__}"
            )


@overload
def _to_power_driver[P: PowerDriver](power: P | Callable[[], P]) -> P: ...


@overload
def _to_power_driver(power: None | Callable[[], None]) -> None: ...


@overload
def _to_power_driver[P: PowerDriver](power: Callable[[], P | None]) -> P | None: ...


@overload
def _to_power_driver(power: retro_device_power) -> ConstantPowerDriver: ...


def _to_power_driver[P: PowerDriver](power: PowerDriverArg[P]) -> P | ConstantPowerDriver | None:
    match power:
        case retro_device_power():
            return ConstantPowerDriver(power)
        case Callable():
            return power()
        case PowerDriver() | None:
            return power
        case _:
            raise TypeError(
                f"Expected a PowerDriver, retro_device_power, a callable that returns one, or None; got {type(power).__name__}"
            )


def _default_timing_driver():
    return DefaultTimingDriver(retro_throttle_state(ThrottleMode.UNBLOCKED, 0.0), 60.0)


# These type parameters are declared the verbose way
# (rather than with PEP 695 ``class Session[...]`` syntax)
# so that each can carry a PEP 696 ``default``
# without requiring the syntax introduced in Python 3.13.
# The defaults mirror the driver each constructor argument falls back to,
# which lets Pyright resolve the type parameter even when an argument is given
# in a form that doesn't carry it
# (e.g. a ``DriverMap`` for ``video``, which is always wrapped in a ``MultiVideoDriver``).
# PEP 696 defaults in native ``[...]`` syntax require Python 3.13+,
# so they are spelled with ``typing(_extensions).TypeVar`` to keep 3.12 support.
# Once we drop Python 3.12 support at some point, we can simplify this syntax.
_Audio = TypeVar("_Audio", bound=AudioDriver, default=ArrayAudioDriver)
_Input = TypeVar("_Input", bound=InputDriver, default=IterableInputDriver)
_Video = TypeVar("_Video", bound=VideoDriver, default=MultiVideoDriver)
_Content = TypeVar("_Content", bound=ContentDriver | None, default=StandardContentDriver)
_Message = TypeVar("_Message", bound=MessageDriver | None, default=LoggerMessageDriver)
_Option = TypeVar("_Option", bound=OptionDriver | None, default=DictOptionDriver)
_Path = TypeVar("_Path", bound=PathDriver | None, default=TempDirPathDriver)
_Rumble = TypeVar("_Rumble", bound=RumbleDriver | None, default=DictRumbleDriver)
_Sensor = TypeVar("_Sensor", bound=SensorDriver | None, default=IterableSensorDriver)
_Log = TypeVar("_Log", bound=LogDriver | None, default=UnformattedLogDriver)
_Perf = TypeVar("_Perf", bound=PerfDriver | None, default=DefaultPerfDriver)
_User = TypeVar("_User", bound=UserDriver | None, default=DefaultUserDriver)
_Vfs = TypeVar("_Vfs", bound=FileSystemDriver | None, default=DefaultFileSystemDriver)
_Led = TypeVar("_Led", bound=LedDriver | None, default=DictLedDriver)
_Midi = TypeVar("_Midi", bound=MidiDriver | None, default=GeneratorMidiDriver)
_Timing = TypeVar("_Timing", bound=TimingDriver | None, default=DefaultTimingDriver)
_Mic = TypeVar("_Mic", bound=MicrophoneDriver | None, default=GeneratorMicrophoneDriver)
_Power = TypeVar("_Power", bound=PowerDriver | None, default=ConstantPowerDriver)


class Session(
    CompositeEnvironmentDriver,
    Generic[
        _Audio,
        _Input,
        _Video,
        _Content,
        _Message,
        _Option,
        _Path,
        _Rumble,
        _Sensor,
        _Log,
        _Perf,
        _User,
        _Vfs,
        _Led,
        _Midi,
        _Timing,
        _Mic,
        _Power,
    ],
):
    """
    A configured libretro core paired with the drivers that satisfy its environment calls.

    Use :class:`Session` as a context manager:
    entering it loads the core (and game, if any) and wires up callbacks;
    exiting it unloads the game and deinitializes the core.
    Each constructor argument selects which driver implementation to use for one libretro subsystem.

    .. seealso::

        :class:`.SessionBuilder`
            Fluent builder that constructs a :class:`Session` with sensible defaults.
    """

    _audio: _Audio
    _input: _Input
    _video: _Video
    _content: _Content
    _message: _Message
    _options: _Option
    _path: _Path
    _rumble: _Rumble
    _sensor: _Sensor
    _log_driver: _Log
    _perf: _Perf
    _user: _User
    _vfs: _Vfs
    _led: _Led
    _midi: _Midi
    _timing: _Timing
    _mic: _Mic
    _device_power: _Power

    def __init__(
        self,
        /,
        core: Core | CDLL | str | PathLike[str] | PathLike[bytes],
        game: Content | SubsystemContent | None,
        audio: AudioDriverArg[_Audio] = ArrayAudioDriver,
        input: InputDriverArg[_Input] = IterableInputDriver,
        video: VideoDriverArg[_Video] = MultiVideoDriver,
        content: ContentDriverArg[_Content] = StandardContentDriver,
        overscan: bool | None = False,
        message: MessageDriverArg[_Message] = LoggerMessageDriver,
        options: OptionDriverArg[_Option] = DictOptionDriver,
        path: PathDriverArg[_Path] = TempDirPathDriver,
        rumble: RumbleDriverArg[_Rumble] = DictRumbleDriver,
        sensor: SensorDriverArg[_Sensor] = IterableSensorDriver,
        camera: CameraDriverArg[CameraDriver] = None,
        log: LogDriverArg[_Log] = UnformattedLogDriver,
        perf: PerfDriverArg[_Perf] = DefaultPerfDriver,
        location: LocationDriverArg[LocationDriver] = None,
        user: UserDriverArg[_User] = DefaultUserDriver,
        vfs: FileSystemArg[_Vfs] = DefaultFileSystemDriver,
        led: LedDriverArg[_Led] = DictLedDriver,
        av_enable: AvEnableFlags | None = AvEnableFlags.ALL,
        midi: MidiDriverArg[_Midi] = GeneratorMidiDriver,
        timing: TimingDriverArg[_Timing] = _default_timing_driver,
        preferred_hw: HardwareContext | None = None,
        driver_switch_enable: bool | None = False,
        savestate_context: SavestateContext | None = SavestateContext.NORMAL,
        jit_capable: bool | None = True,
        mic: MicDriverArg[_Mic] = GeneratorMicrophoneDriver,
        device_power: PowerDriverArg[_Power] = ConstantPowerDriver,
    ):
        """
        Initialize the session with a core, optional game content, and driver implementations.

        Each driver argument accepts the configured driver directly,
        a zero-argument callable that produces one (called here, during construction),
        and—where noted—a convenience value
        that is wrapped in a sensible default driver.
        Optional drivers also accept :obj:`None`
        to leave the corresponding subsystem unavailable to the core.
        The defaults documented below match those of the equivalent
        :class:`.SessionBuilder` ``with_`` methods.

        :param core: The core to load. May be one of the following:

            :class:`.Core`
                Will be used as-is.

            :class:`str`, :class:`~os.PathLike`
                Will load a :class:`.Core` from this path.

            :class:`~ctypes.CDLL`
                Will load a :class:`.Core` from this already-opened library.

        :param game: The content to load, managed by the configured ``content`` driver
            and passed to ``retro_load_game`` (or ``retro_load_game_special``).
            May be one of the following:
            :class:`str`, :class:`~os.PathLike`
                A single content file, loaded without enabling a subsystem.

            :class:`zipfile.Path`
                A single content file within a ZIP archive, loaded without enabling a subsystem.

            :class:`bytes`, :class:`bytearray`, :class:`memoryview`, :class:`~collections.abc.Buffer`
                A single unnamed content buffer, exposed without enabling a subsystem.

            :class:`.retro_game_info`
                Passed to the core as-is, without enabling a subsystem.

            :class:`.SubsystemContent`
                Enables a subsystem and loads its associated content files.

            :obj:`None`
                Loads the core without content and without enabling a subsystem;
                ``retro_load_game`` **is** still called,
                so the core must support contentless operation.

        :param audio: The audio driver. May be one of the following:

            :class:`.AudioDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.AudioDriver`
                Zero-argument function that returns an :class:`.AudioDriver`.

            Defaults to an :class:`.ArrayAudioDriver` with its default configuration.

        :param input: The input driver. May be one of the following:

            :class:`.InputDriver`
                Will be used as-is.

            :class:`~collections.abc.Generator`, :class:`~collections.abc.Iterable`, :class:`~collections.abc.Iterator`
                Will be wrapped in an :class:`.IterableInputDriver`
                that yields :class:`.InputPollResult` values.

            :class:`~collections.abc.Callable` () -> :class:`.InputDriver` | iterable
                Zero-argument function that returns either an :class:`.InputDriver`
                or an iterable/iterator/generator of :class:`.InputPollResult` values.

            Defaults to an :class:`.IterableInputDriver` with its default configuration.

        :param video: The video driver. May be one of the following:

            :class:`.VideoDriver`
                Will be used as-is.

            :class:`~collections.abc.Mapping` [:class:`.HardwareContext`, :class:`~collections.abc.Callable` () -> :class:`.VideoDriver`]
                Will be wrapped in a :class:`.MultiVideoDriver` built from the provided driver map.

            :class:`~collections.abc.Callable` () -> :class:`.VideoDriver`
                Zero-argument function that returns a :class:`.VideoDriver`.

            Defaults to a :class:`.MultiVideoDriver` with its default configuration.

        :param content: The content driver that resolves and loads ``game``.
            May be one of the following:

            :class:`.ContentDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.ContentDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.ContentDriver` or :obj:`None`.

            :obj:`None`
                No content driver will be used; ``game`` will not be loaded.

            Defaults to a :class:`.StandardContentDriver` with its default configuration.

        :param overscan: The overscan flag to report to the core. May be one of the following:

            :class:`bool`
                Will be reported to the core as-is.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            Defaults to :obj:`False`.

        :param message: The message driver that handles ``RETRO_ENVIRONMENT_SET_MESSAGE``.
            May be one of the following:

            :class:`.MessageDriver`
                Will be used as-is.

            :class:`~logging.Logger`
                Will be wrapped in a :class:`.LoggerMessageDriver`
                that forwards messages to the given logger.

            :class:`~collections.abc.Callable` () -> :class:`.MessageDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.MessageDriver` or :obj:`None`.

            :obj:`None`
                The environment calls that :class:`.MessageDriver` normally implements
                will be unavailable to the core.

            Defaults to a :class:`.LoggerMessageDriver` with its default configuration.

        :param options: The core-options driver. May be one of the following:

            :class:`.OptionDriver`
                Will be used as-is.

            :class:`~collections.abc.Mapping` [:obj:`~typing.AnyStr`, :obj:`~typing.AnyStr`]
                Will initialize a :class:`.DictOptionDriver` with the provided options
                and API version 2.
                All keys and values must be either :class:`str` or :class:`bytes`;
                mixing the two is not allowed.

            ``0``, ``1``, or ``2``
                Will initialize a :class:`.DictOptionDriver` with no initial options
                using the provided API version.

            :class:`~collections.abc.Callable` () -> :class:`.OptionDriver` | :obj:`None`
                Zero-argument function that returns an :class:`.OptionDriver` or :obj:`None`.

            :obj:`None`
                The environment calls that :class:`.OptionDriver` normally implements
                will be unavailable to the core.

            Defaults to a :class:`.DictOptionDriver` with API version 2 and no initial options.

        :param path: The path driver that supplies system/save/asset directory paths.
            May be one of the following:

            :class:`.PathDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` (:class:`.Core`) -> :class:`.PathDriver` | :obj:`None`
                One-argument function that accepts the configured :class:`.Core`
                and returns a :class:`.PathDriver` or :obj:`None`.

            :obj:`None`
                The environment calls that :class:`.PathDriver` normally implements
                will be unavailable to the core.

            Defaults to a :class:`.TempDirPathDriver`
            configured with an unspecified temporary directory and the configured core's path.

        :param rumble: The rumble driver. May be one of the following:

            :class:`.RumbleDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.RumbleDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.RumbleDriver` or :obj:`None`.

            :obj:`None`
                No rumble driver will be used,
                and any rumble interfaces the core exposes will not function.

            Defaults to a :class:`.DictRumbleDriver` with no initial state.

        :param sensor: The motion-sensor driver. May be one of the following:

            :class:`.SensorDriver`
                Will be used as-is.

            :class:`~collections.abc.Iterable`, :class:`~collections.abc.Iterator`
                Will be wrapped in an :class:`.IterableSensorDriver`
                that yields elements as described in :class:`.IterableSensorDriver`.

            :class:`~collections.abc.Callable` () -> :class:`.SensorDriver` | iterable
                Zero-argument function that returns either a :class:`.SensorDriver`
                or an iterable/iterator/generator
                as described in :class:`.IterableSensorDriver`.

            :obj:`None`
                The environment calls and interfaces that :class:`.SensorDriver` normally implements
                will be unavailable to the core.

            Defaults to an :class:`.IterableSensorDriver`
            whose sensor state can be configured but produces no nonzero readings.

        :param camera: The camera driver. May be one of the following:

            :class:`.CameraDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.CameraDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.CameraDriver` or :obj:`None`.

            :obj:`None`
                The camera interface will be unavailable to the core.

            Defaults to :obj:`None`.

        :param log: The log driver. May be one of the following:

            :class:`.LogDriver`
                Will be used as-is.

            :class:`~logging.Logger`
                Will be wrapped in an :class:`.UnformattedLogDriver`
                that forwards core log messages to the given logger.

            :class:`~collections.abc.Callable` () -> :class:`.LogDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.LogDriver` or :obj:`None`.

            :obj:`None`
                The log interface will be unavailable to the core.

            Defaults to an :class:`.UnformattedLogDriver` with its default configuration.

        :param perf: The performance-counter driver. May be one of the following:

            :class:`.PerfDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.PerfDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.PerfDriver` or :obj:`None`.

            :obj:`None`
                The performance interface will be unavailable to the core.

            Defaults to a :class:`.DefaultPerfDriver` with its default configuration.

        :param location: The geolocation driver. May be one of the following:

            :class:`.LocationDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.LocationDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.LocationDriver` or :obj:`None`.

            :obj:`None`
                The location interface will be unavailable to the core.

            Defaults to :obj:`None`.

        :param user: The user driver that exposes username and language to the core.
            May be one of the following:

            :class:`.UserDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.UserDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.UserDriver` or :obj:`None`.

            :obj:`None`
                The environment calls that :class:`.UserDriver` normally implements
                will be unavailable to the core.

            Defaults to a :class:`.DefaultUserDriver` with its default configuration.

        :param vfs: The virtual filesystem driver. May be one of the following:

            :class:`.FileSystemDriver`
                Will be used as-is.

            ``1``, ``2``, or ``3``
                Will use a :class:`.DefaultFileSystemDriver` with the given API version.

            :class:`~collections.abc.Callable` () -> :class:`.FileSystemDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.FileSystemDriver` or :obj:`None`.

            :obj:`None`
                The VFS interface will be unavailable to the core.

            Defaults to a :class:`.DefaultFileSystemDriver` with its default configuration.

        :param led: The LED driver. May be one of the following:

            :class:`.LedDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.LedDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.LedDriver` or :obj:`None`.

            :obj:`None`
                The LED interface will be unavailable to the core.

            Defaults to a :class:`.DictLedDriver` with its default configuration.

        :param av_enable: The audio/video enable mask to report to the core.
            May be one of the following:

            :class:`.AvEnableFlags`
                Will be reported to the core as-is.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            Defaults to :attr:`.AvEnableFlags.ALL`.

        :param midi: The MIDI driver. May be one of the following:

            :class:`.MidiDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.MidiDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.MidiDriver` or :obj:`None`.

            :obj:`None`
                The MIDI interface will be unavailable to the core.

            Defaults to a :class:`.GeneratorMidiDriver` with its default configuration.

        :param timing: The timing driver. May be one of the following:

            :class:`.TimingDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.TimingDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.TimingDriver` or :obj:`None`.

            :obj:`None`
                The corresponding environment calls will be unavailable to the core.

            Defaults to a :class:`.DefaultTimingDriver` running unblocked at 60 FPS.

        :param preferred_hw: The preferred hardware context to report to the core.
            May be one of the following:

            :class:`.HardwareContext`
                Will be reported to the core as-is.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            Defaults to :obj:`None`.

        :param driver_switch_enable: Whether the core may switch hardware rendering drivers
            at runtime. May be one of the following:

            :class:`bool`
                Will be reported to the core as-is.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            Defaults to :obj:`False`.

        :param savestate_context: The savestate context to report to the core.
            May be one of the following:

            :class:`.SavestateContext`
                Will be reported to the core as-is.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            Defaults to :attr:`.SavestateContext.NORMAL`.

        :param jit_capable: Whether the host environment is JIT-capable.
            May be one of the following:

            :class:`bool`
                Will be reported to the core as-is.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            Defaults to :obj:`True`.

        :param mic: The microphone driver. May be one of the following:

            :class:`.MicrophoneDriver`
                Will be used as-is.

            :class:`~collections.abc.Callable` () -> :class:`.MicrophoneDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.MicrophoneDriver` or :obj:`None`.

            :obj:`None`
                The microphone interface will be unavailable to the core.

            Defaults to a :class:`.GeneratorMicrophoneDriver` with its default configuration.

        :param device_power: The power driver that reports device battery state.
            May be one of the following:

            :class:`.PowerDriver`
                Will be used as-is.

            :class:`.retro_device_power`
                Will be wrapped in a :class:`.ConstantPowerDriver` that always reports this state.

            :class:`~collections.abc.Callable` () -> :class:`.PowerDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.PowerDriver` or :obj:`None`.

            :obj:`None`
                The power interface will be unavailable to the core.

            Defaults to a :class:`.ConstantPowerDriver`
            reporting a fully charged, plugged-in device.

        :raises TypeError: If ``core`` is not a :class:`.Core`,
            :class:`ctypes.CDLL`, or a filesystem path,
            or if any driver argument is not one of its permitted types.
        :raises ValueError: If ``video`` is given a driver map without an entry
            for :attr:`.HardwareContext.NONE`,
            or if ``options`` is given a :class:`~collections.abc.Mapping`
            whose keys and values are not all :class:`str` or all :class:`bytes`.
        """
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
        super().__init__(
            audio=_to_audio_driver(audio),
            input=_to_input_driver(input),
            video=_to_video_driver(video),
            content=_to_content_driver(content),
            overscan=overscan,
            message=_to_message_driver(message),
            options=_to_option_driver(options),
            path=_to_path_driver(path, self._core),
            rumble=_to_rumble_driver(rumble),
            sensor=_to_sensor_driver(sensor),
            camera=_to_camera_driver(camera),
            log=_to_log_driver(log),
            perf=_to_perf_driver(perf),
            location=_to_location_driver(location),
            user=_to_user_driver(user),
            vfs=_to_vfs_driver(vfs),
            led=_to_led_driver(led),
            av_enable=av_enable,
            midi=_to_midi_driver(midi),
            timing=_to_timing_driver(timing),
            preferred_hw=preferred_hw,
            driver_switch_enable=driver_switch_enable,
            savestate_context=savestate_context,
            jit_capable=jit_capable,
            mic=_to_mic_driver(mic),
            device_power=_to_power_driver(device_power),
        )

        self._game = game

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
    @override
    def audio(self) -> _Audio:
        return self._audio

    @property
    @override
    def input(self) -> _Input:
        return self._input

    @property
    @override
    def video(self) -> _Video:
        return self._video

    @property
    @override
    def content(self) -> _Content:
        return self._content

    @property
    @override
    def message(self) -> _Message:
        return self._message

    @property
    @override
    def options(self) -> _Option:
        return self._options

    @property
    @override
    def path(self) -> _Path:
        return self._path

    @property
    @override
    def rumble(self) -> _Rumble:
        return self._rumble

    @property
    @override
    def sensor(self) -> _Sensor:
        return self._sensor

    @property
    @override
    def log(self) -> _Log:
        return self._log_driver

    @property
    @override
    def perf(self) -> _Perf:
        return self._perf

    @property
    @override
    def user(self) -> _User:
        return self._user

    @property
    @override
    def vfs(self) -> _Vfs:
        return self._vfs

    @property
    @override
    def led(self) -> _Led:
        return self._led

    @property
    @override
    def midi(self) -> _Midi:
        return self._midi

    @property
    @override
    def timing(self) -> _Timing:
        return self._timing

    @property
    @override
    def mic(self) -> _Mic:
        return self._mic

    @property
    @override
    def power(self) -> _Power:
        return self._device_power

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
