from ctypes import CFUNCTYPE, c_int, Structure
from dataclasses import dataclass

from ..._utils import FieldsFromTypeHints

retro_set_led_state_t = CFUNCTYPE(None, c_int, c_int)


@dataclass(init=False)
class retro_led_interface(Structure, metaclass=FieldsFromTypeHints):
    set_led_state: retro_set_led_state_t


__all__ = ['retro_led_interface', 'retro_set_led_state_t']
