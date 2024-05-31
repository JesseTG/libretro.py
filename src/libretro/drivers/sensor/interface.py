from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.sensor import (
    Sensor,
    SensorAction,
    retro_sensor_get_input_t,
    retro_sensor_interface,
    retro_set_sensor_state_t,
)


@runtime_checkable
class SensorInterface(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_sensor_interface()
        self._as_parameter_.set_sensor_state = retro_set_sensor_state_t(self.__set_sensor_state)
        self._as_parameter_.get_sensor_input = retro_sensor_get_input_t(self.__get_sensor_input)

    def set_sensor_state(self, port: int, action: SensorAction | int, rate: int) -> bool:
        if not isinstance(port, int):
            raise TypeError(f"port must be an int, not {type(port).__name__}")

        if not (0 <= port < ((2**32) - 1)):
            raise ValueError(f"Expected 0 <= port < 2**32 - 1, got {port}")

        if action not in SensorAction:
            raise ValueError(f"action must be a SensorAction, not {action}")

        if not isinstance(rate, int):
            raise TypeError(f"rate must be an int, not {type(rate).__name__}")

        if not (0 <= rate < ((2**32) - 1)):
            raise ValueError(f"Expected 0 <= rate < 2**32 - 1, got {rate}")

        return bool(self._set_sensor_state(port, SensorAction(action), rate))

    @abstractmethod
    def _set_sensor_state(self, port: int, action: SensorAction, rate: int) -> bool: ...

    def __set_sensor_state(self, port: int, action: int, rate: int) -> bool:
        return self.set_sensor_state(port, SensorAction(action), rate)

    def get_sensor_input(self, port: int, sensor: Sensor) -> float:
        if not isinstance(port, int):
            raise TypeError(f"port must be an int, not {type(port).__name__}")

        if not (0 <= port < ((2**32) - 1)):
            raise ValueError(f"Expected 0 <= port < 2**32 - 1, got {port}")

        if sensor not in Sensor:
            raise ValueError(f"sensor must be a Sensor, not {sensor}")

        match self._get_sensor_input(port, Sensor(sensor)):
            case float(f) | bool(f) | int(f):
                return float(f)
            case e:
                raise TypeError(
                    f"Expected _get_sensor_input to return a float, got {type(e).__name__}"
                )

    @abstractmethod
    def _get_sensor_input(self, port: int, sensor: Sensor) -> float: ...

    def __get_sensor_input(self, port: int, sensor: int) -> float:
        return self.get_sensor_input(port, Sensor(sensor))


__all__ = [
    "SensorInterface",
]
