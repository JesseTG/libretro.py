from ctypes import CFUNCTYPE, Structure, c_bool, c_float, c_int, c_uint
from dataclasses import dataclass
from enum import IntEnum

from libretro.api._utils import FieldsFromTypeHints

retro_sensor_action = c_int
RETRO_SENSOR_ACCELEROMETER_ENABLE = 0
RETRO_SENSOR_ACCELEROMETER_DISABLE = RETRO_SENSOR_ACCELEROMETER_ENABLE + 1
RETRO_SENSOR_GYROSCOPE_ENABLE = RETRO_SENSOR_ACCELEROMETER_DISABLE + 1
RETRO_SENSOR_GYROSCOPE_DISABLE = RETRO_SENSOR_GYROSCOPE_ENABLE + 1
RETRO_SENSOR_ILLUMINANCE_ENABLE = RETRO_SENSOR_GYROSCOPE_DISABLE + 1
RETRO_SENSOR_ILLUMINANCE_DISABLE = RETRO_SENSOR_ILLUMINANCE_ENABLE + 1
RETRO_SENSOR_DUMMY = 0x7FFFFFFF

RETRO_SENSOR_ACCELEROMETER_X = 0
RETRO_SENSOR_ACCELEROMETER_Y = 1
RETRO_SENSOR_ACCELEROMETER_Z = 2
RETRO_SENSOR_GYROSCOPE_X = 3
RETRO_SENSOR_GYROSCOPE_Y = 4
RETRO_SENSOR_GYROSCOPE_Z = 5
RETRO_SENSOR_ILLUMINANCE = 6

retro_set_sensor_state_t = CFUNCTYPE(c_bool, c_uint, retro_sensor_action, c_uint)
retro_sensor_get_input_t = CFUNCTYPE(c_float, c_uint, c_uint)


@dataclass(init=False)
class retro_sensor_interface(Structure, metaclass=FieldsFromTypeHints):
    set_sensor_state: retro_set_sensor_state_t
    get_sensor_input: retro_sensor_get_input_t

    def __deepcopy__(self, _):
        return retro_sensor_interface(self.set_sensor_state, self.get_sensor_input)


class SensorType(IntEnum):
    ACCELEROMETER = 0
    GYROSCOPE = 1
    ILLUMINANCE = 2


class SensorAction(IntEnum):
    ACCELEROMETER_ENABLE = RETRO_SENSOR_ACCELEROMETER_ENABLE
    ACCELEROMETER_DISABLE = RETRO_SENSOR_ACCELEROMETER_DISABLE
    GYROSCOPE_ENABLE = RETRO_SENSOR_GYROSCOPE_ENABLE
    GYROSCOPE_DISABLE = RETRO_SENSOR_GYROSCOPE_DISABLE
    ILLUMINANCE_ENABLE = RETRO_SENSOR_ILLUMINANCE_ENABLE
    ILLUMINANCE_DISABLE = RETRO_SENSOR_ILLUMINANCE_DISABLE

    def __init__(self, value):
        self._type_ = "i"

    @property
    def sensor_type(self) -> SensorType:
        match self:
            case SensorAction.ACCELEROMETER_ENABLE | SensorAction.ACCELEROMETER_DISABLE:
                return SensorType.ACCELEROMETER
            case SensorAction.GYROSCOPE_ENABLE | SensorAction.GYROSCOPE_DISABLE:
                return SensorType.GYROSCOPE
            case SensorAction.ILLUMINANCE_ENABLE | SensorAction.ILLUMINANCE_DISABLE:
                return SensorType.ILLUMINANCE
            case _:
                raise ValueError(f"Invalid action: {self}")

    @property
    def enabled(self) -> bool:
        match self:
            case (
                SensorAction.ACCELEROMETER_ENABLE
                | SensorAction.GYROSCOPE_ENABLE
                | SensorAction.ILLUMINANCE_ENABLE
            ):
                return True
            case (
                SensorAction.ACCELEROMETER_DISABLE
                | SensorAction.GYROSCOPE_DISABLE
                | SensorAction.ILLUMINANCE_DISABLE
            ):
                return False
            case _:
                raise ValueError(f"Invalid action: {self}")


class Sensor(IntEnum):
    ACCELEROMETER_X = RETRO_SENSOR_ACCELEROMETER_X
    ACCELEROMETER_Y = RETRO_SENSOR_ACCELEROMETER_Y
    ACCELEROMETER_Z = RETRO_SENSOR_ACCELEROMETER_Z
    GYROSCOPE_X = RETRO_SENSOR_GYROSCOPE_X
    GYROSCOPE_Y = RETRO_SENSOR_GYROSCOPE_Y
    GYROSCOPE_Z = RETRO_SENSOR_GYROSCOPE_Z
    ILLUMINANCE = RETRO_SENSOR_ILLUMINANCE

    def __init__(self, value):
        self._type_ = "i"

    @property
    def type(self) -> SensorType:
        match self:
            case Sensor.ACCELEROMETER_X | Sensor.ACCELEROMETER_Y | Sensor.ACCELEROMETER_Z:
                return SensorType.ACCELEROMETER
            case Sensor.GYROSCOPE_X | Sensor.GYROSCOPE_Y | Sensor.GYROSCOPE_Z:
                return SensorType.GYROSCOPE
            case Sensor.ILLUMINANCE:
                return SensorType.ILLUMINANCE
            case _:
                raise ValueError(f"Invalid sensor: {self}")


__all__ = [
    "retro_set_sensor_state_t",
    "retro_sensor_get_input_t",
    "retro_sensor_interface",
    "SensorAction",
    "SensorType",
    "Sensor",
    "retro_sensor_action",
]
