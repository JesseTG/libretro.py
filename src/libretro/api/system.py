from ctypes import Structure, c_bool, c_char_p
from dataclasses import dataclass

from .._utils import FieldsFromTypeHints


@dataclass(init=False)
class retro_system_info(Structure, metaclass=FieldsFromTypeHints):
    library_name: c_char_p
    library_version: c_char_p
    valid_extensions: c_char_p
    need_fullpath: c_bool
    block_extract: c_bool

    def __deepcopy__(self, _):
        return retro_system_info(
            library_name=bytes(self.library_name) if self.library_name else None,
            library_version=bytes(self.library_version) if self.library_version else None,
            valid_extensions=bytes(self.valid_extensions) if self.valid_extensions else None,
            need_fullpath=self.need_fullpath,
            block_extract=self.block_extract
        )


__all__ = [
    'retro_system_info',
]
