from collections.abc import Callable, Generator, Iterable, Iterator, Mapping
from ctypes import CDLL
from enum import Enum, auto
from logging import Logger
from os import PathLike
from typing import AnyStr, Literal, Self, TypeAlias, TypedDict, TypeVar
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
    retro_hw_render_callback,
    retro_throttle_state,
)
from libretro.core import Core
from libretro.drivers import (
    ArrayAudioDriver,
    ArrayVideoDriver,
    AudioDriver,
    CompositeEnvironmentDriver,
    ConstantPowerDriver,
    ContentDriver,
    DefaultPathDriver,
    DefaultPerfDriver,
    DefaultTimingDriver,
    DefaultUserDriver,
    DictLedDriver,
    DictOptionDriver,
    FileSystemInterface,
    GeneratorInputDriver,
    GeneratorLocationDriver,
    GeneratorMicrophoneDriver,
    GeneratorMidiDriver,
    InputDriver,
    InputStateGenerator,
    InputStateIterable,
    InputStateIterator,
    LedDriver,
    LocationDriver,
    LocationInputGenerator,
    LogDriver,
    LoggerMessageInterface,
    MessageInterface,
    MicrophoneDriver,
    MidiDriver,
    MultiVideoDriver,
    OptionDriver,
    PathDriver,
    PerfDriver,
    PowerDriver,
    StandardContentDriver,
    StandardFileSystemInterface,
    TimingDriver,
    UnformattedLogDriver,
    UserDriver,
    VideoDriver,
    VideoDriverInitArgs,
)
from libretro.session import Session

try:
    from libretro.drivers.video import ModernGlVideoDriver
except ImportError:
    ModernGlVideoDriver = None


class _DefaultType(Enum):
    DEFAULT = auto()


DEFAULT = _DefaultType.DEFAULT
Default = Literal[_DefaultType.DEFAULT]
"""
A placeholder that indicates the default value for a SessionBuilder argument.
When passed to a SessionBuilder method, the method will use the default value for that argument.
"""

T = TypeVar("T")

_RequiredFactory: TypeAlias = Callable[[], T]
_OptionalFactory: TypeAlias = Callable[[], T | None]

_RequiredArg: TypeAlias = T | _RequiredFactory[T]
_OptionalArg: TypeAlias = T | _OptionalFactory[T] | Default | None

_nothing = lambda: None
CoreArg: TypeAlias = Core | str | PathLike | CDLL | _RequiredFactory[Core]
AudioDriverArg: TypeAlias = _RequiredArg[AudioDriver] | Default
InputDriverArg: TypeAlias = (
    _RequiredArg[InputDriver]
    | InputStateGenerator
    | InputStateIterable
    | InputStateIterator
    | Default
)
VideoDriverArg: TypeAlias = _RequiredArg[VideoDriver] | Default
ContentArg: TypeAlias = (
    Content | SubsystemContent | _OptionalFactory[Content | SubsystemContent] | None
)
ContentDriverArg: TypeAlias = _OptionalArg[ContentDriver]
BoolArg: TypeAlias = _OptionalArg[bool]
MessageDriverArg: TypeAlias = _OptionalArg[MessageInterface] | Logger
OptionDriverArg: TypeAlias = (
    _OptionalArg[OptionDriver] | Mapping[AnyStr, AnyStr] | Literal[0, 1, 2]
)
PathDriverArg: TypeAlias = _OptionalArg[PathDriver] | str | PathLike
LogDriverArg: TypeAlias = _OptionalArg[LogDriver] | Logger
PerfDriverArg: TypeAlias = _OptionalArg[PerfDriver]
LocationDriverArg: TypeAlias = _OptionalArg[LocationDriver] | LocationInputGenerator
UserDriverArg: TypeAlias = _OptionalArg[UserDriver]
FileSystemArg: TypeAlias = _OptionalArg[FileSystemInterface] | Literal[1, 2, 3]
LedDriverArg: TypeAlias = _OptionalArg[LedDriver]
AvEnableFlagsArg: TypeAlias = _OptionalArg[AvEnableFlags]
MidiDriverArg: TypeAlias = _OptionalArg[MidiDriver]
TimingDriverArg: TypeAlias = _OptionalArg[TimingDriver]
FloatArg: TypeAlias = _OptionalArg[float | int]
HardwareContextArg: TypeAlias = _OptionalArg[HardwareContext]
ThrottleStateArg: TypeAlias = _OptionalArg[retro_throttle_state]
SavestateContextArg: TypeAlias = _OptionalArg[SavestateContext]
MicDriverArg: TypeAlias = _OptionalArg[MicrophoneDriver]
PowerDriverArg: TypeAlias = _OptionalArg[PowerDriver] | retro_device_power


