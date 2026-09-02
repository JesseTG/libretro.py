"""Unit tests for :mod:`libretro.drivers.rumble`."""

from __future__ import annotations

from libretro.api import Port, RumbleEffect
from libretro.drivers import DictRumbleDriver, RecordingRumbleDriver, RumbleCall


def test_dict_driver_defaults_to_silence() -> None:
    driver = DictRumbleDriver()
    state = driver[Port(0)]
    assert state.strong == 0
    assert state.weak == 0


def test_dict_driver_tracks_motors_independently() -> None:
    driver = DictRumbleDriver()
    assert driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 100)
    assert driver.set_rumble_state(Port(0), RumbleEffect.WEAK, 200)

    state = driver[Port(0)]
    assert state.strong == 100
    assert state.weak == 200


def test_dict_driver_setting_one_motor_leaves_the_other_alone() -> None:
    driver = DictRumbleDriver()
    driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 0xFFFF)
    driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 0)

    state = driver[Port(0)]
    assert state.strong == 0
    assert state.weak == 0


def test_dict_driver_keeps_ports_separate() -> None:
    driver = DictRumbleDriver()
    driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 100)
    driver.set_rumble_state(Port(1), RumbleEffect.WEAK, 200)

    assert driver[Port(0)].strong == 100
    assert driver[Port(0)].weak == 0
    assert driver[Port(1)].strong == 0
    assert driver[Port(1)].weak == 200


def test_recording_driver_logs_every_call() -> None:
    driver = RecordingRumbleDriver()
    driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 100)
    driver.set_rumble_state(Port(0), RumbleEffect.WEAK, 200)
    driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 100)

    assert list(driver.calls) == [
        RumbleCall(Port(0), RumbleEffect.STRONG, 100),
        RumbleCall(Port(0), RumbleEffect.WEAK, 200),
        RumbleCall(Port(0), RumbleEffect.STRONG, 100),
    ]


def test_recording_driver_still_tracks_state() -> None:
    driver = RecordingRumbleDriver()
    driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 100)
    driver.set_rumble_state(Port(0), RumbleEffect.WEAK, 200)

    state = driver[Port(0)]
    assert state.strong == 100
    assert state.weak == 200


def test_recording_driver_clear_drops_the_log_but_not_the_state() -> None:
    driver = RecordingRumbleDriver()
    driver.set_rumble_state(Port(0), RumbleEffect.STRONG, 100)
    driver.clear()

    assert not driver.calls
    assert driver[Port(0)].strong == 100
