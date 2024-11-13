from collections.abc import Callable, Generator, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, is_dataclass
from numbers import Real
from typing import Literal, overload

from libretro._typing import override
from libretro.api.sensor import Sensor, SensorAction, SensorType

from .driver import SensorDriver


@dataclass(slots=True)
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass(slots=True)
class SensorState:
    accelerometer_enabled: bool = False
    accelerometer_rate: int = 0

    gyroscope_enabled: bool = False
    gyroscope_rate: int = 0

    illuminance_enabled: bool = False
    illuminance_rate: int = 0

    def is_enabled(self, sensor: SensorType) -> bool:
        if not isinstance(sensor, SensorType):
            raise TypeError(f"Expected a SensorType, got {type(sensor).__name__}")

        match sensor:
            case SensorType.ACCELEROMETER:
                return self.accelerometer_enabled
            case SensorType.GYROSCOPE:
                return self.gyroscope_enabled
            case SensorType.ILLUMINANCE:
                return self.illuminance_enabled
            case _:
                raise ValueError(f"Invalid sensor type: {sensor}")


class SensorInput:
    pass


@dataclass(slots=True)
class AccelerometerInput(SensorInput):
    """
    Represents a reading from a 3D accelerometer.
    """

    x: float = 0.0
    """The acceleration along the x-axis, in meters per second squared."""

    y: float = 0.0
    """The acceleration along the y-axis, in meters per second squared."""

    z: float = 0.0
    """The acceleration along the z-axis, in meters per second squared."""


@dataclass(slots=True)
class GyroscopeInput(SensorInput):
    """
    Represents a reading from a 3D gyroscope.
    """

    x: float = 0.0
    """The angular velocity around the x-axis, in radians per second."""

    y: float = 0.0
    """The angular velocity around the y-axis, in radians per second."""

    z: float = 0.0
    """The angular velocity around the z-axis, in radians per second."""


@dataclass(slots=True)
class IlluminanceInput(SensorInput):
    """
    Represents a reading from an illuminance sensor.
    """

    value: float = 0.0
    """The illuminance value, in lux."""


@dataclass(slots=True)
class PortInput:
    """
    Represents the state of all possible sensors on a port.
    """

    accelerometer: AccelerometerInput = field(default_factory=AccelerometerInput)
    gyroscope: GyroscopeInput = field(default_factory=GyroscopeInput)
    illuminance: IlluminanceInput = field(default_factory=IlluminanceInput)

    @overload
    def __getitem__(self, item: Sensor) -> float: ...

    @overload
    def __getitem__(self, item: Literal[SensorType.ACCELEROMETER]) -> AccelerometerInput: ...

    @overload
    def __getitem__(self, item: Literal[SensorType.GYROSCOPE]) -> GyroscopeInput: ...

    @overload
    def __getitem__(self, item: Literal[SensorType.ILLUMINANCE]) -> IlluminanceInput: ...

    @overload
    def __getitem__(self, item: SensorType) -> SensorInput: ...

    def __getitem__(self, item: Sensor | SensorType) -> float | SensorInput:
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
            case SensorType.ACCELEROMETER:
                return self.accelerometer
            case SensorType.GYROSCOPE:
                return self.gyroscope
            case SensorType.ILLUMINANCE:
                return self.illuminance
            case _:
                raise TypeError(f"Expected a Sensor or SensorType, got {type(item).__name__}")

    @overload
    def __setitem__(self, key: Sensor, value: float): ...

    @overload
    def __setitem__(self, key: Literal[SensorType.ACCELEROMETER], value: AccelerometerInput): ...

    @overload
    def __setitem__(self, key: Literal[SensorType.GYROSCOPE], value: GyroscopeInput): ...

    @overload
    def __setitem__(self, key: Literal[SensorType.ILLUMINANCE], value: IlluminanceInput): ...

    @overload
    def __setitem__(self, key: SensorType, value: SensorState): ...

    def __setitem__(self, key: Sensor | SensorType, value: float | SensorInput):
        match key, value:
            case Sensor.ACCELEROMETER_X, Real(x):
                self.accelerometer.x = x
            case Sensor.ACCELEROMETER_Y, Real(y):
                self.accelerometer.y = y
            case Sensor.ACCELEROMETER_Z, Real(z):
                self.accelerometer.z = z
            case Sensor.GYROSCOPE_X, Real(x):
                self.gyroscope.x = x
            case Sensor.GYROSCOPE_Y, Real(y):
                self.gyroscope.y = y
            case Sensor.GYROSCOPE_Z, Real(z):
                self.gyroscope.z = z
            case Sensor.ILLUMINANCE, Real(v):
                self.illuminance.value = v
            case SensorType.ACCELEROMETER, SensorState(s):
                self.accelerometer = s
            case SensorType.GYROSCOPE, SensorState(s):
                self.gyroscope = s
            case SensorType.ILLUMINANCE, SensorState(s):
                self.illuminance = s
            case (Sensor(s) | SensorType(s)), _:
                raise TypeError(f"Cannot set {s} from {type(value).__name__}")
            case _, _:
                raise TypeError(f"Cannot set {type(key).__name__} from {type(value).__name__}")


