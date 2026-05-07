"""
:class:`.EnvironmentDriver` implementation backed by a ``Mapping`` of envcall handlers.

.. seealso::

    :class:`.EnvironmentDriver`
        The protocol this implementation satisfies.
"""

from collections.abc import Callable, Iterator, Mapping
from ctypes import c_void_p
from types import MappingProxyType
from typing import override

from libretro.api import EnvironmentCall
from libretro.error import UnsupportedEnvCall

from .driver import EnvironmentDriver

EnvironmentCallbackFunction = Callable[[c_void_p], bool]


class DictEnvironmentDriver(
    EnvironmentDriver, Mapping[EnvironmentCall, EnvironmentCallbackFunction]
):
    """
    :class:`.EnvironmentDriver` backed by a mapping from :class:`.EnvironmentCall` to handlers.

    The instance also implements :class:`~collections.abc.Mapping` over its envcall handlers,
    so callers can introspect which environment calls a driver responds to.
    """

    def __init__(self, envcalls: Mapping[EnvironmentCall, EnvironmentCallbackFunction]):
        """
        Store ``envcalls`` as the registered handler mapping.

        :param envcalls: Mapping from :class:`.EnvironmentCall` to a callback that handles it.
        """
        self._envcalls: Mapping[EnvironmentCall, EnvironmentCallbackFunction] = MappingProxyType(
            envcalls
        )

    @override
    def __getitem__(self, __key: EnvironmentCall) -> EnvironmentCallbackFunction:
        return self._envcalls[__key]

    @override
    def __len__(self):
        return len(self._envcalls)

    @override
    def __iter__(self) -> Iterator[EnvironmentCall]:
        return iter(self._envcalls.keys())

    @override
    @EnvironmentDriver.return_on_raise(False)
    def environment(self, cmd: int, data: c_void_p) -> bool:
        if cmd not in EnvironmentCall:
            return False

        envcall = EnvironmentCall(cmd)
        if envcall in self._envcalls:
            try:
                return self._envcalls[envcall](data)
            except UnsupportedEnvCall:
                pass

        return False


__all__ = [
    "EnvironmentCallbackFunction",
    "DictEnvironmentDriver",
]
