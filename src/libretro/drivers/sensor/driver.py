from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.sensor import Sensor, SensorAction


@runtime_checkable
class SensorDriver(Protocol):
    """
    Describes the interface for input from a device's sensors.

    .. note::

        Corresponds to ``RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE``.
    """

    @abstractmethod
    def set_sensor_state(self, port: int, action: SensorAction | int, rate: int) -> bool:
        """
        Configures a sensor on a port,
        possibly with a specific query rate.

        This method must be overridden,
        but can be called by subclasses
        to validate the input.

        Corresponds to ``retro_set_sensor_state_t``.

        .. note ::

            The :class:`EnvironmentDriver` should validate ``port``
            against the maximum number of players (if any),
            skipping this method and returning :obj:`False`
            if the port is invalid.

        :param port: The input port to configure the sensors for.
        :param action: The action to perform on the sensor.
        :param rate: The rate at which to query the sensor.
        :return: Whether the sensor was successfully configured.
        """

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

        return False

    @abstractmethod
    def get_sensor_input(self, port: int, sensor: int | Sensor) -> float:
        """
        Corresponds to ``retro_sensor_get_input_t``.

        This method must be overridden,
        but can be called by subclasses
        to validate the input.
        """

        if not isinstance(port, int):
            raise TypeError(f"port must be an int, not {type(port).__name__}")

        if not (0 <= port < ((2**32) - 1)):
            raise ValueError(f"Expected 0 <= port < 2**32 - 1, got {port}")

        if sensor not in Sensor:
            raise ValueError(f"sensor must be a Sensor, not {sensor}")

        return 0.0

    @abstractmethod
    def poll(self):
        """
        Updates the sensor driver's readings.
        """
        ...


__all__ = [
    "SensorDriver",
]
