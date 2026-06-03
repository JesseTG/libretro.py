"""Input device definitions and state callbacks."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from ctypes import POINTER, Array, Structure, c_char_p, c_int16, c_uint
from dataclasses import dataclass
from enum import CONFORM, IntEnum, IntFlag
from typing import NewType, overload

from libretro.api._utils import MemoDict, NullPointerToNoneMixin, deepcopy_array
from libretro.ctypes import (
    CIntArg,
    TypedArray,
    TypedFunctionPointer,
    TypedPointer,
)

Port = NewType("Port", int)
"""
A controller :term:`port` index.

Intended for type safety when working with controller ports.
"""

RETRO_DEVICE_NONE = 0
RETRO_DEVICE_JOYPAD = 1
RETRO_DEVICE_MOUSE = 2
RETRO_DEVICE_KEYBOARD = 3
RETRO_DEVICE_LIGHTGUN = 4
RETRO_DEVICE_ANALOG = 5
RETRO_DEVICE_POINTER = 6


retro_input_poll_t = TypedFunctionPointer[None, []]
"""
Poll input devices for the current frame.

Registered by the :term:`frontend` and called by the :term:`core`
at least once per :c:func:`retro_run` to refresh cached input state
before any calls to :c:type:`retro_input_state_t`.

Corresponds to :c:type:`retro_input_poll_t` in ``libretro.h``.

.. seealso::
    :attr:`.InputDriver.poll`
        The :class:`.InputDriver` method that implements this callback.

    :attr:`.Core.set_input_poll`
        The method that exposes this callback to a :term:`core`.
"""

retro_input_state_t = TypedFunctionPointer[
    c_int16, [CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_uint]]
]
"""
Query the state of a specific input on a controller.

Registered by the :term:`frontend` and called by the :term:`core`
to read the most recently polled input.

:param port: Index of the controller :term:`port` to query.
:param device: One of the :class:`InputDevice` constants identifying the abstract device type.
    The value is masked with ``RETRO_DEVICE_MASK``.
:param index: Sub-index whose meaning depends on ``device``
    (e.g. an analog stick index).
:param id: Identifier of the specific input to read,
    such as one of the ``RETRO_DEVICE_ID_*`` constants.
:return: The current input value;
    semantics depend on ``device`` and ``id``,
    and ``0`` is returned for unsupported combinations.

Corresponds to :c:type:`retro_input_state_t` in ``libretro.h``.

.. seealso::
    :attr:`.InputDriver.state`
        The suggested entry point for this callback in libretro.py.

    :attr:`.Core.set_input_state`
        The method that exposes this callback to a :term:`core`.
"""


RETRO_DEVICE_TYPE_SHIFT = 8
RETRO_DEVICE_MASK = (1 << RETRO_DEVICE_TYPE_SHIFT) - 1


def RETRO_DEVICE_SUBCLASS(base: int, id: int) -> int:
    """Generate an ID for a libretro input device subclass."""
    return ((id + 1) << RETRO_DEVICE_TYPE_SHIFT) | base


class InputDeviceFlag(IntFlag, boundary=CONFORM):
    """
    Bitmask flag equivalent of :class:`InputDevice`.

    >>> from libretro.api.input import InputDeviceFlag
    >>> InputDeviceFlag.JOYPAD
    <InputDeviceFlag.JOYPAD: 2>
    """

    NONE = 1 << RETRO_DEVICE_NONE
    JOYPAD = 1 << RETRO_DEVICE_JOYPAD
    MOUSE = 1 << RETRO_DEVICE_MOUSE
    KEYBOARD = 1 << RETRO_DEVICE_KEYBOARD
    LIGHTGUN = 1 << RETRO_DEVICE_LIGHTGUN
    ANALOG = 1 << RETRO_DEVICE_ANALOG
    POINTER = 1 << RETRO_DEVICE_POINTER

    ALL = JOYPAD | MOUSE | KEYBOARD | LIGHTGUN | ANALOG | POINTER


class InputDevice(IntEnum):
    """
    Enumeration of standard input device types.

    Corresponds to the ``RETRO_DEVICE_*`` constants in ``libretro.h``.

    >>> from libretro.api.input import InputDevice
    >>> InputDevice.JOYPAD
    <InputDevice.JOYPAD: 1>
    """

    NONE = RETRO_DEVICE_NONE
    JOYPAD = RETRO_DEVICE_JOYPAD
    MOUSE = RETRO_DEVICE_MOUSE
    KEYBOARD = RETRO_DEVICE_KEYBOARD
    LIGHTGUN = RETRO_DEVICE_LIGHTGUN
    ANALOG = RETRO_DEVICE_ANALOG
    POINTER = RETRO_DEVICE_POINTER

    @property
    def flag(self) -> InputDeviceFlag:
        """Returns the corresponding :class:`InputDeviceFlag` for this device."""
        return InputDeviceFlag(1 << self.value)


@dataclass(init=False, slots=True)
class retro_input_descriptor(Structure):
    """
    Description of a single input action for a given device.

    Corresponds to :c:type:`retro_input_descriptor` in ``libretro.h``.
    """

    port: Port
    """Controller port index."""

    device: int
    """Input device type."""

    index: int
    """Sub-device index (e.g. analog stick index)."""

    id: int
    """Button or axis identifier."""

    description: bytes | None
    """Human-readable label for this input."""

    _fields_ = (
        ("port", c_uint),
        ("device", c_uint),
        ("index", c_uint),
        ("id", c_uint),
        ("description", c_char_p),
    )

    def __deepcopy__(self, _):
        """
        Return a deep copy of this object, including all strings.

        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_input_descriptor(
            port=self.port,
            device=self.device,
            index=self.index,
            id=self.id,
            description=self.description,
        )


