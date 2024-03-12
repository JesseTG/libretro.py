from ctypes import CFUNCTYPE, c_int, Structure

from ..retro import FieldsFromTypeHints

retro_set_led_state_t = CFUNCTYPE(None, c_int, c_int)


class retro_led_interface(Structure, metaclass=FieldsFromTypeHints):
    set_led_state: retro_set_led_state_t
