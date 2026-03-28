from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.input.device import Port
from libretro.api.sensor import Sensor, SensorAction


@runtime_checkable
class SensorDriver(Protocol):
    """
    Describes the interface for input from a device's sensors.

    .. note::

        Corresponds to ``RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE``.
    """

    @abstractmethod
    def set_sensor_state(self, port: Port, action: SensorAction, rate: int) -> bool:
        """
        Configures a sensor on a port,
        possibly with a specific query rate.

        Corresponds to :obj:`.retro_set_sensor_state_t`.

        .. note ::

            The :class:`.EnvironmentDriver` should validate ``port``
            against the maximum number of players (if any),
            skipping this method and returning :obj:`False`
            if the port is invalid.

        :param port: The input port to configure the sensors for.
        :param action: The action to perform on the sensor.
        :param rate: The rate at which to query the sensor.
        :return: Whether the sensor was successfully configured.
        """

    @abstractmethod
    def get_sensor_input(self, port: Port, sensor: Sensor) -> float:
        """
        Corresponds to ``retro_sensor_get_input_t``.
        """

    @abstractmethod
    def poll(self):
        """
        Updates the sensor driver's readings.
        """
        ...


__all__ = [
    "SensorDriver",
]
