from ctypes import *

from ..h import retro_sensor_action
from .._utils import FieldsFromTypeHints

retro_set_sensor_state_t = CFUNCTYPE(c_bool, c_uint, retro_sensor_action, c_uint)
retro_sensor_get_input_t = CFUNCTYPE(c_float, c_uint, c_uint)


class retro_sensor_interface(Structure, metaclass=FieldsFromTypeHints):
    set_sensor_state: retro_set_sensor_state_t
    get_sensor_input: retro_sensor_get_input_t
