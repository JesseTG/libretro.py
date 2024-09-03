from abc import abstractmethod
from collections.abc import Callable, Sequence
from copy import deepcopy
from ctypes import (
    CDLL,
    POINTER,
    Array,
    byref,
    c_bool,
    c_char,
    c_char_p,
    c_size_t,
    c_ubyte,
    c_uint,
    c_void_p,
    cast,
    cdll,
)
from os import PathLike
from typing import Protocol

from libretro._typing import Buffer
from libretro.api import (
    Region,
    retro_audio_sample_batch_t,
    retro_audio_sample_t,
    retro_environment_t,
    retro_game_info,
    retro_input_poll_t,
    retro_input_state_t,
    retro_subsystem_info,
    retro_system_av_info,
    retro_system_info,
    retro_video_refresh_t,
)
from libretro.api._utils import memoryview_at

# TODO: Add a CorePhase enum that's updated when entering/leaving each phase.
# (Some envcalls can only be called in certain phases, so this would be useful for error checking.)

_REGION_MEMBERS = Region.__members__.values()


class CoreInterface(Protocol):
    """
    An interface for a libretro core.
    """

    @abstractmethod
    def set_environment(self, env: retro_environment_t) -> None: ...

    @abstractmethod
    def set_video_refresh(self, video: retro_video_refresh_t) -> None: ...

    @abstractmethod
    def set_audio_sample(self, audio: retro_audio_sample_t) -> None: ...

    @abstractmethod
    def set_audio_sample_batch(self, audio: retro_audio_sample_batch_t) -> None: ...

    @abstractmethod
    def set_input_poll(self, poll: retro_input_poll_t) -> None: ...

    @abstractmethod
    def set_input_state(self, state: retro_input_state_t) -> None: ...

    @abstractmethod
    def init(self) -> None: ...

    @abstractmethod
    def deinit(self) -> None: ...

    @abstractmethod
    def api_version(self) -> int: ...

    @abstractmethod
    def get_system_info(self) -> retro_system_info: ...

    @abstractmethod
    def get_system_av_info(self) -> retro_system_av_info: ...

    @abstractmethod
    def set_controller_port_device(self, port: int, device: int) -> None: ...

    @abstractmethod
    def reset(self) -> None: ...

    @abstractmethod
    def run(self) -> None: ...

    @abstractmethod
    def serialize_size(self) -> int: ...

    @abstractmethod
    def serialize(self, data: bytearray | memoryview) -> bool: ...

    @abstractmethod
    def unserialize(self, data: bytes | bytearray | memoryview) -> bool: ...

    @abstractmethod
    def cheat_reset(self) -> None: ...

    @abstractmethod
    def cheat_set(self, index: int, enabled: bool, code: bytes | bytearray | str) -> None: ...

    @abstractmethod
    def load_game(self, game: retro_game_info | None) -> bool: ...

    @abstractmethod
    def load_game_special(self, game_type: int, info: Sequence[retro_game_info]) -> bool: ...

    @abstractmethod
    def unload_game(self) -> None: ...

    @abstractmethod
    def get_region(self) -> Region: ...

    @abstractmethod
    def get_memory_data(self, id: int) -> c_void_p | None: ...

    @abstractmethod
    def get_memory_size(self, id: int) -> int: ...

    def get_memory(self, id: int) -> memoryview | None:
        """
        Convenience method that returns a writable ``memoryview``
        of the memory region given by ``id``.

        :param id: The ID of the memory region to access.
        :return: A writable ``memoryview`` of the given region,
            or ``None`` if ``retro_get_memory_data`` returned ``NULL``.
        """
        data = self.get_memory_data(id)
        if not data:
            return None

        size = self.get_memory_size(id)
        return memoryview_at(data, size, readonly=False)


