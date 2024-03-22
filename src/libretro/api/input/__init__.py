from abc import abstractmethod
from collections.abc import Iterator, Sequence
from ctypes import CFUNCTYPE, c_int16, c_uint
from dataclasses import dataclass, is_dataclass
from enum import IntEnum, IntFlag, CONFORM
from typing import Callable, Protocol, runtime_checkable, final

from ...h import *
from .analog import AnalogState, DeviceIndexAnalog, DeviceIdAnalog
from .joypad import JoypadState, DeviceIdJoypad
from .keyboard import Key, KeyModifier, KeyboardState
from .lightgun import LightGunState, DeviceIdLightgun
from .mouse import MouseState, DeviceIdMouse
from .pointer import PointerState, DeviceIdPointer, Pointer

retro_input_poll_t = CFUNCTYPE(None, )
retro_input_state_t = CFUNCTYPE(c_int16, c_uint, c_uint, c_uint, c_uint)


class InputDeviceFlag(IntFlag, boundary=CONFORM):
    NONE = 1 << RETRO_DEVICE_NONE
    JOYPAD = 1 << RETRO_DEVICE_JOYPAD
    MOUSE = 1 << RETRO_DEVICE_MOUSE
    KEYBOARD = 1 << RETRO_DEVICE_KEYBOARD
    LIGHTGUN = 1 << RETRO_DEVICE_LIGHTGUN
    ANALOG = 1 << RETRO_DEVICE_ANALOG
    POINTER = 1 << RETRO_DEVICE_POINTER

    ALL = JOYPAD | MOUSE | KEYBOARD | LIGHTGUN | ANALOG | POINTER


class InputDevice(IntEnum):
    NONE = RETRO_DEVICE_NONE
    JOYPAD = RETRO_DEVICE_JOYPAD
    MOUSE = RETRO_DEVICE_MOUSE
    KEYBOARD = RETRO_DEVICE_KEYBOARD
    LIGHTGUN = RETRO_DEVICE_LIGHTGUN
    ANALOG = RETRO_DEVICE_ANALOG
    POINTER = RETRO_DEVICE_POINTER

    def __init__(self, value: int):
        self._type_ = 'H'

    @property
    def flag(self) -> InputDeviceFlag:
        return InputDeviceFlag(1 << self.value)


@runtime_checkable
class InputCallbacks(Protocol):
    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def state(self, port: int, device: int, index: int, id: int) -> int: ...


@runtime_checkable
class InputState(InputCallbacks, Protocol):
    @property
    @abstractmethod
    def device_capabilities(self) -> InputDeviceFlag: ...

    @property
    @abstractmethod
    def bitmasks_supported(self) -> bool: ...


@dataclass(frozen=True, order=True, slots=True)
class Point:
    x: int = 0
    y: int = 0


class Direction(IntEnum):
    RIGHT = 0,
    UP = 1,
    LEFT = 2,
    DOWN = 3,

    def matches_direction(self, other: DeviceIdJoypad | Key | DeviceIdLightgun) -> bool:
        match (self, other):
            case (Direction.RIGHT, DeviceIdJoypad.RIGHT | Key.RIGHT | DeviceIdLightgun.DPAD_RIGHT):
                return True
            case (Direction.UP, DeviceIdJoypad.UP | Key.UP | DeviceIdLightgun.DPAD_UP):
                return True
            case (Direction.LEFT, DeviceIdJoypad.LEFT | Key.LEFT | DeviceIdLightgun.DPAD_LEFT):
                return True
            case (Direction.DOWN, DeviceIdJoypad.DOWN | Key.DOWN | DeviceIdLightgun.DPAD_DOWN):
                return True
            case _:
                return False


DeviceState = JoypadState | MouseState | KeyboardState | LightGunState | AnalogState | PointerState


@dataclass(frozen=True, slots=True)
class PortState:
    joypad: JoypadState | None = None
    mouse: MouseState | None = None
    keyboard: KeyboardState | None = None
    light_gun: LightGunState | None = None
    analog: AnalogState | None = None
    pointer: PointerState | None = None

    def __getitem__(self, item) -> DeviceState | None:
        match item:
            case InputDevice.NONE: return None
            case InputDevice.JOYPAD: return self.joypad
            case InputDevice.MOUSE: return self.mouse
            case InputDevice.KEYBOARD: return self.keyboard
            case InputDevice.LIGHTGUN: return self.light_gun
            case InputDevice.ANALOG: return self.analog
            case InputDevice.POINTER: return self.pointer
            case int(): raise IndexError(f"Index {item} is not a valid InputDevice")
            case _: raise TypeError(f"Expected an int or InputDevice, got {item!r}")


