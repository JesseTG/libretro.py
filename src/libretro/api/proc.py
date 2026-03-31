from ctypes import Structure
from dataclasses import dataclass
from typing import TYPE_CHECKING

from libretro.typing import CStringArg, TypedFunctionPointer

retro_proc_address_t = TypedFunctionPointer[None, []]
retro_get_proc_address_t = TypedFunctionPointer[retro_proc_address_t, [CStringArg]]


@dataclass(init=False, slots=True)
class retro_get_proc_address_interface(Structure):
    if TYPE_CHECKING:
        get_proc_address: retro_get_proc_address_t | None

    _fields_ = [("get_proc_address", retro_get_proc_address_t)]

    def __call__(self, sym: str | bytes) -> retro_proc_address_t:
        if not self.get_proc_address:
            raise ValueError("get_proc_address is NULL")

        match sym:
            case str():
                sym_bytes = sym.encode("utf-8")
            case bytes():
                sym_bytes = sym
            case _:
                raise TypeError(f"sym must be str or bytes, got {type(sym).__name__}")

        return self.get_proc_address(sym_bytes)

    def __deepcopy__(self, _):
        return retro_get_proc_address_interface(self.get_proc_address)


__all__ = [
    "retro_get_proc_address_interface",
    "retro_proc_address_t",
    "retro_get_proc_address_t",
]
