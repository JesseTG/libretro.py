from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import override

from libretro.api.input import Port
from libretro.api.sensor import Sensor, SensorAction, SensorType

from .driver import SensorDriver


@dataclass(frozen=True, slots=True)
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass(slots=True)
class SensorState:
    enabled: bool = False
    rate: int = 0


@dataclass(frozen=True, slots=True)
class PortInput:
    accelerometer = Vector3()
    gyroscope = Vector3()
    illuminance: float = 0.0

    def __getitem__(self, item: Sensor) -> float:
        match item:
            case Sensor.ACCELEROMETER_X:
                return self.accelerometer.x
            case Sensor.ACCELEROMETER_Y:
                return self.accelerometer.y
            case Sensor.ACCELEROMETER_Z:
                return self.accelerometer.z
            case Sensor.GYROSCOPE_X:
                return self.gyroscope.x
            case Sensor.GYROSCOPE_Y:
                return self.gyroscope.y
            case Sensor.GYROSCOPE_Z:
                return self.gyroscope.z
            case Sensor.ILLUMINANCE:
                return self.illuminance
            case _:
                raise KeyError(f"Invalid sensor: {item}")


@dataclass(slots=True)
class PortState:
    """
    Represents the state of all possible sensors on a port.
    """

    accelerometer: SensorState = field(default_factory=SensorState)
    gyroscope: SensorState = field(default_factory=SensorState)
    illuminance: SensorState = field(default_factory=SensorState)

    def __getitem__(self, item: Sensor | SensorType) -> SensorState:
        match item:
            case (
                Sensor.ACCELEROMETER_X
                | Sensor.ACCELEROMETER_Y
                | Sensor.ACCELEROMETER_Z
                | SensorType.ACCELEROMETER
            ):
                return self.accelerometer
            case (
                Sensor.GYROSCOPE_X | Sensor.GYROSCOPE_Y | Sensor.GYROSCOPE_Z | SensorType.GYROSCOPE
            ):
                return self.gyroscope
            case Sensor.ILLUMINANCE | SensorType.ILLUMINANCE:
                return self.illuminance
            case _:
                raise TypeError(f"Expected a Sensor or SensorType, got {type(item).__name__}")


SensorPollResult = float | Vector3 | PortInput | None
SensorStateIterator = Iterator[SensorPollResult | Sequence[SensorPollResult]]
SensorStateIterable = Iterable[SensorPollResult | Sequence[SensorPollResult]]
SensorStateGenerator = Callable[[], SensorStateIterator]
SensorStateSource = SensorStateIterator | SensorStateIterable | SensorStateGenerator


