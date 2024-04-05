from collections.abc import Callable
from ctypes import c_int, c_int8, Structure
from dataclasses import dataclass
from enum import IntEnum

from ..._utils import FieldsFromTypeHints
from ...h import *


class PowerState(IntEnum):
    UNKNOWN = RETRO_POWERSTATE_UNKNOWN
    DISCHARGING = RETRO_POWERSTATE_DISCHARGING
    CHARGING = RETRO_POWERSTATE_CHARGING
    CHARGED = RETRO_POWERSTATE_CHARGED
    PLUGGED_IN = RETRO_POWERSTATE_PLUGGED_IN

    def __init__(self, value: int):
        self._type_ = 'I'


@dataclass(init=False)
class retro_device_power(Structure, metaclass=FieldsFromTypeHints):
    state: retro_power_state
    seconds: c_int
    percent: c_int8

    def __deepcopy__(self, _):
        return retro_device_power(
            state=self.state,
            seconds=self.seconds,
            percent=self.percent
        )


DevicePower = Callable[[], retro_device_power]

__all__ = [
    'PowerState',
    'retro_device_power',
    'DevicePower',
]
