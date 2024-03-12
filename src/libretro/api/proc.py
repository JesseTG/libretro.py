from ctypes import CFUNCTYPE, Structure

from ..retro import FieldsFromTypeHints, String, UNCHECKED

retro_proc_address_t = CFUNCTYPE(None, )
retro_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)


class retro_get_proc_address_interface(Structure, metaclass=FieldsFromTypeHints):
    get_proc_address: retro_get_proc_address_t
