from abc import abstractmethod
from collections.abc import Sequence, Mapping
from typing import Protocol, runtime_checkable, MutableMapping, AnyStr

from .defs import *


@runtime_checkable
class OptionDriver(Protocol):
    @abstractmethod
    def get_variable(self, item: bytes) -> bytes | None: ...

    @abstractmethod
    def set_variables(self, variables: Sequence[retro_variable] | None): ...

    @abstractmethod
    def get_variable_update(self) -> bool: ...

    @abstractmethod
    def get_version(self) -> int: ...

    @abstractmethod
    def set_options(self, options: Sequence[retro_core_option_definition] | None): ...

    @abstractmethod
    def set_options_intl(self, options: retro_core_options_intl | None): ...

    @abstractmethod
    def set_display(self, var: bytes, visible: bool): ...

    @abstractmethod
    def set_options_v2(self, options: retro_core_options_v2 | None): ...

    @abstractmethod
    def set_options_v2_intl(self, options: retro_core_options_v2_intl | None): ...

    @abstractmethod
    def set_update_display_callback(self, callback: retro_core_options_update_display_callback | None): ...

    @abstractmethod
    def set_variable(self, var: bytes, value: bytes) -> bool: ...

    @property
    def variable_updated(self) -> bool:
        return self.get_variable_update()

    @property
    def version(self):
        return self.get_version()

    @property
    @abstractmethod
    def update_display_callback(self) -> retro_core_options_update_display_callback | None: ...

    @property
    @abstractmethod
    def supports_categories(self) -> bool: ...

    @property
    @abstractmethod
    def variables(self) -> MutableMapping[AnyStr, bytes]: ...

    @property
    @abstractmethod
    def visibility(self) -> Mapping[AnyStr, bool]: ...

    @property
    @abstractmethod
    def categories(self) -> Mapping[bytes, retro_core_option_v2_category] | None: ...

    @property
    @abstractmethod
    def definitions(self) -> Mapping[bytes, retro_core_option_v2_definition] | None: ...


__all__ = [
    'OptionDriver',
]
