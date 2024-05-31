from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from libretro.api import (
    InputDevice,
    InputDeviceFlag,
    Key,
    KeyModifier,
    Port,
    retro_controller_info,
    retro_input_descriptor,
    retro_keyboard_callback,
)
from libretro.drivers.rumble import RumbleInterface
from libretro.drivers.sensor import SensorInterface


@runtime_checkable
class InputDriver(Protocol):
    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def state(self, port: Port, device: InputDevice, index: int, _id: int) -> int: ...

    @property
    @abstractmethod
    def descriptors(self) -> Sequence[retro_input_descriptor] | None: ...

    @descriptors.setter
    @abstractmethod
    def descriptors(self, descriptors: Sequence[retro_input_descriptor]) -> None: ...

    @property
    @abstractmethod
    def keyboard_callback(self) -> retro_keyboard_callback | None: ...

    @keyboard_callback.setter
    @abstractmethod
    def keyboard_callback(self, callback: retro_keyboard_callback) -> None: ...

    def keyboard_event(
        self, down: bool, keycode: Key, character: int, modifiers: KeyModifier
    ) -> None:
        callback = self.keyboard_callback
        if callback:
            callback.callback(down, keycode, character, modifiers)

    @property
    @abstractmethod
    def rumble(self) -> RumbleInterface | None: ...

    @property
    @abstractmethod
    def sensor(self) -> SensorInterface | None: ...

    @property
    @abstractmethod
    def device_capabilities(self) -> InputDeviceFlag | None: ...

    @device_capabilities.setter
    @abstractmethod
    def device_capabilities(self, capabilities: InputDeviceFlag) -> None: ...

    @device_capabilities.deleter
    @abstractmethod
    def device_capabilities(self) -> None: ...

    @property
    @abstractmethod
    def controller_info(self) -> Sequence[retro_controller_info] | None: ...

    @controller_info.setter
    @abstractmethod
    def controller_info(self, info: Sequence[retro_controller_info]) -> None: ...

    @property
    @abstractmethod
    def bitmasks_supported(self) -> bool | None: ...

    @bitmasks_supported.setter
    @abstractmethod
    def bitmasks_supported(self, bitmask_supported: bool) -> None: ...

    @bitmasks_supported.deleter
    @abstractmethod
    def bitmasks_supported(self) -> None: ...

    @property
    @abstractmethod
    def max_users(self) -> int | None: ...

    @max_users.setter
    @abstractmethod
    def max_users(self, max_users: int) -> None: ...

    @max_users.deleter
    @abstractmethod
    def max_users(self) -> None: ...


__all__ = ["InputDriver"]
