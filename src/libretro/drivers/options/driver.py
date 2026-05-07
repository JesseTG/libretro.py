"""
:class:`~typing.Protocol` definition for the core options interface.

.. seealso::

    :mod:`libretro.api.options`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from collections.abc import Collection, Mapping, MutableMapping
from typing import Protocol, runtime_checkable

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
    """
    Protocol for drivers that store and resolve a core's runtime options.

    .. seealso::

        :mod:`libretro.api.options`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @abstractmethod
    def get_variable(self, key: bytes) -> bytes | None:
        """
        Return the current value of a single core option.

        Corresponds to ``RETRO_ENVIRONMENT_GET_VARIABLE``.

        :param key: The key of the core option to retrieve.
        :return: :obj:`None` if no option with the key given by ``key`` exists.
            Otherwise, the option's current value if it has a valid one
            (as determined by the option definitions),
            or the default value otherwise.
        """
        ...

    @abstractmethod
    def set_variables(self, variables: Collection[retro_variable] | None) -> None:
        """
        Register the v0 core option variables advertised by the core.

        Corresponds to ``RETRO_ENVIRONMENT_SET_VARIABLES``.

        :param variables: The variables registered by the core,
            or :obj:`None` to clear the registration.
        """
        ...

    @property
    @abstractmethod
    def variable_updated(self) -> bool:
        """
        Whether any core option has been changed since the core last queried it.

        Corresponds to ``RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE``.
        Reading this property is expected to clear the flag.
        """
        ...

    @property
    @abstractmethod
    def version(self) -> int:
        """
        The core options interface version this driver implements.

        Corresponds to ``RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION``.
        """
        ...

    @abstractmethod
    def set_options(self, options: Collection[retro_core_option_definition] | None) -> None:
        """
        Register the v1 core option definitions advertised by the core.

        Corresponds to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS``.

        :param options: The options registered by the core,
            or :obj:`None` to clear the registration.
        """
        ...

    @abstractmethod
    def set_options_intl(self, options: retro_core_options_intl | None) -> None:
        """
        Register the v1 core option definitions, with translations, advertised by the core.

        Corresponds to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL``.

        :param options: The options registered by the core,
            or :obj:`None` to clear the registration.
        """
        ...

    @abstractmethod
    def set_display(self, key: bytes, visible: bool) -> None:
        """
        Show or hide a single core option in the frontend's UI.

        Corresponds to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY``.

        :param key: The key of the option to update.
        :param visible: :obj:`True` to show the option, :obj:`False` to hide it.
        """
        ...

    @abstractmethod
    def set_options_v2(self, options: retro_core_options_v2 | None) -> None:
        """
        Register the v2 core option definitions advertised by the core.

        Corresponds to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2``.

        :param options: The options registered by the core,
            or :obj:`None` to clear the registration.
        """
        ...

    @abstractmethod
    def set_options_v2_intl(self, options: retro_core_options_v2_intl | None) -> None:
        """
        Register the v2 core option definitions, with translations, advertised by the core.

        Corresponds to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL``.

        :param options: The options registered by the core,
            or :obj:`None` to clear the registration.
        """
        ...

    @property
    @abstractmethod
    def update_display_callback(self) -> retro_core_options_update_display_callback | None:
        """
        The display-update callback registered by the core, if any.

        Set via ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK``.
        :obj:`None` if the core has not registered one.

        :param callback: The callback to register, or :obj:`None` to clear it.
        :raises UnsupportedEnvCall: If this driver does not support the display-update callback.
        """
        ...

    @update_display_callback.setter
    @abstractmethod
    def update_display_callback(
        self, callback: retro_core_options_update_display_callback | None
    ) -> None:
        """See :attr:`update_display_callback`."""
        ...

    @abstractmethod
    def set_variable(self, var: bytes, value: bytes) -> bool:
        """
        Set a single core option's value.

        Corresponds to ``RETRO_ENVIRONMENT_SET_VARIABLE``.

        :param var: The key of the option to set.
        :param value: The new value for the option.
        :return: :obj:`True` if the value was accepted by the driver.
        """
        ...

    @property
    @abstractmethod
    def supports_categories(self) -> bool:
        """Whether this driver groups core options into categories (v2 feature)."""
        ...

    @property
    @abstractmethod
    def variables(self) -> MutableMapping[bytes, bytes]:
        """
        A live, mutable mapping of option keys to current values.

        Mutating the returned mapping changes the driver's stored option values
        and is the primary way to drive option changes from a Python test harness.
        """
        ...

    @property
    @abstractmethod
    def visibility(self) -> Mapping[bytes, bool]:
        """A mapping of option keys to whether the frontend would show that option."""
        ...

    @property
    @abstractmethod
    def categories(self) -> Mapping[bytes, retro_core_option_v2_category] | None:
        """
        The v2 option categories registered by the core, indexed by category key.

        :obj:`None` if the core has not registered any categories
        or this driver does not support categories.
        """
        ...

    @property
    @abstractmethod
    def definitions(self) -> Mapping[bytes, retro_core_option_v2_definition] | None:
        """
        The v2 option definitions registered by the core, indexed by option key.

        :obj:`None` if the core has not registered any v2 definitions.
        """
        ...


__all__ = [
    "OptionDriver",
]
