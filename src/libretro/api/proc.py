from ctypes import CFUNCTYPE, Structure
from typing import AnyStr

from .._utils import FieldsFromTypeHints, String, UNCHECKED

retro_proc_address_t = CFUNCTYPE(None)
retro_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)


class retro_get_proc_address_interface(Structure, metaclass=FieldsFromTypeHints):
    get_proc_address: retro_get_proc_address_t

    def __call__(self, sym: AnyStr) -> retro_proc_address_t:
        if not self.get_proc_address:
            raise ValueError("get_proc_address is NULL")

        return self.get_proc_address(sym)