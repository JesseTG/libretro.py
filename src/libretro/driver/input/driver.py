from abc import abstractmethod
from collections.abc import Sequence
from typing import runtime_checkable, Protocol

from libretro.api import (
    retro_input_descriptor,
    retro_keyboard_callback,
    retro_controller_info,
    Port,
    InputDevice,
    InputDeviceFlag,
)

from libretro.driver.rumble import RumbleInterface
from libretro.driver.sensor import SensorInterface


@runtime_checkable
class InputDriver(Protocol):
    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def state(self, port: Port, device: InputDevice, index: int, _id: int) -> int: ...

    @abstractmethod
    def set_descriptors(self, descriptors: Sequence[retro_input_descriptor] | None) -> None: ...

    @abstractmethod
    def get_descriptors(self) -> Sequence[retro_input_descriptor] | None: ...

    @property
    def descriptors(self) -> Sequence[retro_input_descriptor] | None:
        return self.get_descriptors()

    @descriptors.setter
    def descriptors(self, descriptors: Sequence[retro_input_descriptor]) -> None:
        self.set_descriptors(descriptors)

    @abstractmethod
    def set_keyboard_callback(self, callback: retro_keyboard_callback | None) -> None: ...

    @abstractmethod
    def get_keyboard_callback(self) -> retro_keyboard_callback | None: ...

    @property
    def keyboard_callback(self) -> retro_keyboard_callback | None:
        return self.get_keyboard_callback()

    @keyboard_callback.setter
    def keyboard_callback(self, callback: retro_keyboard_callback) -> None:
        self.set_keyboard_callback(callback)

    @keyboard_callback.deleter
    def keyboard_callback(self) -> None:
        self.set_keyboard_callback(None)

    @property
    @abstractmethod
    def rumble(self) -> RumbleInterface | None: ...

    @property
    @abstractmethod
    def device_capabilities(self) -> InputDeviceFlag | None: ...

    @property
    @abstractmethod
    def sensor(self) -> SensorInterface | None: ...

    @abstractmethod
    def get_controller_info(self) -> Sequence[retro_controller_info] | None: ...

    @abstractmethod
    def set_controller_info(self, info: Sequence[retro_controller_info] | None) -> bool: ...

    @property
    def controller_info(self) -> Sequence[retro_controller_info] | None:
        return self.get_controller_info()

    @controller_info.setter
    def controller_info(self, info: Sequence[retro_controller_info]) -> None:
        self.set_controller_info(info)

    @property
    @abstractmethod
    def bitmasks_supported(self) -> bool | None: ...

    @abstractmethod
    def get_max_users(self) -> int | None: ...

    @abstractmethod
    def set_max_users(self, max_users: int | None) -> None: ...

    @property
    def max_users(self) -> int | None:
        return self.get_max_users()

    @max_users.setter
    def max_users(self, max_users: int) -> None:
        self.set_max_users(max_users)

    @max_users.deleter
    def max_users(self) -> None:
        self.set_max_users(None)


__all__ = [
    'InputDriver'
]
