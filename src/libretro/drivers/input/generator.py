from collections.abc import Callable, Generator, Iterable, Iterator, Sequence
from dataclasses import dataclass
from enum import Enum, auto

from libretro._typing import override
from libretro._utils import Pollable
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
    retro_controller_info,
    retro_input_descriptor,
    retro_keyboard_callback,
)
from libretro.drivers.rumble import RumbleInterface
from libretro.drivers.sensor import SensorInterface

from .driver import InputDriver

# Needed for Python 3.11 compatibility,
# as "int() in MyIntEnumSubclass" wasn't available until Python 3.12
_DEVICEID_ANALOG_MEMBERS = DeviceIdAnalog.__members__.values()
_DEVICEID_JOYPAD_MEMBERS = DeviceIdJoypad.__members__.values()
_DEVICEID_LIGHTGUN_MEMBERS = DeviceIdLightgun.__members__.values()
_DEVICEID_MOUSE_MEMBERS = DeviceIdMouse.__members__.values()
_KEY_MEMBERS = Key.__members__.values()


@dataclass(order=True, slots=True)
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

    def __getitem__(self, item) -> DeviceState | None:
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


class GeneratorInputDriver(InputDriver):
    def __init__(
        self,
        input_generator: InputStateSource | None = None,
        device_capabilities: InputDeviceFlag | None = InputDeviceFlag.ALL,
        bitmasks_supported: bool | None = True,
        max_users: int | None = 8,
        rumble: RumbleInterface | None = None,
        sensor: SensorInterface | None = None,
    ):
        self._input_generator = input_generator
        self._input_generator_state: (
            Iterator[InputPollResult | Sequence[InputPollResult]] | None
        ) = None
        self._input_poll_result: InputPollResult = None
        self._last_input_poll_result: InputPollResult = None

        self._input_descriptors: Sequence[retro_input_descriptor] | None = None
        self._controller_info: Sequence[retro_controller_info] | None = None
        self._device_capabilities = device_capabilities
        self._bitmasks_supported = bitmasks_supported
        self._max_users = max_users
        self._keyboard_callback: retro_keyboard_callback | None = None

        self._rumble = rumble
        self._sensor = sensor

    @property
    @override
    def device_capabilities(self) -> InputDeviceFlag | None:
        return self._device_capabilities

    @device_capabilities.setter
    @override
    def device_capabilities(self, value: InputDeviceFlag) -> None:
        if not isinstance(value, InputDeviceFlag):
            raise TypeError(f"Expected an InputDeviceFlag, got {type(value).__name__}")

        # Unrecognized devices will be filtered out by the CONFORM boundary on InputDeviceFlag
        self._device_capabilities = InputDeviceFlag(value)

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
    def bitmasks_supported(self, value: bool) -> None:
        self._bitmasks_supported = bool(value)

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

    def poll(self) -> None:
        if self._input_generator:
            if self._input_generator_state is None:
                match self._input_generator:
                    case Callable() as func:
                        self._input_generator_state = func()
                    case Iterable() | Iterator() | Generator() as it:
                        self._input_generator_state = it

            self._last_input_poll_result = self._input_poll_result
            self._input_poll_result = next(self._input_generator_state, None)

            # TODO: Send keyboard callback events

        if isinstance(self._sensor, Pollable):
            self._sensor.poll()

        if isinstance(self._rumble, Pollable):
            self._rumble.poll()

    def state(self, port: int, device: int, index: int, id: int) -> int:
        match (
            self._input_generator,
            self._input_poll_result,
            port,
            InputDevice(device),
        ):
            case (None, _, _, _) | (_, [], _, _):
                # An unassigned generator or an empty result list will default to 0
                return 0
            case (_, _, port, _) if self._max_users is not None and not (
                0 <= port < self._max_users
            ):
                # If we limit the number of ports, any out-of-bounds port will default to 0
                return 0
            case _, _, _, device if (
                self._device_capabilities is not None
                and device.flag not in self._device_capabilities
            ):
                # If we filter by devices, any device not in the flag will default to 0
                return 0
            case _, [*results], port, device if 0 <= port < len(results) and not isinstance(
                results, InputDeviceState
            ):
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

    def _lookup_port_state(
        self, result: InputPollResult, device: InputDevice, index: int, id: int
    ) -> int:
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
            case (
                JoypadState() as joypad_state,
                InputDevice.JOYPAD,
                _,
                DeviceIdJoypad.MASK,
            ) if self._bitmasks_supported:
                # When asking for the joypad's button mask,
                # return the mask as an integer
                joypad_state: JoypadState
                return joypad_state.mask
            case (
                JoypadState() as joypad_state,
                InputDevice.JOYPAD,
                _,
                id,
            ) if id in _DEVICEID_JOYPAD_MEMBERS:
                # When asking for a specific joypad button,
                # return 1 (True) if its pressed and 0 (False) if not
                # NOTE: id in DeviceInJoypad is perfectly valid
                joypad_state: JoypadState
                return joypad_state[id]
            case JoypadState(), _, _, _:
                # When asking for something that joypads don't offer, return 0
                return 0
            case DeviceIdJoypad(DeviceIdJoypad.MASK), _, _, _:
                # Yielding a DeviceIdJoypad value will expose it as a button press on the joypad device.
                # Unless the yielded value is DeviceIdJoypad.MASK, as there's no mask button;
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
            ) if device_id == id:
                # Yield 1 for the pressed button
                return 1
            case DeviceIdJoypad(_), _, _, _:
                return 0

            # Yielding an AnalogState will expose it to the port's mouse device,
            # with all other devices defaulting to 0.
            case (
                AnalogState() as analog_state,
                InputDevice.ANALOG,
                DeviceIndexAnalog.BUTTON,
                id,
            ):
                analog_state: AnalogState
                return analog_state[id]
            case (
                AnalogState() as analog_state,
                InputDevice.ANALOG,
                DeviceIndexAnalog.LEFT,
                id,
            ) if id in _DEVICEID_ANALOG_MEMBERS:
                analog_state: AnalogState
                return analog_state.lstick[id]
            case (
                AnalogState() as analog_state,
                InputDevice.ANALOG,
                DeviceIndexAnalog.RIGHT,
                id,
            ) if id in _DEVICEID_ANALOG_MEMBERS:
                analog_state: AnalogState
                return analog_state.rstick[id]
            case AnalogState(), _, _, _:
                return 0

            # Yielding a MouseState will expose it to the port's mouse device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case (
                MouseState() as mouse_state,
                InputDevice.MOUSE,
                _,
                id,
            ) if id in _DEVICEID_MOUSE_MEMBERS:
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
            case (
                KeyboardState() as keyboard_state,
                InputDevice.KEYBOARD,
                _,
                id,
            ) if id in _KEY_MEMBERS:
                # KeyboardState overloads __getitem__ to return True for pressed keys
                # and False for unpressed or invalid keys.
                return keyboard_state[id]
            case KeyboardState(), _, _, _:
                # When asking for something that keyboards don't offer, return 0
                return 0

            # Yielding a Key value will expose it as a key press on the keyboard device.
            case Key(key), InputDevice.KEYBOARD, _, id if key == id and id in _KEY_MEMBERS:
                return 1
            case Key(_), _, _, _:  # When yielding a Key in all other cases, return 0
                return 0

            # Yielding a LightGunState will expose it to the port's light gun device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case LightGunState() as light_gun_state, InputDevice.LIGHTGUN, _, id if (
                id in _DEVICEID_LIGHTGUN_MEMBERS
            ):
                light_gun_state: LightGunState
                return light_gun_state[id]
            case LightGunState(), _, _, _:
                # When asking for something that light guns don't offer, return 0
                return 0

            case DeviceIdLightgun(device_id), InputDevice.LIGHTGUN, _, id if (
                device_id == id and device_id.is_button
            ):
                return 1

            # Yielding a PointerState will expose it to the port's abstract pointer device.
            case (
                PointerState() as pointer_state,
                InputDevice.POINTER,
                _,
                DeviceIdPointer.COUNT,
            ):
                # The number of touches will be exposed as RETRO_DEVICE_ID_POINTER_COUNT.
                # Index is ignored.
                pointer_state: PointerState
                return len(pointer_state.pointers)
            case (
                PointerState() as pointer_state,
                InputDevice.POINTER,
                index,
                DeviceIdPointer.X,
            ) if (0 <= index < len(pointer_state.pointers)):
                return pointer_state.pointers[index].x
            case (
                PointerState() as pointer_state,
                InputDevice.POINTER,
                index,
                DeviceIdPointer.Y,
            ) if (0 <= index < len(pointer_state.pointers)):
                return pointer_state.pointers[index].y
            case (
                PointerState() as pointer_state,
                InputDevice.POINTER,
                index,
                DeviceIdPointer.PRESSED,
            ) if (0 <= index < len(pointer_state.pointers)):
                return pointer_state.pointers[index].pressed
            case PointerState(), _, _, _:
                return 0

            case (
                Pointer(x=x, y=_, pressed=_),
                InputDevice.POINTER,
                0,
                DeviceIdPointer.X,
            ):
                return x
            case (
                Pointer(x=_, y=y, pressed=_),
                InputDevice.POINTER,
                0,
                DeviceIdPointer.Y,
            ):
                return y
            case (
                Pointer(x=_, y=_, pressed=pressed),
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

    @property
    def rumble(self) -> RumbleInterface | None:
        return self._rumble

    @rumble.setter
    def rumble(self, value: RumbleInterface | None) -> None:
        if value is not None and not isinstance(value, RumbleInterface):
            raise TypeError(f"Expected None or a RumbleInterface, got {value!r}")

        self._rumble = value

    @rumble.deleter
    def rumble(self) -> None:
        self._rumble = None

    @property
    def sensor(self) -> SensorInterface | None:
        return self._sensor

    @sensor.setter
    def sensor(self, value: SensorInterface | None) -> None:
        if value is not None and not isinstance(value, SensorInterface):
            raise TypeError(f"Expected None or a SensorInterface, got {value!r}")

        self._sensor = value

    @sensor.deleter
    def sensor(self) -> None:
        self._sensor = None


__all__ = [
    "GeneratorInputDriver",
    "InputPollResult",
    "InputStateSource",
    "InputStateIterator",
    "InputStateGenerator",
    "InputStateIterable",
    "Point",
]