SensorPollResult = Real | tuple[Real, Real, Real] | PortInput | SensorInput | None
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

        :param source: An iterator or iterable whose elements are each one of the following:

            :obj:`None`
                All sensors on all ports will return 0.0.

            :class:`int` | :class:`float` | :class:`bool` | :class:`Real`
                All sensors on all ports
                will return the yielded value converted to a :class:`float`.

            :class:`tuple`[:class:`Real`, :class:`Real`, :class:`Real`]
                All three values will be converted to :class:`float`s
                and used as the x, y, and z readings
                for every port's sensors.
                For the luminance sensor, only the first element will be used.
        """
        self._generator = source
        self._generator_state: SensorStateIterator | None = None
        self._poll_result: SensorPollResult = None
        self._sensor_state: dict[int, SensorState] = dict()

    @property
    def sensor_state(self) -> Mapping[int, SensorState]:
        return self._sensor_state

    @override
    def poll(self) -> None:
        if self._generator:
            if self._generator_state is None:
                match self._generator:
                    case Callable() as func:
                        self._generator_state = func()
                    case Iterable() | Iterator() | Generator() as it:
                        self._generator_state = it

            self._poll_result = next(self._generator_state, None)

    @override
    def set_sensor_state(self, port: int, action: SensorAction, rate: int) -> bool:
        super().set_sensor_state(port, action, rate)

        if port not in self._sensor_state:
            self._sensor_state[port] = SensorState()

        match action:
            case SensorAction.ACCELEROMETER_ENABLE:
                self._sensor_state[port].accelerometer_enabled = True
                self._sensor_state[port].accelerometer_rate = rate
            case SensorAction.ACCELEROMETER_DISABLE:
                self._sensor_state[port].accelerometer_enabled = False
                self._sensor_state[port].accelerometer_rate = rate
            case SensorAction.GYROSCOPE_ENABLE:
                self._sensor_state[port].gyroscope_enabled = True
                self._sensor_state[port].gyroscope_rate = rate
            case SensorAction.GYROSCOPE_DISABLE:
                self._sensor_state[port].gyroscope_enabled = False
                self._sensor_state[port].gyroscope_rate = rate
            case SensorAction.ILLUMINANCE_ENABLE:
                self._sensor_state[port].illuminance_enabled = True
                self._sensor_state[port].illuminance_rate = rate
            case SensorAction.ILLUMINANCE_DISABLE:
                self._sensor_state[port].illuminance_enabled = False
                self._sensor_state[port].illuminance_rate = rate

        return True

    @override
    def get_sensor_input(self, port: int, sensor: Sensor) -> float:
        super().get_sensor_input(port, sensor)

        if not self._generator:
            # An unassigned generator will default to 0
            return 0.0

        match (self._poll_result, port, sensor):
            case (None | [], _, _):
                # An empty result will default to 0
                return 0.0

            case _, _, _ if not self._sensor_state[port].is_enabled(sensor.type):
                # Disabled sensors will always return 0
                # (Non-existent ports are enforced at the environment layer, not here)
                return 0.0

            case [*results], port, sensor if port < len(results) and not is_dataclass(results):
                # Yielding a sequence of result types
                # will expose it to the port that corresponds to each index,
                # with unfilled ports defaulting to 0.
                results: Sequence[SensorPollResult]
                return self._lookup_port_state(results[port], port, sensor)

            case result, port, sensor if isinstance(result, SensorPollResult):
                # Yielding a type that's _not_ a sequence
                # will expose it to all ports.
                return self._lookup_port_state(result, port, sensor)

            case _, _, _:
                return 0.0

    def _lookup_port_state(self, result: SensorPollResult, port: int, sensor: Sensor) -> float:
        # The port's enabled state is handled by _get_sensor_input

        match result, port, sensor:
            # yielding None returns 0.0
            case None, _, _:
                return 0.0

            case PortInput() as port_input, _, _:
                port_input: PortInput
                # Recurse a little bit from the general sensor state into the specific device
                return self._lookup_port_state(port_input[sensor], port, sensor)

            # yielding a number returns it unconditionally
            case Real() as r, _, _:
                return float(r)

            # yielding a particular SensorState subclass will return the corresponding value for that sensor type
            case AccelerometerInput(x=x), _, Sensor.ACCELEROMETER_X:
                return float(x)
            case AccelerometerInput(y=y), _, Sensor.ACCELEROMETER_Y:
                return float(y)
            case AccelerometerInput(z=z), _, Sensor.ACCELEROMETER_Z:
                return float(z)

            case GyroscopeInput(x=x), _, Sensor.GYROSCOPE_X:
                return float(x)
            case GyroscopeInput(y=y), _, Sensor.GYROSCOPE_Y:
                return float(y)
            case GyroscopeInput(z=z), _, Sensor.GYROSCOPE_Z:
                return float(z)

            case IlluminanceInput(value=v), _, Sensor.ILLUMINANCE:
                return float(v)

            case Vector3(x=x), _, Sensor.ACCELEROMETER_X | Sensor.GYROSCOPE_X:
                return float(x)

            case Vector3(y=y), _, Sensor.ACCELEROMETER_Y | Sensor.GYROSCOPE_Y:
                return float(y)

            case Vector3(z=z), _, Sensor.ACCELEROMETER_Z | Sensor.GYROSCOPE_Z:
                return float(z)

            case _, _, _:
                raise TypeError(f"Unexpected result type: {type(result).__name__}")


__all__ = [
    "Vector3",
    "SensorState",
    "SensorInput",
    "AccelerometerInput",
    "GyroscopeInput",
    "IlluminanceInput",
    "PortInput",
    "SensorPollResult",
    "SensorStateIterator",
    "SensorStateIterable",
    "SensorStateGenerator",
    "IterableSensorDriver",
]
