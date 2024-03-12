from ctypes import *

from .._utils import FieldsFromTypeHints

class retro_memory_descriptor(Structure, metaclass=FieldsFromTypeHints):
    flags: c_uint64
    ptr: c_void_p
    offset: c_size_t
    start: c_size_t
    select: c_size_t
    disconnect: c_size_t
    len: c_size_t
    addrspace: c_char_p


class retro_memory_map(Structure, metaclass=FieldsFromTypeHints):
    descriptors: POINTER(retro_memory_descriptor)
    num_descriptors: c_uint
