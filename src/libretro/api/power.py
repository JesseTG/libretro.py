from ctypes import Structure, c_int, c_int8
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

retro_power_state = c_int
RETRO_POWERSTATE_UNKNOWN = 0
RETRO_POWERSTATE_DISCHARGING = RETRO_POWERSTATE_UNKNOWN + 1
RETRO_POWERSTATE_CHARGING = RETRO_POWERSTATE_DISCHARGING + 1
RETRO_POWERSTATE_CHARGED = RETRO_POWERSTATE_CHARGING + 1
RETRO_POWERSTATE_PLUGGED_IN = RETRO_POWERSTATE_CHARGED + 1
RETRO_POWERSTATE_NO_ESTIMATE = -1

NO_ESTIMATE = RETRO_POWERSTATE_NO_ESTIMATE


class PowerState(IntEnum):
    UNKNOWN = RETRO_POWERSTATE_UNKNOWN
    DISCHARGING = RETRO_POWERSTATE_DISCHARGING
    CHARGING = RETRO_POWERSTATE_CHARGING
    CHARGED = RETRO_POWERSTATE_CHARGED
    PLUGGED_IN = RETRO_POWERSTATE_PLUGGED_IN


@dataclass(init=False)
class retro_device_power(Structure):
    if TYPE_CHECKING:
        state: PowerState
        seconds: int
        percent: int
    else:
        _fields_ = [
            ("state", retro_power_state),
            ("seconds", c_int),
            ("percent", c_int8),
        ]

    def __deepcopy__(self, _):
        return retro_device_power(state=self.state, seconds=self.seconds, percent=self.percent)


__all__ = [
    "PowerState",
    "retro_device_power",
    "retro_power_state",
    "NO_ESTIMATE",
]
