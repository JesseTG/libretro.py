from ctypes import Structure, c_int
from dataclasses import dataclass
from typing import TYPE_CHECKING

from libretro.typing import FrontendFunctionPointer

retro_set_led_state_t = FrontendFunctionPointer[None, [c_int, c_int]]


@dataclass(init=False)
class retro_led_interface(Structure):
    if TYPE_CHECKING:
        set_led_state: retro_set_led_state_t | None

    _fields_ = [("set_led_state", retro_set_led_state_t)]

    def __deepcopy__(self, _):
        return retro_led_interface(self.set_led_state)


__all__ = ["retro_led_interface", "retro_set_led_state_t"]
