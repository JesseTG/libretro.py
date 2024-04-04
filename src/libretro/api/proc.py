from ctypes import CFUNCTYPE, Structure
from dataclasses import dataclass
from typing import AnyStr

from .._utils import FieldsFromTypeHints, String, UNCHECKED

retro_proc_address_t = CFUNCTYPE(None)
retro_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)


@dataclass(init=False)
class retro_get_proc_address_interface(Structure, metaclass=FieldsFromTypeHints):
    get_proc_address: retro_get_proc_address_t

    def __call__(self, sym: AnyStr) -> retro_proc_address_t:
        if not self.get_proc_address:
            raise ValueError("get_proc_address is NULL")

        return self.get_proc_address(sym)

    def __deepcopy__(self, _):
        return retro_get_proc_address_interface(self.get_proc_address)


__all__ = [
    "retro_get_proc_address_interface",
    'retro_proc_address_t',
    'retro_get_proc_address_t',
]