class Core(CoreInterface):
    """
    A thin wrapper around a libretro core that can be used to call its public interface.
    Does not manage the underlying core's life cycle,
    i.e. ``retro_*`` methods are not called implicitly unless otherwise noted;
    that's left to ``Session`` or some custom abstraction layer.
    """

    def __init__(self, core: CDLL | PathLike | str):
        """
        Create a new ``Core`` instance.

        :param core: The core to wrap. Can be one of the following:

            - A ``str`` or ``PathLike`` representing the path to the core's shared library.
            - A ``CDLL`` representing the core's shared library.

        :raises ValueError: If the core does not define all the required functions
            (i.e. the ``retro_*`` function that each method corresponds to).
        :raises TypeError: If ``core`` is not one of the above-mentioned types.
        """

        match core:
            case CDLL():
                self._core = core
            case str(path) | PathLike(path):
                self._core = cdll.LoadLibrary(path)
            case _:
                raise TypeError(
                    f"Expected a CDLL instance or a path to a core, got {type(core).__name__}"
                )

        try:
            self._core.retro_set_environment.argtypes = [retro_environment_t]
            self._core.retro_set_environment.restype = None

            self._core.retro_set_video_refresh.argtypes = [retro_video_refresh_t]
            self._core.retro_set_video_refresh.restype = None

            self._core.retro_set_audio_sample.argtypes = [retro_audio_sample_t]
            self._core.retro_set_audio_sample.restype = None

            self._core.retro_set_audio_sample_batch.argtypes = [retro_audio_sample_batch_t]
            self._core.retro_set_audio_sample_batch.restype = None

            self._core.retro_set_input_poll.argtypes = [retro_input_poll_t]
            self._core.retro_set_input_poll.restype = None

            self._core.retro_set_input_state.argtypes = [retro_input_state_t]
            self._core.retro_set_input_state.restype = None

            self._core.retro_init.argtypes = []
            self._core.retro_init.restype = None

            self._core.retro_deinit.argtypes = []
            self._core.retro_deinit.restype = None

            self._core.retro_api_version.argtypes = []
            self._core.retro_api_version.restype = c_uint

            self._core.retro_get_system_info.argtypes = [
                POINTER(retro_system_info),
            ]
            self._core.retro_get_system_info.restype = None

            self._core.retro_get_system_av_info.argtypes = [
                POINTER(retro_system_av_info),
            ]
            self._core.retro_get_system_av_info.restype = None

            self._core.retro_set_controller_port_device.argtypes = [c_uint, c_uint]
            self._core.retro_set_controller_port_device.restype = None

            self._core.retro_reset.argtypes = []
            self._core.retro_reset.restype = None

            self._core.retro_run.argtypes = []
            self._core.retro_run.restype = None

            self._core.retro_serialize_size.argtypes = []
            self._core.retro_serialize_size.restype = c_size_t

            self._core.retro_serialize.argtypes = [c_void_p, c_size_t]
            self._core.retro_serialize.restype = c_bool

            self._core.retro_unserialize.argtypes = [c_void_p, c_size_t]
            self._core.retro_unserialize.restype = c_bool

            self._core.retro_cheat_reset.argtypes = []
            self._core.retro_cheat_reset.restype = None

            self._core.retro_cheat_set.argtypes = [c_uint, c_bool, c_char_p]
            self._core.retro_cheat_set.restype = None

            self._core.retro_load_game.argtypes = [POINTER(retro_game_info)]
            self._core.retro_load_game.restype = c_bool

            self._core.retro_load_game_special.argtypes = [
                c_uint,
                POINTER(retro_game_info),
                c_size_t,
            ]
            self._core.retro_load_game_special.restype = c_bool

            self._core.retro_unload_game.argtypes = []
            self._core.retro_unload_game.restype = None

            self._core.retro_get_region.argtypes = []
            self._core.retro_get_region.restype = c_uint

            self._core.retro_get_memory_data.argtypes = [c_uint]
            self._core.retro_get_memory_data.restype = POINTER(c_ubyte)
            self._core.retro_get_memory_data.errcheck = lambda v, *a: cast(v, c_void_p)

            self._core.retro_get_memory_size.argtypes = [c_uint]
            self._core.retro_get_memory_size.restype = c_size_t
        except AttributeError as e:
            raise ValueError(
                f"Couldn't find required symbol '{e.name}' in {self._core._name}"
            ) from e

        # Need to keep references to these objects to prevent them from being garbage collected,
        # otherwise the C function pointers to them will become invalid.
        self._environment: retro_environment_t | None = None
        self._video_refresh: retro_video_refresh_t | None = None
        self._audio_sample: retro_audio_sample_t | None = None
        self._audio_sample_batch: retro_audio_sample_batch_t | None = None
        self._input_poll: retro_input_poll_t | None = None
        self._input_state: retro_input_state_t | None = None

    def set_environment(self, env: retro_environment_t) -> None:
        """
        Calls the core's ``retro_set_environment`` function with the given callback.

        :param env: The function that the core should use for environment calls.
        :raises TypeError: If ``env`` is not a ``retro_environment_t``.
        """
        match env:
            case retro_environment_t():
                self._environment = env
            case Callable():
                self._environment = retro_environment_t(env)
            case _:
                raise TypeError(
                    f"Expected a retro_environment_t or an equivalent callable, got {type(env).__name__}"
                )

        self._core.retro_set_environment(self._environment)

    def set_video_refresh(self, video: retro_video_refresh_t) -> None:
        """
        Calls the core's ``retro_set_video_refresh`` function with the given callback.

        :param video: The function that the core should call to update its video output.
        :raises TypeError: If ``video`` is not a ``retro_video_refresh_t``.
        """
        match video:
            case retro_video_refresh_t():
                self._video_refresh = video
            case Callable():
                self._video_refresh = retro_video_refresh_t(video)
            case _:
                raise TypeError(
                    f"Expected a retro_video_refresh_t or an equivalent callable, got {type(video).__name__}"
                )

        self._core.retro_set_video_refresh(self._video_refresh)

    def set_audio_sample(self, audio: retro_audio_sample_t) -> None:
        """
        Calls the core's ``retro_set_audio_sample`` function with the given callback.

        :param audio: The function that the core should call to render a single audio frame.
        :raises TypeError: If ``audio`` is not a ``retro_audio_sample_t``.
        """
        match audio:
            case retro_audio_sample_t():
                self._audio_sample = audio
            case Callable():
                self._audio_sample = retro_audio_sample_t(audio)
            case _:
                raise TypeError(
                    f"Expected a retro_audio_sample_t or an equivalent callable, got {type(audio).__name__}"
                )

        self._core.retro_set_audio_sample(self._audio_sample)

    def set_audio_sample_batch(self, audio: retro_audio_sample_batch_t) -> None:
        """
        Calls the core's ``retro_set_audio_sample_batch`` function with the given callback.

        :param audio: The function that the core should call to render a batch of audio frames.
        :raises TypeError: If ``audio`` is not a ``retro_audio_sample_batch_t``.
        """
        match audio:
            case retro_audio_sample_batch_t():
                self._audio_sample_batch = audio
            case Callable():
                self._audio_sample_batch = retro_audio_sample_batch_t(audio)
            case _:
                raise TypeError(
                    f"Expected a retro_audio_sample_batch_t or an equivalent callable, got {type(audio).__name__}"
                )

        self._core.retro_set_audio_sample_batch(self._audio_sample_batch)

    def set_input_poll(self, poll: retro_input_poll_t) -> None:
        """
        Calls the core's ``retro_set_input_poll`` function with the given callback.

        :param poll: The function that the core should call to poll for updated input state.
        :raises TypeError: If ``poll`` is not a ``retro_input_poll_t``.
        """
        match poll:
            case retro_input_poll_t():
                self._input_poll = poll
            case Callable():
                self._input_poll = retro_input_poll_t(poll)
            case _:
                raise TypeError(
                    f"Expected a retro_input_poll_t or an equivalent callable, got {type(poll).__name__}"
                )

        self._core.retro_set_input_poll(self._input_poll)

    def set_input_state(self, state: retro_input_state_t) -> None:
        """
        Calls the core's ``retro_set_input_state`` function with the given callback.

        :param state: The function that the core should call to request part of the input state.
        :raises TypeError: If ``state`` is not a ``retro_input_state_t``.
        """
        match state:
            case retro_input_state_t():
                self._input_state = state
            case Callable():
                self._input_state = retro_input_state_t(state)
            case _:
                raise TypeError(
                    f"Expected a retro_input_state_t or an equivalent callable, got {type(state).__name__}"
                )

        self._core.retro_set_input_state(self._input_state)

    def init(self):
        """
        Calls the core's ``retro_init`` function.

        :note: This method does not check if the core has already been initialized.
            Additionally, this method is not implicitly called by ``__init__``.
        """
        self._core.retro_init()

    def deinit(self):
        """
        Calls the core's ``retro_deinit`` function.

        :note: This method does not validate that the core has been initialized.
            Additionally, it is not implicitly called upon deletion.
        """
        self._core.retro_deinit()

    def api_version(self) -> int:
        """
        Calls the core's ``retro_api_version`` function.

        :return: The integer returned by the core's implementation of ``retro_api_version``.

        :warning: This method does not validate the returned version number.
        """
        return self._core.retro_api_version()

    def get_system_info(self) -> retro_system_info:
        """
        Calls the core's ``retro_get_system_info`` function.

        :return: A ``retro_system_info`` instance containing information about the core.
            All strings are copied and may be accessed even after unloading the core.
        """
        system_info = retro_system_info()
        self._core.retro_get_system_info(byref(system_info))

        return deepcopy(system_info)

    def get_system_av_info(self) -> retro_system_av_info:
        """
        Calls the core's ``retro_get_system_av_info`` function.

        :return: A ``retro_system_av_info`` instance
            containing information about the core's audiovisual capabilities.
            It may be accessed even after unloading the core.
        """
        system_av_info = retro_system_av_info()
        self._core.retro_get_system_av_info(byref(system_av_info))
        return system_av_info

    def set_controller_port_device(self, port: int, device: int):
        """
        Calls the core's ``retro_set_controller_port_device`` function with the given arguments.

        :param port: The port to set the device for.
            Masked to fit within the range of an ``unsigned int``.
        :param device: The device to assign to ``port``.
            Masked to fit within the range of an ``unsigned int``.
        """
        self._core.retro_set_controller_port_device(port, device)

    def reset(self):
        """
        Calls the core's ``retro_reset`` function.

        :warning: Does not check if the core is in a state where it can be reset.
        """
        self._core.retro_reset()

    def run(self):
        """
        Calls the core's ``retro_run`` function.

        :warning: Does not check if the core is in a state where it can be run.
        """
        self._core.retro_run()

    def serialize_size(self) -> int:
        """
        Calls the core's ``retro_serialize_size`` function.

        :return: The length of the buffer needed to serialize the core's state, in bytes.
            If zero, the core does not support serialization.
        """
        return self._core.retro_serialize_size()

    def serialize(self, data: bytearray | memoryview | Buffer) -> bool:
        """
        Calls the core's ``retro_serialize`` function with the given mutable buffer and its length,
        filling it with whatever data the core returns.

        :param data: A ``bytearray``, mutable ``memoryview``, or ``Buffer`` implementation
            that core's serialized state will be saved to.
        :return: ``True`` if the core successfully serialized its state, ``False`` otherwise.
        :raise TypeError: If ``data`` is not one of the aforementioned types.
        :raise ValueError: If ``data`` is a read-only ``memoryview`` or ``Buffer``.

        :note: The buffer must be at least as large as the last value returned by ``serialize_size``,
            or else the serialized data will be incomplete.
        """
        buf: memoryview
        match data:
            case memoryview() as mem if mem.readonly:
                raise ValueError("data must not be readonly")
            case memoryview():
                buf = data
            case bytearray() | Buffer():
                buf = memoryview(data)
            case _:
                raise TypeError(
                    f"Expected a bytearray, writable Buffer, or writable memoryview; got {type(data).__name__}"
                )

        buflength = len(buf)
        arraytype: Array = c_char * buflength

        return self._core.retro_serialize(byref(arraytype.from_buffer(buf)), buflength)

    def unserialize(self, data: bytes | bytearray | memoryview | Buffer) -> bool:
        """
        Calls the core's ``retro_unserialize`` function with the given buffer and its length,
        restoring the core's state from the serialized data.

        :param data: A ``bytes``, ``bytearray``, ``memoryview``, or ``Buffer``.
        :raises TypeError: If ``data`` is not one of the aforementioned types.
        :return: ``True`` if the core successfully loaded a state from ``data``, ``False`` if not.
        """
        buf: memoryview
        match data:
            case bytes():
                buf = memoryview_at(data, len(data), readonly=False)
                # HACK! ctypes.Array.from_buffer requires a writable buffer,
                # but bytes objects are read-only.
                # retro_unserialize isn't supposed to modify the buffer,
                # so we can blame undefined behavior if the core tries to write to it anyway.
            case bytearray() | Buffer():
                buf = memoryview(data)
            case memoryview():
                buf = data
            case _:
                raise TypeError(
                    f"Expected bytes, bytearray, memoryview, or Buffer; got {type(data).__name__}"
                )

        buflen = len(buf)
        arraytype: Array = c_char * buflen

        # TODO: Validate that the buffer wasn't written to, and raise a warning if it was. (Use zlib.crc32)
        return self._core.retro_unserialize(byref(arraytype.from_buffer(buf)), buflen)

    def cheat_reset(self):
        """
        Calls the core's ``retro_cheat_reset`` function.
        """
        self._core.retro_cheat_reset()

    def cheat_set(self, index: int, enabled: bool, code: bytes | bytearray | str):
        """
        Calls the core's ``retro_cheat_set`` function with the given arguments.

        :param index: The number of the cheat code to toggle.
        :param enabled: Whether the cheat code should be enabled or disabled.
        :param code: A buffer containing a zero-terminated byte string.
        :raise TypeError: If any parameter's value is inconsistent with its documented type.
        :raise ValueError: If ``code`` does not contain a null terminator (i.e. the value 0).
        """
        if not isinstance(index, int):
            raise TypeError(f"Expected int, got {type(index).__name__}")

        if not isinstance(enabled, bool):
            raise TypeError(f"Expected bool, got {type(enabled).__name__}")

        buf: bytes
        match code:
            case bytes():
                buf = code
            case bytearray():
                buf = bytes(code)
            case str():
                buf = code.encode()
            case _:
                raise TypeError(f"Expected bytes, bytearray, or str; got {type(code).__name__}")

        self._core.retro_cheat_set(index, enabled, buf)

    def load_game(self, game: retro_game_info | None) -> bool:
        """
        Calls the core's ``retro_load_game`` function with the given game info.

        :param game: A ``retro_game_info`` instance or ``None``.
        :return: ``True`` if the core successfully loaded ``game``, ``False`` otherwise.
        :raises TypeError: If ``game`` is not a ``retro_game_info`` or ``None``.
        :warning: This method does not validate any preconditions documented in libretro.h,
            e.g. it's possible to pass ``None`` even if the core doesn't support no-content mode.
        """
        match game:
            case retro_game_info():
                return self._core.retro_load_game(byref(game))
            case None:
                return self._core.retro_load_game(None)
            case _:
                raise TypeError(f"Expected retro_game_info or None, got {type(game).__name__}")

    def load_game_special(
        self,
        game_type: int | retro_subsystem_info,
        info: Sequence[retro_game_info] | Array[retro_game_info],
    ) -> bool:
        """
        Calls the core's ``retro_load_game_special`` function with the given arguments.

        :param game_type: The subsystem type to activate.
            May be passed as an ``int`` or a ``retro_subsystem_info`` instance.
        :param info: A ``Sequence`` or ``ctypes.Array`` of ``retro_game_info`` instances.
        :return: ``True`` if the core successfully loaded the game, ``False`` if not.
        :raises TypeError: If any parameter's value is inconsistent with its documented type.
        :warning: This method does not validate any preconditions documented in libretro.h,
            e.g. it's possible to use this method even if the core doesn't define subsystems.
        """
        _type: int
        match game_type:
            case int():
                _type = game_type
            case retro_subsystem_info():
                _type = game_type.id
            case _:
                raise TypeError(
                    f"Expected int or retro_subsystem_info, got {type(game_type).__name__}"
                )

        _array: Array[retro_game_info]

        if isinstance(info, Array):
            _array = info
        elif isinstance(info, Sequence):
            GameInfoArray: type[Array] = retro_game_info * len(info)
            _array = GameInfoArray(*info)
        else:
            raise TypeError(
                f"Expected a Sequence or ctypes Array of retro_game_info, got {type(info).__name__}"
            )

        if not all(isinstance(i, retro_game_info) for i in info):
            raise TypeError("All elements of info must be retro_game_info instances")

        return self._core.retro_load_game_special(_type, _array, len(_array))

    def unload_game(self):
        """
        Calls the core's ``retro_unload_game`` function.

        :warning: Does not check if the preconditions for ``retro_unload_game`` are met,
            e.g. it doesn't check if a game is currently loaded.
        """
        self._core.retro_unload_game()

    def get_region(self) -> Region | int:
        """
        Calls the core's ``retro_get_region`` function.

        :return: The returned region as a ``Region`` enum if it's a known value,
            or as a plain ``int`` if not.
        """
        region: int = self._core.retro_get_region()
        return Region(region) if region in _REGION_MEMBERS else region

    def get_memory_data(self, id: int) -> c_void_p | None:
        """
        Calls the core's ``retro_get_memory_data`` function for the given memory region.

        :param id: The ID of the memory region to access.
        :return: Pointer to the memory region returned by the core,
            or ``None`` if the core returned ``NULL``.

        :raises TypeError: If ``id`` is not an ``int``.
        """
        if not isinstance(id, int):
            raise TypeError(f"Expected int, got {type(id).__name__}")

        return self._core.retro_get_memory_data(id)

    def get_memory_size(self, id: int) -> int:
        """
        Calls the core's ``retro_get_memory_size`` function for the given memory region.

        :param id: The ID of the memory region to get the size of.
        :raises TypeError: If ``id`` is not an ``int``.
        :return: The size of the memory region, in bytes.
        """
        if not isinstance(id, int):
            raise TypeError(f"Expected int, got {type(id).__name__}")

        return self._core.retro_get_memory_size(id)

    @property
    def path(self) -> str:
        """
        The path to the core's shared library.
        """
        return self._core._name


__all__ = [
    "CoreInterface",
    "Core",
]
