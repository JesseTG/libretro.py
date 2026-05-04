"""
Types for providing sensor input to cores.

.. seealso::
    :class:`.SensorDriver`
        The :class:`.Protocol` that uses these types to implement sensor support in libretro.py.

    :mod:`libretro.drivers.sensor`
        libretro.py's included :class:`.SensorDriver` implementations.
"""

from ctypes import Structure, c_bool, c_float, c_int, c_uint
from dataclasses import dataclass
from enum import IntEnum

from libretro.ctypes import CIntArg, TypedFunctionPointer

retro_sensor_action = c_int
"""Corresponds to :c:type:`retro_sensor_action` in ``libretro.h``."""

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


retro_set_sensor_state_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], CIntArg[retro_sensor_action], CIntArg[c_uint]]
]
"""Enables or disables a sensor for a given port."""

retro_sensor_get_input_t = TypedFunctionPointer[c_float, [CIntArg[c_uint], CIntArg[c_uint]]]
"""Reads a sensor value for a given port and sensor ID."""


@dataclass(init=False, slots=True)
class retro_sensor_interface(Structure):
    """
    Provides functions for managing sensor input.

    Corresponds to :c:type:`retro_sensor_interface` in ``libretro.h``.

    >>> from libretro.api import retro_sensor_interface
    >>> s = retro_sensor_interface()
    >>> s.set_sensor_state is None
    True
    """

    set_sensor_state: retro_set_sensor_state_t | None
    """Enables or disables a sensor for a given port."""
    get_sensor_input: retro_sensor_get_input_t | None
    """Reads a sensor value for a given port and sensor ID."""

    _fields_ = (
        ("set_sensor_state", retro_set_sensor_state_t),
        ("get_sensor_input", retro_sensor_get_input_t),
    )

    def __deepcopy__(self, _):
        """Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_sensor_interface
        >>> copy.deepcopy(retro_sensor_interface()).set_sensor_state is None
        True
        """
        return retro_sensor_interface(self.set_sensor_state, self.get_sensor_input)


class SensorType(IntEnum):
    """Type of sensor hardware.

    >>> from libretro.api import SensorType
    >>> SensorType.ACCELEROMETER
    <SensorType.ACCELEROMETER: 0>
    """

    ACCELEROMETER = 0
    GYROSCOPE = 3
    ILLUMINANCE = 6


class SensorAction(IntEnum):
    """Action to enable or disable a sensor.

    >>> from libretro.api import SensorAction
    >>> SensorAction.GYROSCOPE_ENABLE.enabled
    True
    """

    ACCELEROMETER_ENABLE = RETRO_SENSOR_ACCELEROMETER_ENABLE
    ACCELEROMETER_DISABLE = RETRO_SENSOR_ACCELEROMETER_DISABLE
    GYROSCOPE_ENABLE = RETRO_SENSOR_GYROSCOPE_ENABLE
    GYROSCOPE_DISABLE = RETRO_SENSOR_GYROSCOPE_DISABLE
    ILLUMINANCE_ENABLE = RETRO_SENSOR_ILLUMINANCE_ENABLE
    ILLUMINANCE_DISABLE = RETRO_SENSOR_ILLUMINANCE_DISABLE

    @property
    def sensor_type(self) -> SensorType:
        """Returns the :class:`SensorType` this action applies to.

        >>> from libretro.api import SensorAction, SensorType
        >>> SensorAction.ACCELEROMETER_ENABLE.sensor_type == SensorType.ACCELEROMETER
        True
        """
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
        """Returns ``True`` if this action enables the sensor.

        >>> from libretro.api import SensorAction
        >>> SensorAction.GYROSCOPE_DISABLE.enabled
        False
        """
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
    """Individual sensor axis or value identifiers.

    >>> from libretro.api import Sensor, SensorType
    >>> Sensor.GYROSCOPE_X.type == SensorType.GYROSCOPE
    True
    """

    ACCELEROMETER_X = RETRO_SENSOR_ACCELEROMETER_X
    ACCELEROMETER_Y = RETRO_SENSOR_ACCELEROMETER_Y
    ACCELEROMETER_Z = RETRO_SENSOR_ACCELEROMETER_Z
    GYROSCOPE_X = RETRO_SENSOR_GYROSCOPE_X
    GYROSCOPE_Y = RETRO_SENSOR_GYROSCOPE_Y
    GYROSCOPE_Z = RETRO_SENSOR_GYROSCOPE_Z
    ILLUMINANCE = RETRO_SENSOR_ILLUMINANCE

    @property
    def type(self) -> SensorType:
        """Returns the :class:`SensorType` for this sensor reading.

        >>> from libretro.api import Sensor, SensorType
        >>> Sensor.ILLUMINANCE.type == SensorType.ILLUMINANCE
        True
        """
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
