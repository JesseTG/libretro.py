from dataclasses import dataclass
import enum
from abc import abstractmethod
from collections.abc import Iterator, Callable
from ctypes import c_int16, c_uint
from typing import Protocol, NamedTuple, runtime_checkable, final, Sequence, Self

from ..retro import *


@runtime_checkable
class InputCallbacks(Protocol):
    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def state(self, port: int, device: InputDevice, index: int, id: int) -> int: ...


@runtime_checkable
class InputState(InputCallbacks, Protocol):
    @property
    @abstractmethod
    def device_capabilities(self) -> InputDeviceFlag: ...

    @property
    @abstractmethod
    def bitmasks(self) -> bool: ...

    @property
    @abstractmethod
    def max_users(self) -> int: ...


@dataclass
class JoypadState(NamedTuple):
    b: bool = False
    y: bool = False
    select: bool = False
    start: bool = False
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    a: bool = False
    x: bool = False
    l: bool = False
    r: bool = False
    l2: bool = False
    r2: bool = False
    l3: bool = False
    r3: bool = False

    @property
    def mask(self) -> int:
        return (self.b << 0) \
            | (self.y << 1) \
            | (self.select << 2) \
            | (self.start << 3) \
            | (self.up << 4) \
            | (self.down << 5) \
            | (self.left << 6) \
            | (self.right << 7) \
            | (self.a << 8) \
            | (self.x << 9) \
            | (self.l << 10) \
            | (self.r << 11) \
            | (self.l2 << 12) \
            | (self.r2 << 13) \
            | (self.l3 << 14) \
            | (self.r3 << 15)


@dataclass(frozen=True)
class MouseState(NamedTuple):
    x: int = 0
    y: int = 0
    left: bool = False
    right: bool = False
    wheel_up: bool = False
    wheel_down: bool = False
    middle: bool = False
    horizontal_wheel_up: bool = False
    horizontal_wheel_down: bool = False
    button4: bool = False
    button5: bool = False


@dataclass(frozen=True)
class KeyboardState:
    backspace: bool = False
    tab: bool = False
    clear: bool = False
    return_: bool = False
    pause: bool = False
    escape: bool = False
    space: bool = False
    exclaim: bool = False
    quotedbl: bool = False
    hash: bool = False
    dollar: bool = False
    ampersand: bool = False
    quote: bool = False
    leftparen: bool = False
    rightparen: bool = False
    asterisk: bool = False
    plus: bool = False
    comma: bool = False
    minus: bool = False
    period: bool = False
    slash: bool = False
    zero: bool = False
    one: bool = False
    two: bool = False
    three: bool = False
    four: bool = False
    five: bool = False
    six: bool = False
    seven: bool = False
    eight: bool = False
    nine: bool = False
    colon: bool = False
    semicolon: bool = False
    less: bool = False
    equals: bool = False
    greater: bool = False
    question: bool = False
    at: bool = False
    leftbracket: bool = False
    backslash: bool = False
    rightbracket: bool = False
    caret: bool = False
    underscore: bool = False
    backquote: bool = False
    a: bool = False
    b: bool = False
    c: bool = False
    d: bool = False
    e: bool = False
    f: bool = False
    g: bool = False
    h: bool = False
    i: bool = False
    j: bool = False
    k: bool = False
    l: bool = False
    m: bool = False
    n: bool = False
    o: bool = False
    p: bool = False
    q: bool = False
    r: bool = False
    s: bool = False
    t: bool = False
    u: bool = False
    v: bool = False
    w: bool = False
    x: bool = False
    y: bool = False
    z: bool = False
    leftbrace: bool = False
    bar: bool = False
    rightbrace: bool = False
    tilde: bool = False
    delete: bool = False

    kp0: bool = False
    kp1: bool = False
    kp2: bool = False
    kp3: bool = False
    kp4: bool = False
    kp5: bool = False
    kp6: bool = False
    kp7: bool = False
    kp8: bool = False
    kp9: bool = False
    kp_period: bool = False
    kp_divide: bool = False
    kp_multiply: bool = False
    kp_minus: bool = False
    kp_plus: bool = False
    kp_enter: bool = False
    kp_equals: bool = False

    up: bool = False
    down: bool = False
    right: bool = False
    left: bool = False
    insert: bool = False
    home: bool = False
    end: bool = False
    pageup: bool = False
    pagedown: bool = False

    f1: bool = False
    f2: bool = False
    f3: bool = False
    f4: bool = False
    f5: bool = False
    f6: bool = False
    f7: bool = False
    f8: bool = False
    f9: bool = False
    f10: bool = False
    f11: bool = False
    f12: bool = False
    f13: bool = False
    f14: bool = False
    f15: bool = False

    numlock: bool = False
    capslock: bool = False
    scrolllock: bool = False
    rshift: bool = False
    lshift: bool = False
    rctrl: bool = False
    lctrl: bool = False
    ralt: bool = False
    lalt: bool = False
    rmeta: bool = False
    lmeta: bool = False
    lsuper: bool = False
    rsuper: bool = False
    mode: bool = False
    compose: bool = False

    help: bool = False
    print: bool = False
    sysreq: bool = False
    break_: bool = False
    menu: bool = False
    power: bool = False
    euro: bool = False
    oem_102: bool = False

    def __getitem__(self, item: int) -> bool:
        if Key.is_valid(item):
            return getattr(self, Key(item).name.lower())
        else:
            return False


