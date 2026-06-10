"""Integration tests for the LED driver against the ``led_test`` sample core."""

from __future__ import annotations

from libretro.drivers import DictLedDriver
from libretro.session import Session

from .conftest import SampleCoreLoader


def test_dict_led_driver_records_states(load_core: SampleCoreLoader) -> None:
    """``led_test`` toggles LEDs 0 and 1 each frame; the driver records the latest state."""
    core = load_core("custom", "led_test")
    led = DictLedDriver()
    with Session(core, None, led=led) as session:
        for _ in range(4):
            session.run()

    # The core sets LED 0 high on even frames and LED 1 high on odd frames.
    # After running, both LEDs must have received a 0/1 state.
    assert led.get_led_state(0) in (0, 1)
    assert led.get_led_state(1) in (0, 1)
    # The two LEDs are driven in opposite phase, so they should differ on any
    # single frame; after an even number of frames LED 0 is high, LED 1 low.
    assert led.get_led_state(0) != led.get_led_state(1)
