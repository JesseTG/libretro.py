from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, overload

from libretro._typing import override
from libretro.api.input import (
    AnalogState,
    DeviceIdAnalog,
    DeviceIdJoypad,
    DeviceIdLightgun,
    DeviceIdMouse,
    DeviceIdPointer,
    DeviceIndexAnalog,
    InputDevice,
    InputDeviceFlag,
    InputDeviceState,
    JoypadState,
    Key,
    KeyboardState,
    LightGunState,
    MouseState,
    Pointer,
    PointerState,
    retro_controller_description,
    retro_input_descriptor,
    retro_keyboard_callback,
)

from .driver import InputDriver


@dataclass(frozen=True, order=True, slots=True)
class Point:
    x: int = 0
    y: int = 0


DeviceState = JoypadState | MouseState | KeyboardState | LightGunState | AnalogState | PointerState


class Direction(Enum):
    RIGHT = auto()
    UP = auto()
    LEFT = auto()
    DOWN = auto()

    def matches_direction(self, other: DeviceIdJoypad | Key | DeviceIdLightgun) -> bool:
        match (self, other):
            case (
                Direction.RIGHT,
                DeviceIdJoypad.RIGHT | Key.RIGHT | DeviceIdLightgun.DPAD_RIGHT,
            ):
                return True
            case (Direction.UP, DeviceIdJoypad.UP | Key.UP | DeviceIdLightgun.DPAD_UP):
                return True
            case (
                Direction.LEFT,
                DeviceIdJoypad.LEFT | Key.LEFT | DeviceIdLightgun.DPAD_LEFT,
            ):
                return True
            case (
                Direction.DOWN,
                DeviceIdJoypad.DOWN | Key.DOWN | DeviceIdLightgun.DPAD_DOWN,
            ):
                return True
            case _:
                return False


@dataclass(frozen=True, slots=True)
class PortState:
    joypad: JoypadState | None = None
    mouse: MouseState | None = None
    keyboard: KeyboardState | None = None
    light_gun: LightGunState | None = None
    analog: AnalogState | None = None
    pointer: PointerState | None = None

    @overload
    def __getitem__(self, item: Literal[InputDevice.NONE]) -> None: ...

    @overload
    def __getitem__(self, item: Literal[InputDevice.JOYPAD]) -> JoypadState | None: ...
    @overload
    def __getitem__(self, item: Literal[InputDevice.MOUSE]) -> MouseState | None: ...
    @overload
    def __getitem__(self, item: Literal[InputDevice.KEYBOARD]) -> KeyboardState | None: ...
    @overload
    def __getitem__(self, item: Literal[InputDevice.LIGHTGUN]) -> LightGunState | None: ...
    @overload
    def __getitem__(self, item: Literal[InputDevice.ANALOG]) -> AnalogState | None: ...
    @overload
    def __getitem__(self, item: Literal[InputDevice.POINTER]) -> PointerState | None: ...

    def __getitem__(self, item: InputDevice | int) -> DeviceState | None:
        match item:
            case InputDevice.NONE:
                return None
            case InputDevice.JOYPAD:
                return self.joypad
            case InputDevice.MOUSE:
                return self.mouse
            case InputDevice.KEYBOARD:
                return self.keyboard
            case InputDevice.LIGHTGUN:
                return self.light_gun
            case InputDevice.ANALOG:
                return self.analog
            case InputDevice.POINTER:
                return self.pointer
            case int():
                raise IndexError(f"Index {item} is not a valid InputDevice")
            case _:
                raise TypeError(f"Expected an int or InputDevice, got {item!r}")


InputPollResult = PortState | DeviceState | Point | Pointer | bool | int | None
InputStateIterator = Iterator[InputPollResult | Sequence[InputPollResult]]
InputStateIterable = Iterable[InputPollResult | Sequence[InputPollResult]]
InputStateGenerator = Callable[[], InputStateIterator]
InputStateSource = InputStateGenerator | InputStateIterable | InputStateIterator


