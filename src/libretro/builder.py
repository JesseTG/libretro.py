"""
Fluent builder for assembling a configured :class:`.Session` from drivers and a core.

.. seealso::

    :mod:`libretro.session`
        The :class:`.Session` produced by this builder.
"""

from __future__ import annotations

from collections.abc import Buffer, Callable, Generator, Iterable, Iterator, Mapping
from ctypes import CDLL
from enum import Enum, auto
from logging import Logger
from os import PathLike
from typing import Literal, Self, TypedDict
from zipfile import Path as ZipPath

from libretro.api import (
    AvEnableFlags,
    Content,
    HardwareContext,
    PowerState,
    SavestateContext,
    SubsystemContent,
    ThrottleMode,
    retro_device_power,
    retro_game_info,
    retro_throttle_state,
)
from libretro.compat import deprecated
from libretro.core import Core
from libretro.drivers import (
    ArrayAudioDriver,
    AudioDriver,
    CameraDriver,
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
from libretro.session import Session


class _DefaultType(Enum):
    DEFAULT = auto()


DEFAULT = _DefaultType.DEFAULT
"""
A placeholder that indicates the default value for one of :obj:`SessionBuilder`'s arguments.
When passed to one of :obj:`.SessionBuilder`'s ``with_`` methods,
it will use the default driver or argument configuration
unless otherwise noted.
"""

type Default = Literal[_DefaultType.DEFAULT]

type _RequiredFactory[T] = Callable[[], T]
type _OptionalFactory[T] = Callable[[], T | None]

type _RequiredArg[T] = T | _RequiredFactory[T]
type _OptionalArg[T] = T | _OptionalFactory[T] | Default | None


def _nothing():
    pass


CoreArg = Core | str | PathLike[str] | PathLike[bytes] | CDLL | _RequiredFactory[Core]
type AudioDriverArg = _RequiredArg[AudioDriver] | Default
type InputDriverArg = (
    _RequiredArg[InputDriver]
    | InputStateGenerator
    | InputStateIterable
    | InputStateIterator
    | Default
)
type VideoDriverArg = _RequiredArg[VideoDriver] | DriverMap | Default
type ContentArg = Content | SubsystemContent | _OptionalFactory[Content | SubsystemContent] | None
type ContentDriverArg = _OptionalArg[ContentDriver]
type BoolArg = _OptionalArg[bool]
type MessageDriverArg = _OptionalArg[MessageDriver] | Logger
type OptionDriverArg = (
    _OptionalArg[OptionDriver] | Mapping[str, str] | Mapping[bytes, bytes] | Literal[0, 1, 2]
)
type PathDriverArg = PathDriver | Callable[[Core], PathDriver | None] | Default | None
type RumbleDriverArg = _OptionalArg[RumbleDriver]
type SensorDriverArg = (
    _OptionalArg[SensorDriver] | SensorStateGenerator | SensorStateIterable | SensorStateIterator
)
type LogDriverArg = _OptionalArg[LogDriver] | Logger
type PerfDriverArg = _OptionalArg[PerfDriver]
type LocationDriverArg = _OptionalArg[LocationDriver]
type UserDriverArg = _OptionalArg[UserDriver]
type FileSystemArg = _OptionalArg[FileSystemDriver] | Literal[1, 2, 3]
type LedDriverArg = _OptionalArg[LedDriver]
type AvEnableFlagsArg = _OptionalArg[AvEnableFlags]
type MidiDriverArg = _OptionalArg[MidiDriver]
type TimingDriverArg = _OptionalArg[TimingDriver]
type FloatArg = _OptionalArg[float | int]
type HardwareContextArg = _OptionalArg[HardwareContext]
type ThrottleStateArg = _OptionalArg[retro_throttle_state]
type SavestateContextArg = _OptionalArg[SavestateContext]
type MicDriverArg = _OptionalArg[MicrophoneDriver]
type PowerDriverArg = _OptionalArg[PowerDriver] | retro_device_power


class RequiredError(RuntimeError):
    """Raised by :meth:`SessionBuilder.build` when a required argument has not been set."""

    pass


def _raise_required_error(msg: str):
    raise RequiredError(msg)


class _SessionBuilderArgs(TypedDict):
    core: _RequiredFactory[Core]
    audio: _RequiredFactory[AudioDriver]
    input: _RequiredFactory[InputDriver]
    video: _RequiredFactory[VideoDriver]
    content: _OptionalFactory[Content | SubsystemContent]
    content_driver: _OptionalFactory[ContentDriver]
    overscan: _OptionalFactory[bool]  # TODO: Replace with some driver (not sure what yet)
    message: _OptionalFactory[MessageDriver]
    options: _OptionalFactory[OptionDriver]
    path: Callable[[Core], PathDriver | None]
    rumble: _OptionalFactory[RumbleDriver]
    sensor: _OptionalFactory[SensorDriver]
    log: _OptionalFactory[LogDriver]
    perf: _OptionalFactory[PerfDriver]
    location: _OptionalFactory[LocationDriver]
    user: _OptionalFactory[UserDriver]
    vfs: _OptionalFactory[FileSystemDriver]
    led: _OptionalFactory[LedDriver]
    av_mask: _OptionalFactory[AvEnableFlags]
    midi: _OptionalFactory[MidiDriver]
    timing: _OptionalFactory[TimingDriver]
    preferred_hw: _OptionalFactory[HardwareContext]  # TODO: Replace with a method in VideoDriver
    driver_switch_enable: _OptionalFactory[bool]  # TODO: Replace with a method in VideoDriver
    savestate_context: _OptionalFactory[
        SavestateContext
    ]  # TODO: Replace with some driver (not sure what yet)
    jit_capable: _OptionalFactory[bool]  # TODO: Replace with some driver (not sure what yet)
    mic: _OptionalFactory[MicrophoneDriver]
    power: _OptionalFactory[PowerDriver]


type AnySession = Session[
    AudioDriver,
    InputDriver,
    VideoDriver,
    ContentDriver | None,
    MessageDriver | None,
    OptionDriver | None,
    PathDriver | None,
    RumbleDriver | None,
    SensorDriver | None,
    CameraDriver | None,
    LogDriver | None,
    PerfDriver | None,
    LocationDriver | None,
    UserDriver | None,
    FileSystemDriver | None,
    LedDriver | None,
    MidiDriver | None,
    TimingDriver | None,
    MicrophoneDriver | None,
    PowerDriver | None,
]


@deprecated("Use Session's constructor with kwargs instead")
class SessionBuilder:
    """
    A builder class for constructing a :py:class:`.Session`.

    At minimum, a :py:class:`.Session` requires a :py:class:`.Core`,
    an :py:class:`.AudioDriver`,
    an :py:class:`.InputDriver`,
    and a :py:class:`.VideoDriver`;
    each ``with_`` method sets an argument (mostly drivers) for the :py:class:`.Session`.
    """

    def __init__(self):
        """
        Initialize a new :py:class:`SessionBuilder` with no arguments, not even the required ones.

        Calling :py:meth:`build` before setting any of the required arguments
        will raise a :py:class:`RequiredError`.
        """
        self._args = _SessionBuilderArgs(
            core=lambda: _raise_required_error("A Core is required"),
            audio=lambda: _raise_required_error("An AudioDriver is required"),
            input=lambda: _raise_required_error("An InputDriver is required"),
            video=lambda: _raise_required_error("A VideoDriver is required"),
            content=_nothing,
            content_driver=_nothing,
            overscan=_nothing,
            message=_nothing,
            options=_nothing,
            path=lambda _: None,
            rumble=_nothing,
            log=_nothing,
            sensor=_nothing,
            perf=_nothing,
            location=_nothing,
            user=_nothing,
            vfs=_nothing,
            led=_nothing,
            av_mask=_nothing,
            midi=_nothing,
            timing=_nothing,
            preferred_hw=_nothing,
            driver_switch_enable=_nothing,
            savestate_context=_nothing,
            jit_capable=_nothing,
            mic=_nothing,
            power=_nothing,
        )

    @classmethod
    def defaults(cls, core: CoreArg) -> SessionBuilder:
        """Alias to :py:func:`defaults`."""
        return defaults(core)

    def with_core(self, core: CoreArg) -> Self:
        """
        Set the core to use for the session.

        :param core: The core to use for the session. May be one of the following:

            :class:`.Core`
                Will be used as-is.

            :class:`str`, :class:`~os.PathLike`
                Will load a :class:`.Core` from this path in :meth:`build`.

            :class:`~ctypes.CDLL`
                Will load a :class:`.Core` from this library in :meth:`build`.

            :class:`~collections.abc.Callable` () -> :class:`.Core`
                Zero-argument function that returns a :class:`.Core`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``core`` is not one of the permitted types.
        """
        match core:
            case Callable() as func:
                self._args["core"] = func
            case Core():
                self._args["core"] = lambda: core
            case str() | PathLike() | CDLL():
                self._args["core"] = lambda: Core(core)
            case _:
                raise TypeError(
                    f"Expected Core, str, PathLike, a CDLL, or a callable that returns a Core; got {type(core).__name__}"
                )

        return self

    def with_content(self, content: ContentArg) -> Self:
        """
        Set the content to use for this session.

        Will be loaded and managed by this builder's assigned :class:`.ContentDriver`.

        :param content: The content to use for this session. May be one of the following:

            :class:`str`, :class:`~os.PathLike`
                Will load a single content file without enabling a subsystem.

            :class:`zipfile.Path`
                Will load a single content file within a ZIP archive without enabling a subsystem.

            :class:`bytes`, :class:`bytearray`, :class:`memoryview`, :class:`~collections.abc.Buffer`
                Will expose a single unnamed content buffer without enabling a subsystem.

            :class:`.SubsystemContent`
                Will enable a subsystem and load multiple associated content files.

            :class:`.retro_game_info`
                Will be passed to the core as-is without enabling a subsystem.

            :obj:`None`
                Will load the core without using any content or enabling a subsystem;
                if not supported by the core, this will raise an error in :meth:`build`.
                Note that ``retro_load_game`` **will** be called.

            :class:`~collections.abc.Callable` () -> :data:`.Content` | :class:`.SubsystemContent` | :obj:`None`
                Zero-argument function that returns one of the above.
                Will be called in :meth:`build`.

        :return: This :class:`.SessionBuilder` object.
        :raises TypeError: If ``content`` is not one of the permitted types.

        :see: :meth:`.ContentDriver.load` for details on how loaded content is exposed to the core.
        """
        match content:
            case Callable() as func:
                self._args["content"] = func
            case (
                PathLike()
                | ZipPath()
                | str()
                | bytes()
                | bytearray()
                | Buffer()
                | memoryview()
                | SubsystemContent()
                | retro_game_info()
                | None
            ):
                self._args["content"] = lambda: content
            case _DefaultType.DEFAULT:
                raise ValueError(
                    "Content does not have a default value (if you wanted None, provide it explicitly)"
                )
            case _:
                raise TypeError(
                    f"Expected a path, content buffer, None, SubsystemContent, or a callable that returns one of them; got {type(content).__name__}"
                )

        return self

    def with_audio(self, audio: AudioDriverArg) -> Self:
        """
        Set the audio driver for this session.

        :param audio: The audio driver to use for this session. May be one of the following:

            :class:`.AudioDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use an :class:`.ArrayAudioDriver` with its default configuration.

            :class:`~collections.abc.Callable` () -> :class:`.AudioDriver`
                Zero-argument function that returns an :class:`.AudioDriver`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``audio`` is not one of the permitted types.
        :raises ValueError: If ``audio`` is :obj:`None`.
        """
        match audio:
            case Callable() as func:
                self._args["audio"] = func
            case AudioDriver():
                self._args["audio"] = lambda: audio
            case _DefaultType.DEFAULT:
                self._args["audio"] = ArrayAudioDriver
            case None:
                raise ValueError("An audio driver is required")
            case _:
                raise TypeError(
                    f"Expected AudioDriver, a callable that returns one, or DEFAULT; got {type(audio).__name__}"
                )

        return self

    def with_input(self, input: InputDriverArg) -> Self:
        """
        Set the input driver for this session.

        :param input: The input driver to use for this session. May be one of the following:

            :class:`.InputDriver`
                Will be used by the built :class:`.Session` as-is.

            :class:`~collections.abc.Generator`, :class:`~collections.abc.Iterable`, :class:`~collections.abc.Iterator`
                Will be wrapped in an :class:`.IterableInputDriver`
                that yields :class:`.InputState` values.

            :data:`.DEFAULT`
                Will use an :class:`.IterableInputDriver` with its default configuration.

            :class:`~collections.abc.Callable` () -> :class:`.InputDriver` | iterable
                Zero-argument function that returns either an :class:`.InputDriver`
                or an iterable/iterator/generator of :class:`.InputState` values.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``input`` (or the value returned by a callable ``input``)
            is not one of the permitted types.
        :raises ValueError: If ``input`` is :obj:`None`.
        """
        match input:
            case Generator() as generator:
                self._args["input"] = lambda: IterableInputDriver(generator)
            case InputDriver():
                self._args["input"] = lambda: input
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

                self._args["input"] = _generate
            case _DefaultType.DEFAULT:
                # TODO: Set the rumble interface
                self._args["input"] = IterableInputDriver
            case None:
                raise ValueError("An input driver is required")
            case _:
                raise TypeError(
                    f"Expected InputDriver or a callable that returns one, a callable or iterator that yields InputState, or DEFAULT; got {type(input).__name__}"
                )

        return self

    def with_rumble(self, rumble: RumbleDriverArg) -> Self:
        """
        Configure the rumble driver for this session's input driver.

        :param rumble: The rumble driver to use for this session. May be one of the following:

            :class:`.RumbleDriver`
                Will be used by the built :class:`.Session` as-is.

            :obj:`None`
                No rumble driver will be used, and any rumble interfaces
                that the core exposes will not function.

            :data:`.DEFAULT`
                Will use a :class:`.DictRumbleDriver` with no initial state.

            :class:`~collections.abc.Callable` () -> :class:`.RumbleDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.RumbleDriver` or :obj:`None`.
                Will be called in :meth:`build`.
        :return: This :class:`.SessionBuilder` object.
        :raises TypeError: If ``rumble`` is not one of the aforementioned types.
        """
        match rumble:
            case Callable() as func:
                self._args["rumble"] = func
            case RumbleDriver():
                self._args["rumble"] = lambda: rumble
            case _DefaultType.DEFAULT:
                self._args["rumble"] = DictRumbleDriver
            case None:
                self._args["rumble"] = _nothing
            case _:
                raise TypeError(
                    f"Expected RumbleDriver, a callable that returns one, DEFAULT, or None; got {type(rumble).__name__}"
                )

        return self

    def with_video(self, video: VideoDriverArg) -> Self:
        """
        Set the video driver for this session.

        :param video: The video driver to use for this session. May be one of the following:

            :class:`.VideoDriver`
                Used by the built :class:`.Session` as-is.

            :const:`DEFAULT`
                Uses a :class:`.MultiVideoDriver` with its default configuration.
                See its documentation for more details.

            :class:`~collections.abc.Mapping` [:class:`.HardwareContext`, :class:`~collections.abc.Callable` () -> :class:`.VideoDriver`]
                Uses a :class:`.MultiVideoDriver` with the provided driver map.

            :class:`~collections.abc.Callable` () -> :class:`.VideoDriver`
                Zero-argument function that returns a :class:`.VideoDriver`.
                Called in :meth:`build`.


        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``video`` is not one of the aforementioned types.
        :raises ValueError: If ``video`` does not contain a mapping for :attr:`.HardwareContext.NONE`.
        """
        match video:
            case Callable() as func:
                self._args["video"] = func
            case VideoDriver():
                self._args["video"] = lambda: video
            case _DefaultType.DEFAULT:
                self._args["video"] = MultiVideoDriver
            case Mapping():
                if HardwareContext.NONE not in video:
                    raise ValueError("A driver for HardwareContext.NONE is required")

                if not all(isinstance(k, HardwareContext) for k in video.keys()):
                    raise TypeError(
                        "Each key in the provided driver map must be a HardwareContext"
                    )

                if not all(callable(v) for v in video.values()):
                    raise TypeError(
                        "Each value in the provided driver map must be a callable that returns a VideoDriver"
                    )

                self._args["video"] = lambda: MultiVideoDriver(video)

            case None:
                raise ValueError("A video driver is required")
            case _:
                raise TypeError(
                    f"Expected a VideoDriver, a callable that returns one, a map of HardwareContexts to Callables, or DEFAULT; got {type(video).__name__}"
                )

        return self

    def with_content_driver(self, content: ContentDriverArg) -> Self:
        """
        Set the content driver for this session.

        :param content: The content driver to use for this session. May be one of the following:

            :class:`.ContentDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.StandardContentDriver` with its default configuration.

            :obj:`None`
                No content driver will be used; content set via :meth:`with_content`
                will not be loaded.

            :class:`~collections.abc.Callable` () -> :class:`.ContentDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.ContentDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``content`` is not one of the permitted types.
        """
        match content:
            case Callable() as func:
                self._args["content_driver"] = func
            case ContentDriver():
                self._args["content_driver"] = lambda: content
            case _DefaultType.DEFAULT:
                self._args["content_driver"] = StandardContentDriver
            case None:
                self._args["content_driver"] = _nothing
            case _:
                raise TypeError(
                    f"Expected ContentDriver, a callable that returns one, DEFAULT, or None; got {type(content).__name__}"
                )

        return self

    def with_overscan(self, overscan: BoolArg) -> Self:
        """
        Set whether the loaded core should render overscan regions.

        :param overscan: The overscan flag to expose to the core. May be one of the following:

            :class:`bool`
                Will be reported to the core as-is.

            :data:`.DEFAULT`
                Reports :obj:`False` to the core.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            :class:`~collections.abc.Callable` () -> :class:`bool` | :obj:`None`
                Zero-argument function that returns a :class:`bool` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``overscan`` is not one of the permitted types.
        """
        match overscan:
            case bool():
                self._args["overscan"] = lambda: overscan
            case Callable() as func:
                self._args["overscan"] = func
            case _DefaultType.DEFAULT:
                self._args["overscan"] = lambda: False
            case None:
                self._args["overscan"] = _nothing
            case _:
                raise TypeError(
                    f"Expected bool, a callable that returns one, DEFAULT, or None; got {type(overscan).__name__}"
                )

        return self

    def with_message(self, message: MessageDriverArg) -> Self:
        """
        Set the message driver for this session.

        :param message: The message driver to use for this session. May be one of the following:

            :class:`.MessageDriver`
                Will be used by the built :class:`.Session` as-is.

            :class:`~logging.Logger`
                Will be wrapped in a :class:`.LoggerMessageDriver`
                that forwards messages to the given logger.

            :data:`.DEFAULT`
                Will use a :class:`.LoggerMessageDriver` with its default configuration.

            :obj:`None`
                The environment calls that :class:`.MessageDriver` normally implements
                will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.MessageDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.MessageDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``message`` is not one of the permitted types.
        """
        match message:
            case Callable() as func:
                self._args["message"] = func
            case MessageDriver():
                self._args["message"] = lambda: message
            case Logger() as logger:
                self._args["message"] = lambda: LoggerMessageDriver(logger=logger)
            case _DefaultType.DEFAULT:
                self._args["message"] = LoggerMessageDriver
            case None:
                self._args["message"] = _nothing
            case _:
                raise TypeError(
                    f"Expected MessageInterface, a callable that returns one, DEFAULT, or None; got {type(message).__name__}"
                )

        return self

    def with_options(self, options: OptionDriverArg) -> Self:
        """
        Configure the options driver for this session.

        :param options: May be one of the following:

            :class:`.OptionDriver`
                Will be used by the built :class:`.Session` as-is.

            :class:`~collections.abc.Mapping` [:obj:`~typing.AnyStr`, :obj:`~typing.AnyStr`]
                Will be used to initialize a :class:`.DictOptionDriver` with the provided options
                and with API version 2.
                All keys and values must be either :class:`str` or :class:`bytes`;
                mixing the two is not allowed.

            ``0``, ``1``, or ``2``
                Will be used to initialize a :class:`.DictOptionDriver` with no initial options
                using the provided API version.

            :data:`.DEFAULT`
                Will use a :class:`.DictOptionDriver` with API version 2
                and no initial options.

            :obj:`None`
                All environment calls that :class:`.OptionDriver` normally implements
                will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.OptionDriver` | :obj:`None`
                Zero-argument function that returns an :class:`.OptionDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`.SessionBuilder` object.
        :raises TypeError: If ``options`` is not one of the aforementioned types.
        :raises ValueError: If ``options`` is a :class:`~collections.abc.Mapping` whose keys and values
            are not all :class:`str` or :class:`bytes`.
        """
        match options:
            case Callable() as func:
                self._args["options"] = func
            case OptionDriver() as driver:
                self._args["options"] = lambda: driver
            case Mapping() as optionvars:
                all_str = all(
                    isinstance(k, str) and isinstance(v, str) for k, v in optionvars.items()
                )
                all_bytes = all(
                    isinstance(k, bytes) and isinstance(v, bytes) for k, v in optionvars.items()
                )
                if not (all_str or all_bytes):
                    raise ValueError("All keys and values must be either str or bytes")
                self._args["options"] = lambda: DictOptionDriver(2, True, optionvars)
            case 0 | 1 | 2 as version:
                self._args["options"] = lambda: DictOptionDriver(version)
            case _DefaultType.DEFAULT:
                self._args["options"] = DictOptionDriver
            case None:
                self._args["options"] = _nothing
            case _:
                raise TypeError(
                    f"Expected an OptionDriver, a Mapping, DEFAULT, an API version, or a Callable that returns an OptionDriver, or None; got {type(options).__name__}"
                )

        return self

    def with_paths(self, path: PathDriverArg) -> Self:
        """
        Configure the path driver for this session.

        :param path: May be one of the following:

            :class:`.PathDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.TempDirPathDriver`
                configured with an unspecified temporary directory
                and the provided :class:`.Core`'s path.

            :class:`~collections.abc.Callable` (:class:`.Core`) -> :class:`.PathDriver` | :obj:`None`
                One-argument function that accepts a :class:`.Core`
                and returns a :class:`.PathDriver` or :obj:`None`.
                Will be called in :meth:`build` with the configured :class:`.Core` as the argument.

            :obj:`None`
                All environment calls that :class:`.PathDriver` normally implements
                will be unavailable to the loaded :class:`.Core`.

        :return: This :class:`.SessionBuilder` object.
        :raises TypeError: If ``path`` is not one of the aforementioned types.
        """
        match path:
            case Callable() as func:
                self._args["path"] = func
            case PathDriver():
                self._args["path"] = lambda _: path
            case _DefaultType.DEFAULT:
                self._args["path"] = lambda core: TempDirPathDriver(core)
            case None:
                self._args["path"] = lambda _: None
            case _:
                raise TypeError(
                    f"Expected PathDriver, a callable that returns one, DEFAULT, or None; got {type(path).__name__}"
                )

        return self

    def with_sensor(self, sensor: SensorDriverArg) -> Self:
        """
        Configure the sensor driver for this session.

        :param sensor: May be one of the following:

            :class:`.SensorDriver`
                Will be used by the built :class:`.Session` as-is.

            :obj:`None`
                All environment calls and interfaces
                that :class:`.SensorDriver` normally implements
                will be unavailable to the loaded :class:`.Core`.

            :data:`.DEFAULT`
                Will use an :class:`.IterableSensorDriver`
                whose sensor state can be configured,
                but does not produce any nonzero readings.

            :class:`~collections.abc.Callable` () -> :class:`.SensorDriver`
                Zero-argument function that returns the :class:`.SensorDriver`
                that the built :class:`.Session` will use.

            :class:`~collections.abc.Callable` () -> :class:`~collections.abc.Iterable` | :class:`~collections.abc.Iterator`
                Zero-argument function that returns an iterator or generator
                that yields elements as described in :class:`.IterableSensorDriver`.
                An :class:`.IterableSensorDriver` will be created from this iterator.

            :class:`~collections.abc.Iterable` | :class:`~collections.abc.Iterator`
                An iterator, iterable, or generator function that yields
                elements as described in :class:`.IterableSensorDriver`.
                An :class:`.IterableSensorDriver` will be created from this iterator.

        :return: This :class:`.SessionBuilder` object.
        """
        match sensor:
            case (Generator() as source) | (Iterable() as source) | (Iterator() as source):
                self._args["sensor"] = lambda: IterableSensorDriver(source)
            case SensorDriver():
                self._args["sensor"] = lambda: sensor
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

                self._args["sensor"] = _generate
            case _DefaultType.DEFAULT:
                self._args["sensor"] = IterableSensorDriver
            case None:
                self._args["sensor"] = _nothing
            case _:
                raise TypeError(
                    f"Expected SensorDriver or a callable that returns one, a callable or iterator that yields SensorState; got {type(input).__name__}"
                )

        return self

    def with_log(self, log: LogDriverArg) -> Self:
        """
        Set the log driver for this session.

        :param log: The log driver to use for this session. May be one of the following:

            :class:`.LogDriver`
                Will be used by the built :class:`.Session` as-is.

            :class:`~logging.Logger`
                Will be wrapped in an :class:`.UnformattedLogDriver`
                that forwards core log messages to the given logger.

            :data:`.DEFAULT`
                Will use an :class:`.UnformattedLogDriver` with its default configuration.

            :obj:`None`
                The log interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.LogDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.LogDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``log`` is not one of the permitted types.
        """
        match log:
            case Callable() as func:
                self._args["log"] = func
            case LogDriver():
                self._args["log"] = lambda: log
            case Logger() as logger:
                self._args["log"] = lambda: UnformattedLogDriver(logger=logger)
            case _DefaultType.DEFAULT:
                self._args["log"] = UnformattedLogDriver
            case None:
                self._args["log"] = _nothing
            case _:
                raise TypeError(
                    f"Expected LogDriver, a callable that returns one, DEFAULT, or None; got {type(log).__name__}"
                )

        return self

    def with_perf(self, perf: PerfDriverArg) -> Self:
        """
        Set the performance driver for this session.

        :param perf: The performance driver to use for this session. May be one of the following:

            :class:`.PerfDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.DefaultPerfDriver` with its default configuration.

            :obj:`None`
                The performance interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.PerfDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.PerfDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``perf`` is not one of the permitted types.
        """
        match perf:
            case Callable() as func:
                self._args["perf"] = func
            case PerfDriver():
                self._args["perf"] = lambda: perf
            case _DefaultType.DEFAULT:
                self._args["perf"] = DefaultPerfDriver
            case None:
                self._args["perf"] = _nothing
            case _:
                raise TypeError(
                    f"Expected PerfDriver, a callable that returns one, DEFAULT, or None; got {type(perf).__name__}"
                )

        return self

    def with_location(self, location: LocationDriverArg) -> Self:
        """
        Set the location driver for this session.

        :param location: The location driver to use for this session. May be one of the following:

            :class:`.LocationDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                No location driver will be used; equivalent to passing :obj:`None`.

            :obj:`None`
                The location interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.LocationDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.LocationDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``location`` is not one of the permitted types.
        """
        match location:
            case Callable() as func:
                self._args["location"] = func
            case LocationDriver():
                self._args["location"] = lambda: location
            case _DefaultType.DEFAULT:
                self._args["location"] = _nothing
            case None:
                self._args["location"] = _nothing
            case _:
                raise TypeError(
                    f"Expected LocationDriver, a callable that returns one, DEFAULT, or None; got {type(location).__name__}"
                )

        return self

    def with_user(self, user: UserDriverArg) -> Self:
        """
        Set the user driver for this session.

        :param user: The user driver to use for this session. May be one of the following:

            :class:`.UserDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.DefaultUserDriver` with its default configuration.

            :obj:`None`
                The environment calls that :class:`.UserDriver` normally implements
                will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.UserDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.UserDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``user`` is not one of the permitted types.
        """
        match user:
            case Callable() as func:
                self._args["user"] = func
            case UserDriver():
                self._args["user"] = lambda: user
            case _DefaultType.DEFAULT:
                self._args["user"] = DefaultUserDriver
            case None:
                self._args["user"] = _nothing
            case _:
                raise TypeError(
                    f"Expected UserDriver, a callable that returns one, DEFAULT, or None; got {type(user).__name__}"
                )

        return self

    def with_vfs(self, vfs: FileSystemArg) -> Self:
        """
        Set the virtual filesystem driver for this session.

        :param vfs: The filesystem driver to use for this session. May be one of the following:

            :class:`.FileSystemDriver`
                Will be used by the built :class:`.Session` as-is.

            ``1``, ``2``, or ``3``
                Will use a :class:`.DefaultFileSystemDriver` with the given API version.

            :data:`.DEFAULT`
                Will use a :class:`.DefaultFileSystemDriver` with its default configuration.

            :obj:`None`
                The VFS interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.FileSystemDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.FileSystemDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``vfs`` is not one of the permitted types.
        """
        match vfs:
            case Callable() as func:
                self._args["vfs"] = func
            case FileSystemDriver() as interface:
                self._args["vfs"] = lambda: interface
            case 1 | 2 | 3 as version:
                self._args["vfs"] = lambda: DefaultFileSystemDriver(version)
            case _DefaultType.DEFAULT:
                self._args["vfs"] = DefaultFileSystemDriver
            case None:
                self._args["vfs"] = _nothing
            case _:
                raise TypeError(
                    f"Expected FileSystemInterface, a callable that returns one, DEFAULT, or None; got {type(vfs).__name__}"
                )

        return self

    def with_led(self, led: LedDriverArg) -> Self:
        """
        Set the LED driver for this session.

        :param led: The LED driver to use for this session. May be one of the following:

            :class:`.LedDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.DictLedDriver` with its default configuration.

            :obj:`None`
                The LED interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.LedDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.LedDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``led`` is not one of the permitted types.
        """
        match led:
            case Callable() as func:
                self._args["led"] = func
            case LedDriver():
                self._args["led"] = lambda: led
            case _DefaultType.DEFAULT:
                self._args["led"] = DictLedDriver
            case None:
                self._args["led"] = _nothing
            case _:
                raise TypeError(
                    f"Expected LedDriver, a callable that returns one, or None; got {type(led).__name__}"
                )

        return self

    def with_av_mask(self, av_mask: AvEnableFlagsArg) -> Self:
        """
        Set the audio/video enable mask for this session.

        :param av_mask: The :class:`.AvEnableFlags` to expose to the core. May be one of the following:

            :class:`.AvEnableFlags`
                Will be reported to the core as-is.

            :data:`.DEFAULT`
                Reports :attr:`.AvEnableFlags.ALL` to the core.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            :class:`~collections.abc.Callable` () -> :class:`.AvEnableFlags` | :obj:`None`
                Zero-argument function that returns an :class:`.AvEnableFlags` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``av_mask`` is not one of the permitted types.
        """
        match av_mask:
            case Callable() as func:
                self._args["av_mask"] = func
            case AvEnableFlags():
                self._args["av_mask"] = lambda: av_mask
            case _DefaultType.DEFAULT:
                self._args["av_mask"] = lambda: AvEnableFlags.ALL
            case None:
                self._args["av_mask"] = _nothing
            case _:
                raise TypeError(
                    f"Expected AvEnableFlags, a callable that returns one, or None; got {type(av_mask).__name__}"
                )

        return self

    def with_midi(self, midi: MidiDriverArg) -> Self:
        """
        Set the MIDI driver for this session.

        :param midi: The MIDI driver to use for this session. May be one of the following:

            :class:`.MidiDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.GeneratorMidiDriver` with its default configuration.

            :obj:`None`
                The MIDI interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.MidiDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.MidiDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``midi`` is not one of the permitted types.
        """
        match midi:
            case func if callable(func):
                self._args["midi"] = func
            case MidiDriver():
                self._args["midi"] = lambda: midi
            case _DefaultType.DEFAULT:
                self._args["midi"] = GeneratorMidiDriver
            case None:
                self._args["midi"] = _nothing
            case _:
                raise TypeError(
                    f"Expected MidiDriver, a callable that returns one, or None; got {type(midi).__name__}"
                )

        return self

    def with_timing(self, timing: TimingDriverArg) -> Self:
        """
        Set the timing driver for this session.

        :param timing: The timing driver to use for this session. May be one of the following:

            :class:`.TimingDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.DefaultTimingDriver` running unblocked at 60 FPS.

            :obj:`None`
                The corresponding environment calls will be unavailable to the core.

            :class:`~collections.abc.Callable` () -> :class:`.TimingDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.TimingDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``timing`` is not one of the permitted types.
        """
        match timing:
            case TimingDriver():
                self._args["timing"] = lambda: timing
            case Callable() as func:
                self._args["timing"] = func
            case _DefaultType.DEFAULT:
                self._args["timing"] = lambda: DefaultTimingDriver(
                    retro_throttle_state(ThrottleMode.UNBLOCKED, 0.0), 60.0
                )
            case None:
                self._args["timing"] = _nothing
            case _:
                raise TypeError(
                    f"Expected TimingDriver, a callable that returns one, DEFAULT, or None; got {type(timing).__name__}"
                )

        return self

    def with_preferred_hw(self, hw: HardwareContextArg) -> Self:
        """
        Set the preferred hardware context to report to the core.

        :param hw: The preferred hardware context to expose to the core. May be one of the following:

            :class:`.HardwareContext`
                Will be reported to the core as-is.

            :data:`.DEFAULT`
                The corresponding environment call will be unavailable to the core.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            :class:`~collections.abc.Callable` () -> :class:`.HardwareContext` | :obj:`None`
                Zero-argument function that returns a :class:`.HardwareContext` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``hw`` is not one of the permitted types.
        """
        match hw:
            case Callable() as func:
                self._args["preferred_hw"] = func
            case HardwareContext():
                self._args["preferred_hw"] = lambda: hw
            case _DefaultType.DEFAULT:
                self._args["preferred_hw"] = _nothing
            case None:
                self._args["preferred_hw"] = _nothing
            case _:
                raise TypeError(
                    f"Expected HardwareContext, a callable that returns one, DEFAULT, or None; got {type(hw).__name__}"
                )

        return self

    def with_driver_switch_enable(self, enable: BoolArg) -> Self:
        """
        Set whether the core may switch hardware rendering drivers at runtime.

        :param enable: The driver-switch flag to expose to the core. May be one of the following:

            :class:`bool`
                Will be reported to the core as-is.

            :data:`.DEFAULT`
                Reports :obj:`False` to the core.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            :class:`~collections.abc.Callable` () -> :class:`bool` | :obj:`None`
                Zero-argument function that returns a :class:`bool` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``enable`` is not one of the permitted types.
        """
        match enable:
            case bool():
                self._args["driver_switch_enable"] = lambda: enable
            case Callable() as func:
                self._args["driver_switch_enable"] = func
            case _DefaultType.DEFAULT:
                self._args["driver_switch_enable"] = lambda: False
            case None:
                self._args["driver_switch_enable"] = _nothing
            case _:
                raise TypeError(
                    f"Expected bool, a callable that returns one, DEFAULT, or None; got {type(enable).__name__}"
                )

        return self

    def with_savestate_context(self, context: SavestateContextArg) -> Self:
        """
        Set the savestate context to report to the core.

        :param context: The :class:`.SavestateContext` to expose to the core. May be one of the following:

            :class:`.SavestateContext`
                Will be reported to the core as-is.

            :data:`.DEFAULT`
                Reports :attr:`.SavestateContext.NORMAL` to the core.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            :class:`~collections.abc.Callable` () -> :class:`.SavestateContext` | :obj:`None`
                Zero-argument function that returns a :class:`.SavestateContext` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``context`` is not one of the permitted types.
        """
        match context:
            case SavestateContext():
                self._args["savestate_context"] = lambda: context
            case func if callable(func):
                self._args["savestate_context"] = func
            case _DefaultType.DEFAULT:
                self._args["savestate_context"] = lambda: SavestateContext.NORMAL
            case None:
                self._args["savestate_context"] = _nothing
            case _:
                raise TypeError(
                    f"Expected SavestateContext, a callable that returns one, DEFAULT, or None; got {type(context).__name__}"
                )

        return self

    def with_jit_capable(self, capable: BoolArg) -> Self:
        """
        Set whether the host environment is JIT-capable.

        :param capable: The JIT-capable flag to expose to the core. May be one of the following:

            :class:`bool`
                Will be reported to the core as-is.

            :data:`.DEFAULT`
                Reports :obj:`True` to the core.

            :obj:`None`
                The corresponding environment call will be unavailable to the core.

            :class:`~collections.abc.Callable` () -> :class:`bool` | :obj:`None`
                Zero-argument function that returns a :class:`bool` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``capable`` is not one of the permitted types.
        """
        match capable:
            case bool():
                self._args["jit_capable"] = lambda: capable
            case func if callable(func):
                self._args["jit_capable"] = func
            case _DefaultType.DEFAULT:
                self._args["jit_capable"] = lambda: True
            case None:
                self._args["jit_capable"] = _nothing
            case _:
                raise TypeError(
                    f"Expected bool, a callable that returns one, DEFAULT, or None; got {type(capable).__name__}"
                )

        return self

    def with_mic(self, mic: MicDriverArg) -> Self:
        """
        Set the microphone driver for this session.

        :param mic: The microphone driver to use for this session. May be one of the following:

            :class:`.MicrophoneDriver`
                Will be used by the built :class:`.Session` as-is.

            :data:`.DEFAULT`
                Will use a :class:`.GeneratorMicrophoneDriver` with its default configuration.

            :obj:`None`
                The microphone interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.MicrophoneDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.MicrophoneDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``mic`` is not one of the permitted types.
        """
        match mic:
            case Callable() as func:
                self._args["mic"] = func
            case MicrophoneDriver():
                self._args["mic"] = lambda: mic
            case _DefaultType.DEFAULT:
                self._args["mic"] = GeneratorMicrophoneDriver
            case None:
                self._args["mic"] = _nothing
            case _:
                raise TypeError(
                    f"Expected MicrophoneDriver, a callable that returns one, DEFAULT, or None; got {type(mic).__name__}"
                )

        return self

    def with_power(self, power: PowerDriverArg) -> Self:
        """
        Set the power driver for this session.

        :param power: The power driver to use for this session. May be one of the following:

            :class:`.PowerDriver`
                Will be used by the built :class:`.Session` as-is.

            :class:`.retro_device_power`
                Will be wrapped in a :class:`.ConstantPowerDriver` that always reports this state.

            :data:`.DEFAULT`
                Will use a :class:`.ConstantPowerDriver` reporting a fully charged, plugged-in device.

            :obj:`None`
                The power interface will be unavailable to the loaded :class:`.Core`.

            :class:`~collections.abc.Callable` () -> :class:`.PowerDriver` | :obj:`None`
                Zero-argument function that returns a :class:`.PowerDriver` or :obj:`None`.
                Will be called in :meth:`build`.

        :return: This :class:`SessionBuilder` object.
        :raises TypeError: If ``power`` is not one of the permitted types.
        """
        match power:
            case retro_device_power() as pow:
                self._args["power"] = lambda: ConstantPowerDriver(pow)
            case Callable() as func:
                self._args["power"] = func
            case PowerDriver():
                self._args["power"] = lambda: power
            case _DefaultType.DEFAULT:
                self._args["power"] = lambda: ConstantPowerDriver(
                    retro_device_power(PowerState.PLUGGED_IN, 0, 100)
                )
            case None:
                self._args["power"] = _nothing
            case _:
                raise TypeError(
                    f"Expected a PowerDriver, retro_device_power, a callable that returns one, DEFAULT, or None; got {type(power).__name__}"
                )

        return self

    def build(self) -> AnySession:
        """
        Construct a :py:class:`.Session` with the provided arguments.

        :raises RequiredError: If a :py:class:`.Core`, :py:class:`.AudioDriver`, :py:class:`.InputDriver`, or :py:class:`.VideoDriver` is not set.
        :raises Exception: Any exception raised by a registered driver factory or initializer.

        :return: A :py:class:`.Session` object.
        """
        core = self._args["core"]()

        return Session(
            core=core,
            game=self._args["content"](),
            audio=self._args["audio"](),
            input=self._args["input"](),
            video=self._args["video"](),
            content=self._args["content_driver"](),
            overscan=self._args["overscan"](),
            message=self._args["message"](),
            options=self._args["options"](),
            path=self._args["path"](core),
            rumble=self._args["rumble"](),
            sensor=self._args["sensor"](),
            log=self._args["log"](),
            perf=self._args["perf"](),
            location=self._args["location"](),
            user=self._args["user"](),
            vfs=self._args["vfs"](),
            led=self._args["led"](),
            av_enable=self._args["av_mask"](),
            midi=self._args["midi"](),
            timing=self._args["timing"](),
            preferred_hw=self._args["preferred_hw"](),
            driver_switch_enable=self._args["driver_switch_enable"](),
            savestate_context=self._args["savestate_context"](),
            jit_capable=self._args["jit_capable"](),
            mic=self._args["mic"](),
            device_power=self._args["power"](),
        )


def defaults(core: CoreArg) -> SessionBuilder:
    """
    Construct a :py:class:`SessionBuilder` with the recommended drivers and their default values.

    Does not build the session, so these defaults may still be overridden.

    :param core: The core to use for the session.

    Examples::

        builder = SessionBuilder.defaults(core)
        with builder.with_log(None).build() as session:
            pass

    """
    return (
        SessionBuilder()
        .with_core(core)
        .with_audio(DEFAULT)
        .with_input(DEFAULT)
        .with_video(DEFAULT)
        .with_content_driver(DEFAULT)
        .with_overscan(DEFAULT)
        .with_message(DEFAULT)
        .with_options(DEFAULT)
        .with_sensor(DEFAULT)
        .with_paths(DEFAULT)
        .with_rumble(DEFAULT)
        .with_log(DEFAULT)
        .with_perf(DEFAULT)
        .with_location(DEFAULT)
        .with_user(DEFAULT)
        .with_vfs(DEFAULT)
        .with_led(DEFAULT)
        .with_av_mask(DEFAULT)
        .with_midi(DEFAULT)
        .with_timing(DEFAULT)
        .with_preferred_hw(DEFAULT)
        .with_driver_switch_enable(DEFAULT)
        .with_savestate_context(DEFAULT)
        .with_jit_capable(DEFAULT)
        .with_mic(DEFAULT)
        .with_power(DEFAULT)
    )


__all__ = [
    "SessionBuilder",
    "DEFAULT",
    "defaults",
    "RequiredError",
    "AnySession",
]
