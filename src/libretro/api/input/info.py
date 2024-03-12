from ctypes import Structure, c_uint, c_char_p, POINTER
from typing import Sequence, overload

from ...retro import FieldsFromTypeHints


class retro_input_descriptor(Structure, metaclass=FieldsFromTypeHints):
    port: c_uint
    device: c_uint
    index: c_uint
    id: c_uint
    description: c_char_p


class retro_controller_description(Structure, metaclass=FieldsFromTypeHints):
    desc: c_char_p
    id: c_uint


class retro_controller_info(Structure, metaclass=FieldsFromTypeHints):
    types: POINTER(retro_controller_description)
    num_types: c_uint

    @overload
    def __getitem__(self, index: int) -> retro_controller_description: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[retro_controller_description]: ...

    def __getitem__(self, index):
        if not self.types:
            raise ValueError("No controller types available")

        match index:
            case int(i):
                if not (0 <= i < self.num_types):
                    raise IndexError(f"Expected 0 <= index < {len(self)}, got {i}")
                return self.types[i]

            case slice() as s:
                s: slice
                return self.types[s]

            case _:
                raise TypeError(f"Expected an int or slice index, got {type(index).__name__}")

    def __len__(self):
        return int(self.num_types)
