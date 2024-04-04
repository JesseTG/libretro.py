from copy import deepcopy
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

    def __deepcopy__(self, memodict):
        return retro_memory_descriptor(
            flags=self.flags.value,
            ptr=self.ptr.value,
            offset=self.offset.value,
            start=self.start.value,
            select=self.select.value,
            disconnect=self.disconnect.value,
            len=self.len.value,
            addrspace=self.addrspace.value
        )


class retro_memory_map(Structure, metaclass=FieldsFromTypeHints):
    descriptors: POINTER(retro_memory_descriptor)
    num_descriptors: c_uint

    def __len__(self):
        return self.num_descriptors

    def __getitem__(self, item):
        if item < 0 or item >= self.num_descriptors:
            raise IndexError(f"Expected 0 <= index < {self.num_descriptors}, got {item}")

        return self.descriptors[item]

    def __deepcopy__(self, memodict):
        arraytype = retro_memory_descriptor * self.num_descriptors.value
        descriptors: Array = arraytype()

        for i in range(self.num_descriptors.value):
            descriptors[i] = deepcopy(self.descriptors[i])

        return retro_memory_map(
            descriptors=descriptors,
            num_descriptors=self.num_descriptors.value
        )


__all__ = [
    "retro_memory_descriptor",
    "retro_memory_map",
]