InputPollResult = PortState | DeviceState | Point | Pointer | bool | int | None
InputStateIterator = Iterator[InputPollResult | Sequence[InputPollResult]]
InputStateGenerator = Callable[[], InputStateIterator]


@final
class GeneratorInputState(InputState):
    def __init__(
            self,
            generator: InputStateGenerator | None = None,
            device_capabilities: InputDeviceFlag = InputDeviceFlag.ALL,
            bitmasks_supported: bool = True,
    ):
        self._generator = generator
        self._generator_state: Iterator[InputPollResult | Sequence[InputPollResult]] | None = None
        self._last_poll_result: InputPollResult = None
        self._device_capabilities = device_capabilities
        self._bitmasks_supported = bitmasks_supported

    @property
    def device_capabilities(self) -> InputDeviceFlag:
        return self._device_capabilities

    @device_capabilities.setter
    def device_capabilities(self, value: InputDeviceFlag) -> None:
        # Unrecognized devices will be filtered out by the CONFORM boundary on InputDeviceFlag
        self._device_capabilities = InputDeviceFlag(value)

    @property
    def bitmasks_supported(self) -> bool:
        return self._bitmasks_supported

    @bitmasks_supported.setter
    def bitmasks_supported(self, value: bool) -> None:
        self._bitmasks_supported = bool(value)

    def poll(self) -> None:
        if self._generator:
            if self._generator_state is None:
                self._generator_state = self._generator()

            self._last_poll_result = next(self._generator_state, None)

    def state(self, port: int, device: int, index: int, id: int) -> int:
        match (self._generator, self._last_poll_result, port, InputDevice(device)):
            case(None, _, _, _) | (_, [], _, _):
                # An unassigned generator or an empty result list will default to 0
                return 0
            case _, _, _, device if not (self.device_capabilities & device.flag):
                # Unavailable devices will always return 0
                # (Non-existent ports are enforced at the environment layer, not here)
                return 0
            case _, [*results], port, device if port < len(results) and not is_dataclass(results):
                # Yielding a sequence of result types
                # will expose it to the port that corresponds to each index,
                # with unfilled ports defaulting to 0.
                results: Sequence[InputPollResult]
                return self._lookup_port_state(results[port], device, index, id)
            case _, result, _, device if isinstance(result, InputPollResult):
                # Yielding a type that's _not_ a sequence
                # will expose it to all ports.
                return self._lookup_port_state(result, device, index, id)
            case _:
                return 0

    def _lookup_port_state(self, result: InputPollResult, device: InputDevice, index: int, id: int) -> int:
        match (result, device, index, id):
            # Yielding a PortState will set zero or more input devices for a port
            # (e.g. you can expose a joypad and a mouse to a single port).
            # All set devices will be exposed to the core as if the generator had yielded them alone.
            # All unset devices will be exposed to the core as 0.
            case PortState() as port_state, device, index, id:
                port_state: PortState
                # Recurse a little bit from the general port state into the specific device
                return self._lookup_port_state(port_state[device], device, index, id)

            # Yielding a JoypadState will expose it to the port's joypad device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case JoypadState() as joypad_state, InputDevice.JOYPAD, _, DeviceIdJoypad.MASK if self._bitmasks_supported:
                # When asking for the joypad's button mask,
                # return the mask as an integer
                joypad_state: JoypadState
                return joypad_state.mask
            case JoypadState() as joypad_state, InputDevice.JOYPAD, _, id if id in DeviceIdJoypad:
                # When asking for a specific joypad button,
                # return 1 (True) if its pressed and 0 (False) if not
                # NOTE: id in DeviceInJoypad is perfectly valid
                joypad_state: JoypadState
                return joypad_state[id]
            case JoypadState(), _, _, _:
                # When asking for something that joypads don't offer, return 0
                return 0

            # Yielding a DeviceIdJoypad value will expose it as a button press on the joypad device.
            # Unless the yielded value is DeviceIdJoypad.MASK, as there's no mask button;
            # so we return the flag value instead.
            case DeviceIdJoypad(DeviceIdJoypad.MASK), _, _, _:
                return 0
            # Yield a button mask with just the one button set
            case DeviceIdJoypad(device_id), InputDevice.JOYPAD, _, DeviceIdJoypad.MASK if self._bitmasks_supported:
                return 1 << device_id
            # Yield 1 for the pressed button
            case DeviceIdJoypad(device_id), InputDevice.JOYPAD, _, id if device_id == id:
                return 1
            case DeviceIdJoypad(_), _, _, _:
                return 0

            case AnalogState() as analog_state, InputDevice.ANALOG, _, id:
                analog_state: AnalogState
                return 0 # TODO: Implement

            # Yielding a MouseState will expose it to the port's mouse device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case MouseState() as mouse_state, InputDevice.MOUSE, _, id if id in DeviceIdMouse:
                # When asking for a specific mouse button,
                # return 1 (True) if its pressed and 0 (False) if not
                mouse_state: MouseState
                return mouse_state[id]
            case MouseState(), _, _, _:
                # When asking for something that mice don't offer, return 0
                return 0

            # Yielding a DeviceIdMouse value will expose it as a button press on the mouse device,
            # with all other devices defaulting to 0.
            # Yielding DeviceIdMouse.X or DeviceIdMouse.Y will return 0.
            case DeviceIdMouse(device_id), InputDevice.MOUSE, _, id if device_id == id and id not in (DeviceIdMouse.X, DeviceIdMouse.Y):
                return 1
            case DeviceIdMouse(_), _, _, _:
                return 0

            # Yielding a KeyboardState will expose it to the port's keyboard device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case KeyboardState() as keyboard_state, InputDevice.KEYBOARD, _, id if id in Key:
                # KeyboardState overloads __getitem__ to return True for pressed keys
                # and False for unpressed or invalid keys.
                return keyboard_state[id]
            case KeyboardState(), _, _, _:
                # When asking for something that keyboards don't offer, return 0
                return 0

            # Yielding a Key value will expose it as a key press on the keyboard device.
            case Key(key), InputDevice.KEYBOARD, _, id if key == id and id in Key:
                return 1
            case Key(_), _, _, _:  # When yielding a Key in all other cases, return 0
                return 0

            # Yielding a LightGunState will expose it to the port's light gun device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case LightGunState() as light_gun_state, InputDevice.LIGHTGUN, _, id if id in DeviceIdLightgun:
                light_gun_state: LightGunState
                return light_gun_state[id]
            case LightGunState(), _, _, _:
                # When asking for something that light guns don't offer, return 0
                return 0

            case DeviceIdLightgun(device_id), InputDevice.LIGHTGUN, _, id if device_id == id and device_id.is_button:
                return 1

            # Yielding a PointerState will expose it to the port's abstract pointer device.
            case PointerState() as pointer_state, InputDevice.POINTER, _, DeviceIdPointer.COUNT:
                # The number of touches will be exposed as RETRO_DEVICE_ID_POINTER_COUNT.
                # Index is ignored.
                pointer_state: PointerState
                return len(pointer_state.pointers)
            case PointerState() as pointer_state, InputDevice.POINTER, index, DeviceIdPointer.X \
                    if 0 <= index < len(pointer_state.pointers):
                return pointer_state.pointers[index].x
            case PointerState() as pointer_state, InputDevice.POINTER, index, DeviceIdPointer.Y \
                    if 0 <= index < len(pointer_state.pointers):
                return pointer_state.pointers[index].y
            case PointerState() as pointer_state, InputDevice.POINTER, index, DeviceIdPointer.PRESSED \
                    if 0 <= index < len(pointer_state.pointers):
                return pointer_state.pointers[index].pressed
            case PointerState(), _, _, _:
                return 0

            case Pointer(x=x, y=_, pressed=_), InputDevice.POINTER, 0, DeviceIdPointer.X:
                return x
            case Pointer(x=_, y=y, pressed=_), InputDevice.POINTER, 0, DeviceIdPointer.Y:
                return y
            case Pointer(x=_, y=_, pressed=pressed), InputDevice.POINTER, 0, DeviceIdPointer.PRESSED:
                return pressed
            case Pointer(), InputDevice.POINTER, 0, DeviceIdPointer.COUNT:
                return 1
            case Pointer(), _, _, _:
                return 0

            case _, InputDevice.NONE, _, _:
                return 0

            case Point(x=x, y=_), InputDevice.POINTER, 0, DeviceIdPointer.X:
                return x
            case Point(x=_, y=y), InputDevice.POINTER, 0, DeviceIdPointer.Y:
                return y
            case Point(x=_, y=_), InputDevice.POINTER, 0, DeviceIdPointer.COUNT:
                return 1
            case Point(), _, _, _:
                return 0

            # Yielding a specific number will unconditionally return it
            # to all devices, indexes, and IDs
            case bool(b), _, _, _:
                return int(b)
            case int(v), _, _, _:
                return v

            # Yielding None will unconditionally return 0 for all devices, indexes, and IDs.
            case None, _, _, _:
                return 0

            case _, _, _, _:
                raise ValueError(f"Invalid input state: {result}")
