"""
Types for describing input devices.
"""

from __future__ import annotations

from ctypes import POINTER, Structure, c_char_p, c_int16, c_uint
from dataclasses import dataclass
from enum import CONFORM, IntEnum, IntFlag
from typing import NewType, overload

from libretro.api._utils import MemoDict, deepcopy_array
from libretro.ctypes import CIntArg, TypedFunctionPointer, TypedPointer

Port = NewType("Port", int)
"""
A controller port index.

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
Called by the :class:`.Core` once per frame to poll input devices.

.. seealso::
    :attr:`.InputDriver.poll`
        The :class:`.InputDriver` method that implements this callback.

    :attr:`.Core.set_input_poll`
        The method that exposes this callback to a :class:`.Core` instance.
"""

retro_input_state_t = TypedFunctionPointer[
    c_int16, [CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_uint], CIntArg[c_uint]]
]
"""
Called by the :class:`.Core` to query the state of a specific type of input.

.. seealso::
    :attr:`.InputDriver.state`
        The suggested entry point for this callback in libretro.py.

    :attr:`.Core.set_input_state`
        The method that exposes this callback to a :class:`.Core` instance.
"""


RETRO_DEVICE_TYPE_SHIFT = 8
RETRO_DEVICE_MASK = (1 << RETRO_DEVICE_TYPE_SHIFT) - 1


def RETRO_DEVICE_SUBCLASS(base: int, id: int) -> int:
    return ((id + 1) << RETRO_DEVICE_TYPE_SHIFT) | base


class InputDeviceFlag(IntFlag, boundary=CONFORM):
    """Bitmask flags for input device types.

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
    Describes a single kind of input action for a given device.

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
        Returns a deep copy of this object, including all strings.

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
    Describes a kind of controller emulated by a :class:`.Core`.

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
        Creates a deep copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_controller_description(self.desc, self.id)


@dataclass(init=False, slots=True)
class retro_controller_info(Structure):
    """
    Lists the controller types available for a port.
    This class can be indexed like a :class:`.Sequence`
    to access individual :class:`.retro_controller_description` entries.

    Corresponds to :c:type:`retro_controller_info` in ``libretro.h``.
    """

    types: TypedPointer[retro_controller_description] | None
    """Array of controller types supported by this port."""

    num_types: int
    """Number of entries in :attr:`types`."""

    _fields_ = (
        ("types", POINTER(retro_controller_description)),
        ("num_types", c_uint),
    )

    def __deepcopy__(self, memo: MemoDict):
        return retro_controller_info(
            types=(deepcopy_array(self.types, self.num_types, memo) if self.types else None),
            num_types=self.num_types,
        )

    @overload
    def __getitem__(self, index: int) -> retro_controller_description: ...

    @overload
    def __getitem__(
        self, index: slice[retro_controller_description]
    ) -> list[retro_controller_description]: ...

    def __getitem__(self, index: int | slice[retro_controller_description]):
        """
        Returns the :class:`.retro_controller_description` at the given index or slice.

        :param index: An integer index or slice object.
        :raises ValueError: If there are no controller types available.
        :raises IndexError: If the index is out of range.
        :raises TypeError: If the index is not an int or slice.
        """
        if not self.types:
            raise ValueError("No controller types available")

        match index:
            case int(i) if 0 <= i < self.num_types:
                return self.types[i]
            case int(i):
                raise IndexError(f"Expected 0 <= index < {len(self)}, got {i}")
            case slice() as s:
                return self.types[s]
            case _:
                raise TypeError(f"Expected an int or slice index, got {type(index).__name__}")

    def __len__(self):
        """
        :returns: :attr:`num_types`
        """
        return self.num_types


class InputDeviceState:
    """
    Empty marker class for identifying input device states.
    """

    pass


__all__ = [
    "InputDeviceFlag",
    "InputDevice",
    "retro_input_poll_t",
    "retro_input_state_t",
    "retro_input_descriptor",
    "retro_controller_description",
    "retro_controller_info",
    "InputDeviceState",
    "Port",
]
