from abc import abstractmethod
from ctypes import c_double, POINTER
from typing import Protocol, runtime_checkable, NamedTuple

from .defs import *

c_double_p = POINTER(c_double)


class Position(NamedTuple):
    latitude: float | None
    longitude: float | None
    horizontal_accuracy: float | None
    vertical_accuracy: float | None


@runtime_checkable
class LocationInterface(Protocol):
    @abstractmethod
    def __init__(self):
        self._as_parameter_ = retro_location_callback()
        self._as_parameter_.start = retro_location_start_t(self.start)
        self._as_parameter_.stop = retro_location_stop_t(self.stop)
        self._as_parameter_.get_position = retro_location_get_position_t(self.__get_position)
        self._as_parameter_.set_interval = retro_location_set_interval_t(self.set_interval)

    @abstractmethod
    def start(self) -> bool: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def get_position(self) -> Position | None: ...

    @abstractmethod
    def set_interval(self, interval: int, distance: int) -> None: ...

    @property
    def initialized(self) -> retro_location_lifetime_status_t:
        return self._as_parameter_.initialized

    @initialized.setter
    def initialized(self, value: retro_location_lifetime_status_t) -> None:
        if value is not None and not isinstance(value, retro_location_lifetime_status_t):
            raise TypeError(f"expected retro_location_lifetime_status_t or None, got {type(value).__name__}")

        self._as_parameter_.initialized = value

    @initialized.deleter
    def initialized(self) -> None:
        self._as_parameter_.initialized = None

    @property
    def deinitialized(self) -> retro_location_lifetime_status_t:
        return self._as_parameter_.deinitialized

    @deinitialized.setter
    def deinitialized(self, value: retro_location_lifetime_status_t) -> None:
        if value is not None and not isinstance(value, retro_location_lifetime_status_t):
            raise TypeError(f"expected retro_location_lifetime_status_t or None, got {type(value).__name__}")

        self._as_parameter_.deinitialized = value

    @deinitialized.deleter
    def deinitialized(self) -> None:
        self._as_parameter_.deinitialized = None

    def __get_position(self, lat: c_double_p, lon: c_double_p, horiz_accuracy: c_double_p, vert_accuracy: c_double_p) -> bool:
        if not lat:
            raise ValueError("latitude pointer cannot be None")

        if not lon:
            raise ValueError("longitude pointer cannot be None")

        if not horiz_accuracy:
            raise ValueError("horiz_accuracy pointer cannot be None")

        if not vert_accuracy:
            raise ValueError("vert_accuracy pointer cannot be None")

        match self.get_position():
            case None:
                return False
            case (latitude, longitude, horizontal_accuracy, vertical_accuracy):
                lat[0] = latitude or 0.0
                lon[0] = longitude or 0.0
                horiz_accuracy[0] = horizontal_accuracy or 0.0
                vert_accuracy[0] = vertical_accuracy or 0.0
                return True
            case e:
                raise TypeError(f"expected Position or None, got {type(e).__name__}")


__all__ = [
    'LocationInterface',
    'Position',
]
