from ctypes import Structure, c_int
from dataclasses import dataclass

from libretro.ctypes import CIntArg, TypedFunctionPointer

retro_set_led_state_t = TypedFunctionPointer[None, [CIntArg[c_int], CIntArg[c_int]]]


@dataclass(init=False, slots=True)
class retro_led_interface(Structure):
    set_led_state: retro_set_led_state_t | None

    _fields_ = (("set_led_state", retro_set_led_state_t),)

    def __deepcopy__(self, _):
        return retro_led_interface(self.set_led_state)


__all__ = ["retro_led_interface", "retro_set_led_state_t"]
