from ctypes import CFUNCTYPE, Structure, c_int
from dataclasses import dataclass

from libretro.api._utils import FieldsFromTypeHints

retro_set_led_state_t = CFUNCTYPE(None, c_int, c_int)


@dataclass(init=False)
class retro_led_interface(Structure, metaclass=FieldsFromTypeHints):
    set_led_state: retro_set_led_state_t

    def __deepcopy__(self, _):
        return retro_led_interface(self.set_led_state)


__all__ = ["retro_led_interface", "retro_set_led_state_t"]
