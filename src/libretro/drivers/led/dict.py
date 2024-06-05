from libretro._typing import override

from .driver import LedDriver


class DictLedDriver(LedDriver):
    def __init__(self):
        super().__init__()
        self._leds: dict[int, int] = {}

    @override
    def set_led_state(self, led: int, state: int) -> None:
        self._leds[led] = state

    @override
    def get_led_state(self, led: int) -> int:
        return self._leds.get(led, 0)


__all__ = ["DictLedDriver"]
