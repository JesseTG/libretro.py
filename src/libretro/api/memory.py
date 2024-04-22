from ctypes import POINTER, Structure, c_char_p, c_size_t, c_uint, c_uint64, c_void_p
from dataclasses import dataclass
from enum import IntFlag

from libretro.api._utils import FieldsFromTypeHints, deepcopy_array

RETRO_MEMDESC_CONST = 1 << 0
RETRO_MEMDESC_BIGENDIAN = 1 << 1
RETRO_MEMDESC_SYSTEM_RAM = 1 << 2
RETRO_MEMDESC_SAVE_RAM = 1 << 3
RETRO_MEMDESC_VIDEO_RAM = 1 << 4
RETRO_MEMDESC_ALIGN_2 = 1 << 16
RETRO_MEMDESC_ALIGN_4 = 2 << 16
RETRO_MEMDESC_ALIGN_8 = 3 << 16
RETRO_MEMDESC_MINSIZE_2 = 1 << 24
RETRO_MEMDESC_MINSIZE_4 = 2 << 24
RETRO_MEMDESC_MINSIZE_8 = 3 << 24


class MemoryDescriptorFlag(IntFlag):
    CONST = RETRO_MEMDESC_CONST
    BIGENDIAN = RETRO_MEMDESC_BIGENDIAN
    SYSTEM_RAM = RETRO_MEMDESC_SYSTEM_RAM
    SAVE_RAM = RETRO_MEMDESC_SAVE_RAM
    VIDEO_RAM = RETRO_MEMDESC_VIDEO_RAM
    ALIGN_2 = RETRO_MEMDESC_ALIGN_2
    ALIGN_4 = RETRO_MEMDESC_ALIGN_4
    ALIGN_8 = RETRO_MEMDESC_ALIGN_8
    MINSIZE_2 = RETRO_MEMDESC_MINSIZE_2
    MINSIZE_4 = RETRO_MEMDESC_MINSIZE_4
    MINSIZE_8 = RETRO_MEMDESC_MINSIZE_8


@dataclass(init=False)
class retro_memory_descriptor(Structure, metaclass=FieldsFromTypeHints):
    flags: c_uint64
    ptr: c_void_p
    offset: c_size_t
    start: c_size_t
    select: c_size_t
    disconnect: c_size_t
    len: c_size_t
    addrspace: c_char_p

    def __deepcopy__(self, _):
        return retro_memory_descriptor(
            flags=self.flags,
            ptr=self.ptr,
            offset=self.offset,
            start=self.start,
            select=self.select,
            disconnect=self.disconnect,
            len=self.len,
            addrspace=self.addrspace,
        )

    # TODO: Implement __getitem__, __setitem__
    # TODO: Implement a buffer property (not __buffer__ because Structure provides that)


@dataclass(init=False)
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
        return retro_memory_map(
            descriptors=deepcopy_array(self.descriptors, self.num_descriptors, memodict),
            num_descriptors=self.num_descriptors,
        )


__all__ = [
    "retro_memory_descriptor",
    "retro_memory_map",
    "MemoryDescriptorFlag",
]
