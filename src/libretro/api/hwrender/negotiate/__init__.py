from ctypes import Structure, c_uint

from ....retro import FieldsFromTypeHints
from ....h import retro_hw_render_context_negotiation_interface_type


class retro_hw_render_context_negotiation_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_context_negotiation_interface_type
    interface_version: c_uint
