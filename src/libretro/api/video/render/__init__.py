from ctypes import CFUNCTYPE, POINTER, c_uint, Structure

from libretro.retro import FieldsFromTypeHints
from libretro.h import retro_hw_render_interface_type

class retro_hw_render_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_interface_type
    interface_version: c_uint