class IterableInputDriver(InputDriver):
    _input_generator: InputStateSource | None
    _input_generator_state: InputStateIterator | None
    _input_poll_result: InputPollResult | Sequence[InputPollResult] | None
    _input_descriptors: Sequence[retro_input_descriptor] | None
    _controller_info: Sequence[retro_controller_description] | None
    _device_capabilities: InputDeviceFlag | None
    _bitmasks_supported: bool | None
    _max_users: int | None
    _keyboard_callback: retro_keyboard_callback | None

    def __init__(
        self,
        input_generator: InputStateSource | None = None,
        device_capabilities: InputDeviceFlag | None = InputDeviceFlag.ALL,
        bitmasks_supported: bool | None = True,
        max_users: int | None = 8,
    ):
        self._input_generator = input_generator
        self._input_generator_state = None
        self._input_poll_result = None

        self._input_descriptors = None
        self._controller_info = None
        self._device_capabilities = device_capabilities
        self._bitmasks_supported = bitmasks_supported
        self._max_users = max_users
        self._keyboard_callback = None

    @property
    @override
    def device_capabilities(self) -> InputDeviceFlag | None:
        return self._device_capabilities

    @device_capabilities.setter
    @override
    def device_capabilities(self, capabilities: InputDeviceFlag) -> None:
        if not isinstance(capabilities, InputDeviceFlag):
            raise TypeError(f"Expected an InputDeviceFlag, got {type(capabilities).__name__}")

        # Unrecognized devices will be filtered out by the CONFORM boundary on InputDeviceFlag
        self._device_capabilities = InputDeviceFlag(capabilities)

    @device_capabilities.deleter
    @override
    def device_capabilities(self) -> None:
        self._device_capabilities = None

    @property
    @override
    def bitmasks_supported(self) -> bool | None:
        return self._bitmasks_supported

    @bitmasks_supported.setter
    @override
    def bitmasks_supported(self, bitmask_supported: bool) -> None:
        self._bitmasks_supported = bool(bitmask_supported)

    @bitmasks_supported.deleter
    @override
    def bitmasks_supported(self) -> None:
        self._bitmasks_supported = None

    @property
    @override
    def max_users(self) -> int | None:
        return self._max_users

    @max_users.setter
    @override
    def max_users(self, max_users: int | None) -> None:
        match max_users:
            case int(i) if i >= 0:
                self._max_users = int(i)
            case int(i):
                raise ValueError(f"Expected None or a non-negative int, got {i}")
            case None:
                self._max_users = None
            case _:
                raise TypeError(f"Expected None or a non-negative int, got {max_users!r}")

    @max_users.deleter
    @override
    def max_users(self) -> None:
        self._max_users = None

    @override
    def poll(self) -> None:
        # TODO: handle cases where the core calls this method multiple times in a frame
        if self._input_generator:
            if self._input_generator_state is None:
                match self._input_generator:
                    case Callable() as func:
                        self._input_generator_state = func()
                    case Iterator() as it:
                        self._input_generator_state = it
                    case Iterable() as it:
                        self._input_generator_state = iter(it)

            self._input_poll_result = next(self._input_generator_state, None)

            # TODO: Send keyboard callback events

    @override
    def state(self, port: int, device: int, index: int, id: int) -> int:
        if not self._input_generator:
            # If there's no input generator, all states will default to 0
            return 0

        match self._input_poll_result, port, InputDevice(device):
            case ([], _, _):
                # An empty result list will default to 0 (no input)
                return 0
            case (_, port, _) if self._max_users is not None and not (0 <= port < self._max_users):
                # If we limit the number of ports, any out-of-bounds port will default to 0
                return 0
            case _, _, device if (
                self._device_capabilities is not None
                and device.flag not in self._device_capabilities
            ):
                # If we filter by devices, any device not in the flag will default to 0
                return 0
            case [*results], port, device if 0 <= port < len(results) and not isinstance(
                results, InputDeviceState
            ):
                # Yielding a sequence of result types
                # will expose it to the port that corresponds to each index,
                # with unfilled ports defaulting to 0.
                return self._lookup_port_state(results[port], device, index, id)
            case result, _, device if isinstance(result, InputPollResult):
                # Yielding a type that's _not_ a sequence
                # will expose it to all ports.
                return self._lookup_port_state(result, device, index, id)
            case _, _, _:
                return 0

    def _lookup_port_state(
        self, result: InputPollResult, device: InputDevice, index: int, id: int
    ) -> int:
        match (result, device, index, id):
            # Yielding a PortState will set zero or more input devices for a port
            # (e.g. you can expose a joypad and a mouse to a single port).
            # All set devices will be exposed to the core as if the generator had yielded them alone.
            # All unset devices will be exposed to the core as 0.
            case PortState() as port_state, device, index, id:
                # Recurse a little bit from the general port state into the specific device
                return self._lookup_port_state(port_state[device], device, index, id)

            # Yielding a JoypadState will expose it to the port's joypad device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case (
                JoypadState() as joypad,
                InputDevice.JOYPAD,
                _,
                DeviceIdJoypad.MASK,
            ) if self._bitmasks_supported:
                # When asking for the joypad's button mask,
                # return the mask as an integer
                return joypad.mask
            case JoypadState() as joypad, InputDevice.JOYPAD, _, id if id in DeviceIdJoypad:
                # When asking for a specific joypad button,
                # return 1 (True) if its pressed and 0 (False) if not
                # NOTE: id in DeviceIdJoypad is perfectly valid
                return joypad[id]
            case JoypadState(), _, _, _:
                # When asking for something that joypads don't offer, return 0
                return 0
            case DeviceIdJoypad(DeviceIdJoypad.MASK), _, _, _:
                # Yielding a DeviceIdJoypad value will expose it as a button press on the joypad device.
                # Unless the yielded value is DeviceIdJoypad.MASK, as there's no "mask" button;
                # so we return the flag value instead.
                return 0
            case (
                DeviceIdJoypad(device_id),
                InputDevice.JOYPAD,
                _,
                DeviceIdJoypad.MASK,
            ) if self._bitmasks_supported:
                # Yield a button mask with just the one button set
                return 1 << device_id
            case (
                DeviceIdJoypad(device_id),
                InputDevice.JOYPAD,
                _,
                id,
            ) if (device_id == id):
                # Yield 1 for the pressed button
                return 1
            case DeviceIdJoypad(_), _, _, _:
                return 0

            # Yielding an AnalogState will expose it to the port's mouse device,
            # with all other devices defaulting to 0.
            case (
                AnalogState() as analog,
                InputDevice.ANALOG,
                DeviceIndexAnalog.BUTTON,
                id,
            ):
                return analog[id]
            case (
                AnalogState() as analog,
                InputDevice.ANALOG,
                DeviceIndexAnalog.LEFT,
                id,
            ) if (id in DeviceIdAnalog):
                return analog.lstick[id]
            case (
                AnalogState() as analog,
                InputDevice.ANALOG,
                DeviceIndexAnalog.RIGHT,
                id,
            ) if (id in DeviceIdAnalog):
                return analog.rstick[id]
            case AnalogState(), _, _, _:
                return 0

            # Yielding a MouseState will expose it to the port's mouse device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case MouseState() as mouse, InputDevice.MOUSE, _, id if id in DeviceIdMouse:
                # When asking for a specific mouse button,
                # return 1 (True) if its pressed and 0 (False) if not
                return mouse[id]
            case MouseState(), _, _, _:
                # When asking for something that mice don't offer, return 0
                return 0

            # Yielding a DeviceIdMouse value will expose it as a button press on the mouse device,
            # with all other devices defaulting to 0.
            # Yielding DeviceIdMouse.X or DeviceIdMouse.Y will return 0.
            case (
                DeviceIdMouse(device_id),
                InputDevice.MOUSE,
                _,
                id,
            ) if device_id == id and id not in (
                DeviceIdMouse.X,
                DeviceIdMouse.Y,
            ):
                return 1
            case DeviceIdMouse(_), _, _, _:
                return 0

            # Yielding a KeyboardState will expose it to the port's keyboard device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case KeyboardState() as keyboard, InputDevice.KEYBOARD, _, id if id in Key:
                # KeyboardState overloads __getitem__ to return True for pressed keys
                # and False for unpressed or invalid keys.
                return keyboard[id]
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
            case LightGunState() as lightgun, InputDevice.LIGHTGUN, _, id if (
                id in DeviceIdLightgun
            ):
                return lightgun[id]
            case LightGunState(), _, _, _:
                # When asking for something that light guns don't offer, return 0
                return 0

            case DeviceIdLightgun(device_id), InputDevice.LIGHTGUN, _, id if (
                device_id == id and device_id.is_button
            ):
                return 1

            # Yielding a PointerState will expose it to the port's abstract pointer device.
            case (
                PointerState() as pointer,
                InputDevice.POINTER,
                _,
                DeviceIdPointer.COUNT,
            ):
                # The number of touches will be exposed as RETRO_DEVICE_ID_POINTER_COUNT.
                # Index is ignored.
                return len(pointer.pointers)
            case (
                PointerState() as pointer,
                InputDevice.POINTER,
                index,
                DeviceIdPointer.X,
            ) if (0 <= index < len(pointer.pointers)):
                return pointer.pointers[index].x
            case (
                PointerState() as pointer,
                InputDevice.POINTER,
                index,
                DeviceIdPointer.Y,
            ) if (0 <= index < len(pointer.pointers)):
                return pointer.pointers[index].y
            case (
                PointerState() as pointer,
                InputDevice.POINTER,
                index,
                DeviceIdPointer.PRESSED,
            ) if (0 <= index < len(pointer.pointers)):
                return pointer.pointers[index].pressed
            case PointerState(), _, _, _:
                return 0

            case (
                Pointer(x=x),
                InputDevice.POINTER,
                0,
                DeviceIdPointer.X,
            ):
                return x
            case (
                Pointer(y=y),
                InputDevice.POINTER,
                0,
                DeviceIdPointer.Y,
            ):
                return y
            case (
                Pointer(pressed=pressed),
                InputDevice.POINTER,
                0,
                DeviceIdPointer.PRESSED,
            ):
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

    @property
    @override
    def descriptors(self) -> Sequence[retro_input_descriptor] | None:
        return self._input_descriptors

    @descriptors.setter
    @override
    def descriptors(self, descriptors: Sequence[retro_input_descriptor] | None) -> None:
        if descriptors is None:
            self._input_descriptors = None
        elif all(isinstance(descriptor, retro_input_descriptor) for descriptor in descriptors):
            self._input_descriptors = tuple(descriptors)
        else:
            raise TypeError(
                f"Expected None or a sequence of retro_input_descriptor, got {descriptors!r}"
            )

    @property
    @override
    def controller_info(self) -> Sequence[retro_controller_description] | None:
        return self._controller_info

    @controller_info.setter
    @override
    def controller_info(self, info: Sequence[retro_controller_description] | None) -> None:
        if info is None:
            self._controller_info = None
        elif all(
            isinstance(controller_info, retro_controller_description) for controller_info in info
        ):
            self._controller_info = tuple(info)
        else:
            raise TypeError(f"Expected None or a sequence of retro_controller_info, got {info!r}")

    @property
    @override
    def keyboard_callback(self) -> retro_keyboard_callback | None:
        return self._keyboard_callback

    @keyboard_callback.setter
    @override
    def keyboard_callback(self, callback: retro_keyboard_callback | None) -> None:
        if callback is not None and not isinstance(callback, retro_keyboard_callback):
            raise TypeError(f"Expected None or a retro_keyboard_callback, got {callback!r}")

        self._keyboard_callback = callback


__all__ = [
    "IterableInputDriver",
    "InputPollResult",
    "InputStateSource",
    "InputStateIterator",
    "InputStateGenerator",
    "InputStateIterable",
    "Point",
]
