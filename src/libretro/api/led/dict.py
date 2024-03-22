from .interface import LedInterface


class DictLedInterface(LedInterface):
    def __init__(self):
        super().__init__()
        self._leds: dict[int, int] = {}

    def set_led_state(self, led: int, state: int) -> None:
        self._leds[led] = state

    def __getitem__(self, item):
        return self._leds.get(item, 0)


__all__ = ['DictLedInterface']