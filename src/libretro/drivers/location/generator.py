from collections.abc import Callable, Iterator

from .driver import LocationDriver, Position

LocationInputIterator = Iterator[Position | None]
LocationInputGenerator = Callable[[], LocationInputIterator]


class GeneratorLocationDriver(LocationDriver):
    def __init__(self, generator: LocationInputGenerator | None = None):
        super().__init__()
        self._generator = generator
        self._generator_state: LocationInputIterator | None = None
        self._active = False
        self._interval = 0
        self._distance = 0

    def start(self) -> bool:
        self._active = True
        return True

    def stop(self) -> None:
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        if value:
            self.start()
        else:
            self.stop()

    def get_position(self) -> Position | None:
        if not self._active:
            return None

        if not self._generator_state:
            self._generator_state = self._generator()

        try:
            match next(self._generator_state, None):
                case None:
                    return None
                case Position() as pos:
                    return pos
                case e:
                    raise TypeError(f"expected Position or None, got {type(e).__name__}")
        except StopIteration:
            return None

    def set_interval(self, interval: int, distance: int) -> None:
        self._interval = interval
        self._distance = distance

    @property
    def interval(self) -> int:
        return self._interval

    @property
    def distance(self) -> int:
        return self._distance


__all__ = ["GeneratorLocationDriver", "LocationInputGenerator", "LocationInputIterator"]
