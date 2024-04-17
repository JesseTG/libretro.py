from collections.abc import Mapping, Callable, KeysView
from ctypes import c_void_p
from types import MappingProxyType
from typing import override

from .driver import EnvironmentDriver
from libretro.error import UnsupportedEnvCall
from libretro.api import EnvironmentCall

EnvironmentCallbackFunction = Callable[[c_void_p], bool]


class DictEnvironmentDriver(
    EnvironmentDriver, Mapping[EnvironmentCall, EnvironmentCallbackFunction]
):
    def __init__(self, envcalls: Mapping[EnvironmentCall, EnvironmentCallbackFunction]):
        self._envcalls: Mapping[EnvironmentCall, EnvironmentCallbackFunction] = (
            MappingProxyType(envcalls)
        )

    @override
    def __getitem__(self, __key: EnvironmentCall) -> EnvironmentCallbackFunction:
        return self._envcalls[__key]

    @override
    def __len__(self):
        return len(self._envcalls)

    @override
    def __iter__(self) -> KeysView[EnvironmentCall]:
        return self._envcalls.keys()

    @override
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