@dataclass(init=False, slots=True)
class retro_controller_description(Structure):
    """
    Description of a specific kind of controller emulated by a :term:`core`.

    Corresponds to :c:type:`retro_controller_description` in ``libretro.h``.
    """

    desc: bytes | None
    """Human-readable name of the controller type."""

    id: int
    """Device type identifier, used with :c:func:`retro_set_controller_port_device`."""

    _fields_ = (
        ("desc", c_char_p),
        ("id", c_uint),
    )

    def __deepcopy__(self, _):
        """
        Create a deep copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_controller_description(self.desc, self.id)


@dataclass(init=False, slots=True)
class retro_controller_info(Structure, NullPointerToNoneMixin):
    r"""
    List of controller types usable by a controller :term:`port`.

    Can be indexed like a :class:`.Sequence`
    to access individual :class:`.retro_controller_description`\s.

    Corresponds to :c:type:`retro_controller_info` in ``libretro.h``.

    Iterating an instance yields each :class:`.retro_controller_description`
    in turn:

    >>> from libretro.api import retro_controller_description, retro_controller_info
    >>> descs = (retro_controller_description * 2)(
    ...     retro_controller_description(b'Game Pad', 5),
    ...     retro_controller_description(b'Analog Stick', 2),
    ... )
    >>> info = retro_controller_info(descs, 2)
    >>> len(info)
    2
    >>> [d.desc for d in info]
    [b'Game Pad', b'Analog Stick']
    """

    types: TypedPointer[retro_controller_description] | None
    """Array of controller types supported by this port."""

    num_types: int
    """Number of entries in :attr:`types`."""

    _fields_ = (
        ("types", POINTER(retro_controller_description)),
        ("num_types", c_uint),
    )

    def __init__(
        self,
        types: TypedPointer[retro_controller_description]
        | TypedArray[retro_controller_description]
        | Sequence[retro_controller_description]
        | Array[retro_controller_description]
        | None = None,
        num_types: CIntArg[c_uint] | None = None,
    ):
        """
        Initialize a :class:`retro_controller_info`.

        When *types* is a :class:`~ctypes.Array`,
        its address is used to initialize :attr:`types`.

        When *types* is an :class:`~collections.abc.Sequence` (but not a pointer or ),
        it is converted to a :class:`~ctypes.Array`
        and *num_types* defaults to its length:

        >>> from libretro.api import retro_controller_description, retro_controller_info
        >>> descs = [retro_controller_description(b'Game Pad', 1)]
        >>> info = retro_controller_info(types=descs)
        >>> len(info)
        1

        :param types: Array of controller descriptions as a pointer, array, or sequence.
        :param num_types: Number of controller types;
            inferred from *types* when it is an array or sequence,
            and ``0`` when it is a pointer.
        """
        if types is not None and not isinstance(types, (TypedPointer, Array)):
            items = list(types)
            types = (retro_controller_description * len(items))(*items)

        if num_types is None:
            num_types = len(types) if isinstance(types, Array) else 0

        super().__init__(types, num_types)

    def __deepcopy__(self, memo: MemoDict):
        """
        Return a deep copy of this object, including all strings and arrays.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_controller_info(
            types=(deepcopy_array(self.types, self.num_types, memo) if self.types else None),
            num_types=self.num_types,
        )

    @overload
    def __getitem__(self, index: int) -> retro_controller_description: ...

    @overload
    def __getitem__(self, index: slice[int | None]) -> list[retro_controller_description]: ...

    def __getitem__(self, index: int | slice[int | None]):
        """
        Return the :class:`.retro_controller_description` at the given index or slice.

        Supports negative indexes in the usual Python fashion:

        >>> from libretro.api import retro_controller_description, retro_controller_info
        >>> descs = (retro_controller_description * 2)(
        ...     retro_controller_description(b'Game Pad', 1),
        ...     retro_controller_description(b'Analog Stick', 2),
        ... )
        >>> info = retro_controller_info(descs, 2)
        >>> info[-1].desc
        b'Analog Stick'

        :param index: An integer index or slice.
        :raises ValueError: If there are no controller types available.
        :raises IndexError: If ``index`` is an integer outside ``[-len, len)``.
        :raises TypeError: If ``index`` is neither an :class:`int` nor a :class:`slice`.
        """
        if not self.types:
            raise ValueError("No controller types available")

        match index:
            case int(i):
                n = len(self)
                if not (-n <= i < n):
                    raise IndexError(f"Expected {-n} <= index < {n}, got {i}")
                if i < 0:
                    i += n
                return self.types[i]
            case slice() as s:
                return self.types[s]
            case _:
                raise TypeError(f"Expected an int or slice index, got {type(index).__name__}")

    def __len__(self):
        """
        Return the number of device types.

        :return: :attr:`num_types`.
        """
        return self.num_types

    def __iter__(self) -> Iterator[retro_controller_description]:
        """
        Iterate over the controller descriptions for this port.

        Returns no elements when :attr:`types` is :obj:`None`:

        >>> from libretro.api import retro_controller_info
        >>> list(retro_controller_info())
        []
        """
        if not self.types:
            return
        for i in range(self.num_types):
            yield self.types[i]

    def __contains__(self, item: object) -> bool:
        """
        Test whether ``item`` appears in this sequence.

        :param item: The element to search for.
        :return: :obj:`True` if found, :obj:`False` otherwise.
        """
        return any(v is item or v == item for v in self)

    def __reversed__(self) -> Iterator[retro_controller_description]:
        """
        Iterate over the controller descriptions in reverse order.

        Returns no elements when :attr:`types` is :obj:`None`.

        :return: An iterator over the descriptions in reverse order.
        """
        if not self.types:
            return
        for i in range(self.num_types - 1, -1, -1):
            yield self.types[i]

    def count(self, value: object) -> int:
        """
        Count occurrences of ``value`` in this sequence.

        :param value: The element to count.
        :return: The number of times ``value`` appears.
        """
        return sum(1 for v in self if v is value or v == value)

    def index(self, value: object, start: int = 0, stop: int | None = None) -> int:
        """
        Return the index of the first occurrence of ``value``.

        :param value: The element to search for.
        :param start: Optional start index (inclusive).
        :param stop: Optional stop index (exclusive).
        :return: The index of the first match within ``[start, stop)``.
        :raises ValueError: If ``value`` is not found within the given range.
        """
        n = len(self)
        if start < 0:
            start = max(n + start, 0)
        if stop is None:
            stop = n
        elif stop < 0:
            stop = max(n + stop, 0)
        for i in range(start, min(stop, n)):
            v = self[i]
            if v is value or v == value:
                return i
        raise ValueError(f"{value!r} is not in sequence")


Sequence.register(retro_controller_info)  # type: ignore
# Sequence.register isn't part of the type stubs


class InputDeviceState:
    """Empty marker class for identifying input device states."""

    pass


__all__ = [
    "InputDeviceFlag",
    "InputDevice",
    "RETRO_DEVICE_SUBCLASS",
    "retro_input_poll_t",
    "retro_input_state_t",
    "retro_input_descriptor",
    "retro_controller_description",
    "retro_controller_info",
    "InputDeviceState",
    "Port",
]
