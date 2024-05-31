from abc import abstractmethod
from collections.abc import Mapping, MutableMapping, Sequence
from typing import AnyStr, Protocol, runtime_checkable

from libretro.api.options import (
    retro_core_option_definition,
    retro_core_option_v2_category,
    retro_core_option_v2_definition,
    retro_core_options_intl,
    retro_core_options_update_display_callback,
    retro_core_options_v2,
    retro_core_options_v2_intl,
    retro_variable,
)


@runtime_checkable
class OptionDriver(Protocol):
    @abstractmethod
    def get_variable(self, item: bytes) -> bytes | None:
        """
        :param item: The key of the core option to retrieve.
        :return: If no option with the key given by ``item`` exists, return ``None``.
            If the option has a valid value (as determined by the option definitions), return it.
            Otherwise, return the default value.

        :note: Corresponds to ``EnvironmentCall.GET_VARIABLE``.
        """
        ...

    @abstractmethod
    def set_variables(self, variables: Sequence[retro_variable] | None): ...

    @property
    @abstractmethod
    def variable_updated(self) -> bool: ...

    @property
    @abstractmethod
    def version(self) -> int: ...

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

    @property
    @abstractmethod
    def update_display_callback(self) -> retro_core_options_update_display_callback: ...

    @update_display_callback.setter
    @abstractmethod
    def update_display_callback(
        self, callback: retro_core_options_update_display_callback | None
    ): ...

    @abstractmethod
    def set_variable(self, var: bytes, value: bytes) -> bool: ...

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
    "OptionDriver",
]