@dataclass(frozen=True)
class LightGunState(NamedTuple):
    screen_x: int = 0
    screen_y: int = 0
    is_offscreen: bool = False
    trigger: bool = False
    reload: bool = False
    aux_a: bool = False
    aux_b: bool = False
    start: bool = False
    select: bool = False
    aux_c: bool = False
    dpad_up: bool = False
    dpad_down: bool = False
    dpad_left: bool = False
    dpad_right: bool = False
    x: int = 0
    y: int = 0

    @property
    def cursor(self) -> bool:
        return self.aux_a

    @property
    def turbo(self) -> bool:
        return self.aux_b

    @property
    def pause(self) -> bool:
        return self.start


class AnalogState(NamedTuple):
    b: int = 0
    y: int = 0
    select: int = 0
    start: int = 0
    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0
    a: int = 0
    x: int = 0
    l: int = 0
    r: int = 0
    l2: int = 0
    r2: int = 0
    l3: int = 0
    r3: int = 0

    left_x: int = 0
    left_y: int = 0
    right_x: int = 0
    right_y: int = 0

@dataclass(frozen=True)
class Point(NamedTuple):
    x: int = 0
    y: int = 0


@dataclass(frozen=True)
class Pointer(NamedTuple):
    x: int = 0
    y: int = 0
    pressed: bool = False


class Direction(enum.IntEnum):
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


@dataclass(frozen=True)
class PointerState(NamedTuple):
    pointers: Sequence[Pointer] = ()


DeviceState = JoypadState | MouseState | KeyboardState | LightGunState | AnalogState | PointerState


@dataclass(frozen=True)
class PortState(NamedTuple):
    joypad: JoypadState | None = None
    mouse: MouseState | None = None
    keyboard: KeyboardState | None = None
    light_gun: LightGunState | None = None
    analog: AnalogState | None = None
    pointer: PointerState | None = None


InputPollResult = PortState | DeviceState | Point | bool | int | None
InputStateIterator = Iterator[InputPollResult | Sequence[InputPollResult]]
InputStateGenerator = Callable[[], InputStateIterator]


