from collections import defaultdict
from collections.abc import Callable, Iterator, MutableMapping, Sequence
from dataclasses import dataclass, field, is_dataclass
from numbers import Real
from typing import Literal, NamedTuple, overload

from libretro.api.sensor import Sensor, SensorAction, SensorType

from .interface import SensorInterface


class Vector3(NamedTuple):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass(slots=True)
class SensorState:
    enabled: bool = False
    rate: int = 0


@dataclass(slots=True)
class PortSensorState:
    accelerometer: SensorState = field(default_factory=SensorState)
    gyroscope: SensorState = field(default_factory=SensorState)
    illuminance: SensorState = field(default_factory=SensorState)

    @overload
    def __getitem__(self, item: SensorType) -> SensorState: ...

    @overload
    def __getitem__(self, item: SensorAction) -> bool: ...

    def __getitem__(self, item: SensorType | SensorAction) -> SensorState | bool:
        match item:
            case SensorType.ACCELEROMETER:
                return self.accelerometer
            case SensorType.GYROSCOPE:
                return self.gyroscope
            case SensorType.ILLUMINANCE:
                return self.illuminance
            case SensorAction.ACCELEROMETER_ENABLE:
                return self.accelerometer.enabled
            case SensorAction.GYROSCOPE_ENABLE:
                return self.gyroscope.enabled
            case SensorAction.ILLUMINANCE_ENABLE:
                return self.illuminance.enabled
            case SensorAction.ACCELEROMETER_DISABLE:
                return not self.accelerometer.enabled
            case SensorAction.GYROSCOPE_DISABLE:
                return not self.gyroscope.enabled
            case SensorAction.ILLUMINANCE_DISABLE:
                return not self.illuminance.enabled
            case _:
                raise TypeError(
                    f"Expected a SensorType or SensorAction, got {type(item).__name__}"
                )

    @overload
    def __setitem__(self, key: SensorType, value: SensorState): ...

    @overload
    def __setitem__(self, key: SensorAction, value: bool): ...

    def __setitem__(self, key: SensorType | SensorAction, value: SensorState | bool):
        match key, value:
            case SensorType.ACCELEROMETER, SensorState(s):
                self.accelerometer = SensorState(s.enabled, s.rate)
            case SensorType.GYROSCOPE, SensorState(s):
                self.gyroscope = SensorState(s.enabled, s.rate)
            case SensorType.ILLUMINANCE, SensorState(s):
                self.illuminance = SensorState(s.enabled, s.rate)
            case SensorAction.ACCELEROMETER_ENABLE, bool(value):
                self.accelerometer.enabled = value
            case SensorAction.GYROSCOPE_ENABLE, bool(value):
                self.gyroscope.enabled = value
            case SensorAction.ILLUMINANCE_ENABLE, bool(value):
                self.illuminance.enabled = value
            case SensorAction.ACCELEROMETER_DISABLE, bool(value):
                self.accelerometer.enabled = not value
            case SensorAction.GYROSCOPE_DISABLE, bool(value):
                self.gyroscope.enabled = not value
            case SensorAction.ILLUMINANCE_DISABLE, bool(value):
                self.illuminance.enabled = not value
            case (SensorType(k) | SensorAction(k)), _:
                raise TypeError(f"Cannot set {k} from {type(value).__name__}")
            case _, _:
                raise TypeError(f"Expected a SensorType or SensorAction, got {type(key).__name__}")