class IterableSensorDriver(SensorDriver):
    """
    A :class:`.SensorDriver` that feeds input to the core
    from the output of an iterator.
    """

    def __init__(self, source: SensorStateSource | None = None):
        """
        Initializes this sensor driver.
        If a sensor is disabled, then it will always output 0.0.

        :param source: An iterator or iterable whose elements are each one of the following:

            :obj:`None`
                All sensors on all ports will return 0.0.

            :class:`int` | :class:`float` | :class:`bool` | :class:`~numbers.Real`
                All sensors on all ports
                will return the yielded value converted to a :class:`float`.

            :class:`.Vector3`
                Each value be used as the x, y, and z readings
                for every port's accelerometer and gyroscope.

            :class:`.PortInput`
                The fields on the yielded object will be used
                as each port's sensor readings.

            :class:`~collections.abc.Sequence` [ :class:`.PortInput` | :class:`.AccelerometerInput` | :class:`.GyroscopeInput` | :class:`.IlluminanceInput` ]
                Each element in the sequence will be used
                for its corresponding port's sensor readings
                based on the aforementioned rules.
        """
        self._generator = source
        self._generator_state: SensorStateIterator | None = None
        self._poll_result: SensorPollResult | Sequence[SensorPollResult] | None = None
        self._ports: defaultdict[Port, PortState] = defaultdict(PortState)

    @property
    def sensor_state(self) -> Mapping[Port, PortState]:
        return self._ports

    @override
    def poll(self) -> None:
        if not self._generator:
            return

        if self._generator_state is None:
            match self._generator:
                case Callable() as func:
                    self._generator_state = func()
                case Iterator() as it:
                    self._generator_state = it
                case Iterable() as it:
                    self._generator_state = iter(it)
        self._poll_result = next(self._generator_state, None)

    @override
    def set_sensor_state(self, port: Port, action: SensorAction | int, rate: int) -> bool:
        # It's fine if port is out of bounds,
        # the defaultdict will create a new PortState for it
        match action:
            case SensorAction.ACCELEROMETER_ENABLE:
                self._ports[port].accelerometer.enabled = True
                self._ports[port].accelerometer.rate = rate
            case SensorAction.ACCELEROMETER_DISABLE:
                self._ports[port].accelerometer.enabled = False
                self._ports[port].accelerometer.rate = rate
            case SensorAction.GYROSCOPE_ENABLE:
                self._ports[port].gyroscope.enabled = True
                self._ports[port].gyroscope.rate = rate
            case SensorAction.GYROSCOPE_DISABLE:
                self._ports[port].gyroscope.enabled = False
                self._ports[port].gyroscope.rate = rate
            case SensorAction.ILLUMINANCE_ENABLE:
                self._ports[port].illuminance.enabled = True
                self._ports[port].illuminance.rate = rate
            case SensorAction.ILLUMINANCE_DISABLE:
                self._ports[port].illuminance.enabled = False
                self._ports[port].illuminance.rate = rate
            case _:
                return False

        return True

    @override
    def get_sensor_input(self, port: Port, sensor: Sensor) -> float:
        if not self._generator:
            # An unassigned generator will default to 0
            return 0.0

        match (self._poll_result, port, sensor):
            case (None | [], _, _):
                # An empty result will default to 0
                return 0.0

            case _, _, sensor if not self._ports[port][sensor].enabled:
                # Disabled sensors will always return 0
                return 0.0

            case [*results], port, sensor:
                # Yielding a sequence of result types
                # will expose it to the port that corresponds to each index,
                # with unfilled ports defaulting to 0.
                return self._lookup_port_state(results[port], sensor)

            case result, port, sensor:
                # Yielding a type that's _not_ a sequence
                # will expose it to all ports.
                return self._lookup_port_state(result, sensor)

            case _, _, _:
                return 0.0

    def _lookup_port_state(self, result: SensorPollResult, sensor: Sensor) -> float:
        # The port's enabled state is handled by _get_sensor_input

        match result, sensor:
            # yielding None returns 0.0
            case None, _:
                return 0.0

            case PortInput() as port_input, Sensor.ACCELEROMETER_X:
                return port_input.accelerometer.x
            case PortInput() as port_input, Sensor.ACCELEROMETER_Y:
                return port_input.accelerometer.y
            case PortInput() as port_input, Sensor.ACCELEROMETER_Z:
                return port_input.accelerometer.z
            case PortInput() as port_input, Sensor.GYROSCOPE_X:
                return port_input.gyroscope.x
            case PortInput() as port_input, Sensor.GYROSCOPE_Y:
                return port_input.gyroscope.y
            case PortInput() as port_input, Sensor.GYROSCOPE_Z:
                return port_input.gyroscope.z
            case PortInput() as port_input, Sensor.ILLUMINANCE:
                return port_input.illuminance

            # yielding a number returns it unconditionally
            case float(r), _:
                return r

            # yielding a Vector3 returns the corresponding axis for the gyroscope and accelerometer
            case Vector3(x=x), Sensor.ACCELEROMETER_X | Sensor.GYROSCOPE_X:
                return float(x)
            case Vector3(y=y), Sensor.ACCELEROMETER_Y | Sensor.GYROSCOPE_Y:
                return float(y)
            case Vector3(z=z), Sensor.ACCELEROMETER_Z | Sensor.GYROSCOPE_Z:
                return float(z)

            case _, _:
                raise TypeError(f"Unexpected result type: {type(result).__name__}")


__all__ = [
    "Vector3",
    "SensorState",
    "PortInput",
    "SensorPollResult",
    "SensorStateIterator",
    "SensorStateIterable",
    "SensorStateGenerator",
    "IterableSensorDriver",
]