@final
class GeneratorInputState(InputState):
    def __init__(self, generator: InputStateGenerator | InputStateIterator | None = None):
        self._generator = generator
        self._generator_state: Iterator[InputPollResult | Sequence[InputPollResult]] | None = None
        self._last_poll_result: InputPollResult = None

    def device_capabilities(self) -> InputDeviceFlag:
        pass  # TODO: Implement

    def bitmasks(self) -> bool:
        pass  # TODO: Implement

    def max_users(self) -> int:
        pass  # TODO: Implement

    def poll(self) -> None:
        if self._generator:
            if self._generator_state is None:
                self._generator_state = self._generator()

            self._last_poll_result = next(self._generator_state, None)

    def state(self, port: int, device: InputDevice, index: int, id: int) -> int:
        match self._last_poll_result:
            case []:
                # Yielding an empty sequence will expose 0 to all ports, devices, indexes, and IDs.
                return 0
            case [*results]:
                # Yielding a sequence of result types
                # will expose it to the port that corresponds to each index,
                # with unfilled ports defaulting to 0.
                results: Sequence[InputPollResult]
                return self._lookup_port_state(results[port], device, index, id)
            case result if isinstance(result, InputPollResult):
                # Yielding a type that's _not_ a sequence
                # will expose it to all ports.
                return self._lookup_port_state(result, device, index, id)

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
            case JoypadState() as joypad_state, InputDevice.JOYPAD, _, DeviceIdJoypad.MASK:
                # When asking for the joypad's button mask,
                # return the mask as an integer
                joypad_state: JoypadState
                return joypad_state.mask
            case JoypadState() as joypad_state, InputDevice.JOYPAD, _, id if 0 <= id < len(joypad_state):
                # When asking for a specific joypad button,
                # return 1 (True) if its pressed and 0 (False) if not
                joypad_state: JoypadState
                return joypad_state[id]
            case JoypadState(), _, _, _:
                # When asking for something that joypads don't offer, return 0
                return 0

            # Yielding a DeviceIdJoypad value will expose it as a button press on the joypad device.
            case DeviceIdJoypad(device_id), InputDevice.JOYPAD, _, id if device_id == id and id != DeviceIdJoypad.MASK:
                return 1
            case DeviceIdJoypad(_), _, _, _:
                return 0

            case AnalogState() as analog_state, InputDevice.ANALOG, _, id:
                analog_state: AnalogState
                return 0

            # Yielding a MouseState will expose it to the port's mouse device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case MouseState() as mouse_state, InputDevice.MOUSE, _, id if 0 <= id < len(mouse_state):
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
            case KeyboardState() as keyboard_state, InputDevice.KEYBOARD, _, id if Key.is_valid(id):
                # KeyboardState overloads __getitem__ to return True for pressed keys
                # and False for unpressed or invalid keys.
                return keyboard_state[id]
            case KeyboardState(), _, _, _:
                # When asking for something that keyboards don't offer, return 0
                return 0

            # Yielding a Key value will expose it as a key press on the keyboard device.
            case Key(key), InputDevice.KEYBOARD, _, id if key == id and Key.is_valid(id):
                return 1
            case Key(_), _, _, _:  # When yielding a Key in all other cases, return 0
                return 0

            # Yielding a LightGunState will expose it to the port's light gun device,
            # with all other devices defaulting to 0.
            # Index is ignored.
            case LightGunState() as light_gun_state, InputDevice.LIGHTGUN, _, id if 0 <= id < len(light_gun_state):
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
            case PointerState() as pointer_state, InputDevice.POINTER, index, id \
                    if 0 <= index < len(pointer_state.pointers) and 0 <= id < len(pointer_state.pointers[index]):
                # The state of a specific touch will be exposed as RETRO_DEVICE_ID_POINTER_PRESSED on that index.
                # Unused or invalid touches will return 0 (False).
                # id=0 is X, id=1 is Y, id=2 is PRESSED
                return pointer_state.pointers[index][id]
            case PointerState(), _, _, _:
                return 0

            case _, InputDevice.NONE, _, _:
                return 0

            # Yielding a specific number will unconditionally return it
            # to all devices, indexes, and IDs
            case int() | bool() as value:
                return int(value)
            # Yielding None will unconditionally return 0 for all devices, indexes, and IDs.
            case None:
                return 0

            case _:
                raise ValueError(f"Invalid input state: {result}")