@dataclass(slots=True)
class PortState:
    accelerometer: SensorState = field(default_factory=SensorState)
    gyroscope: SensorState = field(default_factory=SensorState)
    illuminance: SensorState = field(default_factory=SensorState)

    @overload
    def __getitem__(self, item: SensorType) -> SensorState: ...

    @overload
    def __getitem__(self, item: SensorAction) -> bool: ...

    def __getitem__(self, item: SensorType | SensorAction) -> SensorState | bool:
        match item:
            case SensorType.ACCELEROMETER:
                return self.accelerometer
            case SensorType.GYROSCOPE:
                return self.gyroscope
            case SensorType.ILLUMINANCE:
                return self.illuminance
            case SensorAction.ACCELEROMETER_ENABLE:
                return self.accelerometer.enabled
            case SensorAction.GYROSCOPE_ENABLE:
                return self.gyroscope.enabled
            case SensorAction.ILLUMINANCE_ENABLE:
                return self.illuminance.enabled
            case SensorAction.ACCELEROMETER_DISABLE:
                return not self.accelerometer.enabled
            case SensorAction.GYROSCOPE_DISABLE:
                return not self.gyroscope.enabled
            case SensorAction.ILLUMINANCE_DISABLE:
                return not self.illuminance.enabled
            case _:
                raise TypeError(
                    f"Expected a SensorType or SensorAction, got {type(item).__name__}"
                )

    @overload
    def __setitem__(self, key: SensorType, value: SensorState): ...

    @overload
    def __setitem__(self, key: SensorAction, value: bool): ...

    def __setitem__(self, key: SensorType | SensorAction, value: SensorState | bool):
        match key, value:
            case SensorType.ACCELEROMETER, SensorState(s):
                self.accelerometer = SensorState(s.enabled, s.rate)
            case SensorType.GYROSCOPE, SensorState(s):
                self.gyroscope = SensorState(s.enabled, s.rate)
            case SensorType.ILLUMINANCE, SensorState(s):
                self.illuminance = SensorState(s.enabled, s.rate)
            case SensorAction.ACCELEROMETER_ENABLE, bool(value):
                self.accelerometer.enabled = value
            case SensorAction.GYROSCOPE_ENABLE, bool(value):
                self.gyroscope.enabled = value
            case SensorAction.ILLUMINANCE_ENABLE, bool(value):
                self.illuminance.enabled = value
            case SensorAction.ACCELEROMETER_DISABLE, bool(value):
                self.accelerometer.enabled = not value
            case SensorAction.GYROSCOPE_DISABLE, bool(value):
                self.gyroscope.enabled = not value
            case SensorAction.ILLUMINANCE_DISABLE, bool(value):
                self.illuminance.enabled = not value
            case (SensorType(k) | SensorAction(k)), _:
                raise TypeError(f"Cannot set {k} from {type(value).__name__}")
            case _, _:
                raise TypeError(f"Expected a SensorType or SensorAction, got {type(key).__name__}")


class SensorInput:
    pass


@dataclass(slots=True)
class AccelerometerInput(SensorInput):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass(slots=True)
class GyroscopeInput(SensorInput):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass(slots=True)
class IlluminanceInput(SensorInput):
    value: float = 0.0


@dataclass(slots=True)
class PortInput:
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


SensorPollResult = Real | PortInput | SensorInput | Vector3 | None
SensorInputIterator = Iterator[SensorPollResult | Sequence[SensorPollResult]]
SensorInputGenerator = Callable[[], SensorInputIterator]


class GeneratorSensorInterface(SensorInterface):
    def __init__(self, generator: SensorInputGenerator | None = None):
        self._generator = generator
        self._generator_state: SensorInputIterator | None = None
        self._last_poll_result: SensorPollResult = None
        self._sensor_state: defaultdict[int, PortState] = defaultdict(PortState)

    @property
    def sensor_state(self) -> MutableMapping[int, PortState]:
        return self._sensor_state

    def poll(self) -> None:
        if self._generator:
            if self._generator_state is None:
                self._generator_state = self._generator()

            self._last_poll_result = next(self._generator_state, None)

    def _set_sensor_state(self, port: int, action: SensorAction, rate: int) -> bool:
        sensor_type = action.sensor_type
        sensor = self._sensor_state[port][sensor_type]
        sensor.rate = rate
        sensor.enabled = action.enabled

        return True

    def _get_sensor_input(self, port: int, sensor: Sensor) -> float:
        if not self._generator:
            # An unassigned generator will default to 0
            return 0.0

        match (self._last_poll_result, port, sensor):
            case (None | [], _, _):
                # An empty result will default to 0
                return 0.0

            case _, _, _ if not self._sensor_state[port][sensor.type].enabled:
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
            case Real(r), _, _:
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
    "PortState",
    "SensorInput",
    "AccelerometerInput",
    "GyroscopeInput",
    "IlluminanceInput",
    "PortInput",
    "SensorPollResult",
    "SensorInputIterator",
    "SensorInputGenerator",
    "GeneratorSensorInterface",
]