class RequiredError(RuntimeError):
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
    message: _OptionalFactory[MessageInterface]
    options: _OptionalFactory[OptionDriver]
    path: _OptionalFactory[PathDriver]
    log: _OptionalFactory[LogDriver]
    perf: _OptionalFactory[PerfDriver]
    location: _OptionalFactory[LocationDriver]
    user: _OptionalFactory[UserDriver]
    vfs: _OptionalFactory[FileSystemInterface]
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


class SessionBuilder:
    """
    A builder class for constructing Session objects.

    A Session requires a Core, an AudioDriver, an InputDriver, and a VideoDriver;
    each ``with_`` method sets an argument (mostly drivers) for the Session.
    """

    def __init__(self):
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
            path=_nothing,
            log=_nothing,
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

    def with_core(self, core: CoreArg) -> Self:
        """
        Sets the core to use for the session.

        ``core`` may be one of the following:

        - A :class:`Core` that will be used as-is.
        - A :class:`str` or :class:`PathLike` that represents a path to the core.
          It will be loaded as a :class:`Core` when the session is built.
        - A :class:`CDLL` object that represents a loaded binary.
          It will be loaded into a :class:`Core` when the session is built.
        - A :class:`Callable` that returns one of the above types.
          It will be evaluated when the session is built.

        :param core: The core to use for the session.
        :return: This builder object.
        :raises ValueError: If ``core`` is :py:const:`Default`.
        :raises TypeError: If ``core`` is not one of the permitted types.
        """
        match core:
            case Callable() as func:
                self._args["core"] = func
            case Core():
                self._args["core"] = lambda: core
            case str() | PathLike() | CDLL():
                self._args["core"] = lambda: Core(core)
            case _DefaultType.DEFAULT:
                raise ValueError("Core does not have a default value")
            case _:
                raise TypeError(
                    f"Expected Core, str, PathLike, a CDLL, or a callable that returns one of them; got {type(core).__name__}"
                )

        return self

    def with_content(self, content: ContentArg) -> Self:
        """
        Sets the content to use for this session.

        ``content`` may be one of the following:

        TODO
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
        match input:
            case Generator() as generator:
                self._args["input"] = lambda: GeneratorInputDriver(generator)
            case InputDriver():
                self._args["input"] = lambda: input
            case Callable() as func:
                # Either a generator or a driver type;
                def _generate():
                    match func():
                        case Generator() | Iterable() | Iterator() as gen:
                            return GeneratorInputDriver(gen)
                        case InputDriver() as driver:
                            return driver
                        case err:
                            raise TypeError(
                                f"Expected a generator, an iterable, an iterator, or an InputDriver from the callable, got {type(err).__name__}"
                            )

                self._args["input"] = _generate
            case _DefaultType.DEFAULT:
                self._args["input"] = (
                    GeneratorInputDriver  # TODO: Set the rumble and sensor interfaces
                )
            case None:
                raise ValueError("An input driver is required")
            case _:
                raise TypeError(
                    f"Expected InputDriver or a callable that returns one, a callable or iterator that yields InputState, or DEFAULT; got {type(input).__name__}"
                )

        return self

    def with_video(self, video: VideoDriverArg) -> Self:
        """
        Sets the video driver for this session.

        The default video driver is a ``MultiVideoDriver`` that supports the following contexts:

        - ``HardwareContext.NONE``: An ``ArrayVideoDriver``.
        - ``HardwareContext.OPENGL``: A ``ModernGlVideoDriver`` if the ``moderngl`` package is installed,
          absent if not.

        :param video: One of the following:

            - A ``VideoDriver`` that will be used as-is.
            - A ``Callable`` that returns a ``VideoDriver``.
            - A :class:`Callable` that returns a :class:`VideoDriver`.
            - :py:const:`DEFAULT` to use the default video driver.
            - :py:const:`None` to raise an error.
        :return: This builder object.
        """

        match video:
            case Callable() as func:
                self._args["video"] = func
            case VideoDriver():
                self._args["video"] = lambda: video
            case _DefaultType.DEFAULT:
                drivers: dict[HardwareContext, Callable[[], VideoDriver]] = dict()
                drivers[HardwareContext.NONE] = ArrayVideoDriver

                if ModernGlVideoDriver:
                    # If moderngl is installed...
                    drivers[HardwareContext.OPENGL] = ModernGlVideoDriver
                    drivers[HardwareContext.OPENGL_CORE] = ModernGlVideoDriver

                self._args["video"] = lambda: MultiVideoDriver(drivers)
            case None:
                raise ValueError("A video driver is required")
            case _:
                raise TypeError(
                    f"Expected a VideoDriver, a callable that returns one, or DEFAULT; got {type(video).__name__}"
                )

        return self

    def with_content_driver(self, content: ContentDriverArg) -> Self:
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
        match message:
            case Callable() as func:
                self._args["message"] = func
            case MessageInterface():
                self._args["message"] = lambda: message
            case Logger() as logger:
                self._args["message"] = lambda: LoggerMessageInterface(logger=logger)
            case _DefaultType.DEFAULT:
                self._args["message"] = LoggerMessageInterface
            case None:
                self._args["message"] = _nothing
            case _:
                raise TypeError(
                    f"Expected MessageInterface, a callable that returns one, DEFAULT, or None; got {type(message).__name__}"
                )

        return self

    def with_options(self, options: OptionDriverArg) -> Self:
        _types = (str, bytes)
        match options:
            case Callable() as func:
                self._args["options"] = func
            case OptionDriver() as driver:
                driver: OptionDriver
                self._args["options"] = lambda: driver
            case dict(vars) if all(
                isinstance(k, _types) and isinstance(v, _types) for k, v in vars.items()
            ):
                vars: Mapping[AnyStr, AnyStr]
                self._args["options"] = lambda: DictOptionDriver(2, True, vars)
            case 0 | 1 | 2 as version:
                self._args["options"] = lambda: DictOptionDriver(version)
            case _DefaultType.DEFAULT:
                self._args["options"] = DictOptionDriver
            case None:
                self._args["options"] = _nothing
            case _:
                raise TypeError(
                    f"Expected OptionDriver, a dict, a callable that returns one, DEFAULT, or None; got {type(options).__name__}"
                )

        return self

    def with_paths(self, path: PathDriverArg) -> Self:
        match path:
            case Callable() as func:
                self._args["path"] = func
            case PathDriver():
                self._args["path"] = lambda: path
            case _DefaultType.DEFAULT:
                self._args["path"] = DefaultPathDriver  # TODO: How to pass core path?
            case None:
                self._args["path"] = _nothing
            case _:
                raise TypeError(
                    f"Expected PathDriver, a callable that returns one, DEFAULT, or None; got {type(path).__name__}"
                )

        return self

    def with_log(self, log: LogDriverArg) -> Self:
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
        match location:
            case Callable() as func:
                self._args["location"] = func
            case LocationDriver():
                self._args["location"] = lambda: location
            case _DefaultType.DEFAULT:
                self._args["location"] = GeneratorLocationDriver
            case None:
                self._args["location"] = _nothing
            case _:
                raise TypeError(
                    f"Expected LocationDriver, a callable that returns one, DEFAULT, or None; got {type(location).__name__}"
                )

        return self

    def with_user(self, user: UserDriverArg) -> Self:
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
        match vfs:
            case Callable() as func:
                self._args["vfs"] = func
            case FileSystemInterface() as interface:
                interface: FileSystemInterface
                self._args["vfs"] = lambda: interface
            case 1 | 2 | 3 as version:
                self._args["vfs"] = lambda: StandardFileSystemInterface(version)
            case _DefaultType.DEFAULT:
                self._args["vfs"] = StandardFileSystemInterface
            case None:
                self._args["vfs"] = _nothing
            case _:
                raise TypeError(
                    f"Expected FileSystemInterface, a callable that returns one, DEFAULT, or None; got {type(vfs).__name__}"
                )

        return self

    def with_led(self, led: LedDriverArg) -> Self:
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
        match mic:
            case Callable() as func:
                # Either a generator or a driver type;
                def _generate():
                    match func():
                        case Generator() | Iterable() | Iterator() as gen:
                            return GeneratorMicrophoneDriver(gen)
                        case MicrophoneDriver() as driver:
                            return driver
                        case err:
                            raise TypeError(
                                f"Expected a generator, an iterable, an iterator, or a MicrophoneDriver from the callable, got {type(err).__name__}"
                            )

                self._args["mic"] = _generate
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

    def build(self) -> Session:
        """
        Constructs a Session object with the provided arguments.
        """
        core = self._args["core"]()
        content = self._args["content"]()
        envargs = CompositeEnvironmentDriver.Args(
            audio=self._args["audio"](),
            input=self._args["input"](),
            video=self._args["video"](),
            content=self._args["content_driver"](),
            overscan=self._args["overscan"](),
            message=self._args["message"](),
            options=self._args["options"](),
            path=self._args["path"](),
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
            mic_interface=self._args["mic"](),
            device_power=self._args["power"](),
        )

        environment = CompositeEnvironmentDriver(envargs)
        return Session(core, content, environment)


def defaults(core: CoreArg) -> SessionBuilder:
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
        .with_paths(DEFAULT)
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
]
