"""Unit tests for :mod:`libretro.api.power`."""

from __future__ import annotations

import copy

from libretro.api import NO_ESTIMATE, PowerState, retro_device_power


def test_retro_device_power_kwarg_init() -> None:
    power = retro_device_power(state=PowerState.CHARGING, seconds=1800, percent=75)
    assert power.state == PowerState.CHARGING
    assert power.seconds == 1800
    assert power.percent == 75


def test_retro_device_power_no_estimate_sentinel() -> None:
    power = retro_device_power(state=PowerState.UNKNOWN, seconds=NO_ESTIMATE, percent=NO_ESTIMATE)
    assert power.seconds == NO_ESTIMATE
    assert power.percent == NO_ESTIMATE


def test_retro_device_power_deepcopy() -> None:
    power = retro_device_power(state=PowerState.CHARGED, seconds=0, percent=100)
    dup = copy.deepcopy(power)
    assert dup is not power
    assert dup.state == power.state
    assert dup.seconds == power.seconds
    assert dup.percent == power.percent


def test_power_state_enum_values() -> None:
    assert PowerState.UNKNOWN.value == 0
    assert PowerState.DISCHARGING.value == 1
    assert PowerState.CHARGING.value == 2
    assert PowerState.CHARGED.value == 3
    assert PowerState.PLUGGED_IN.value == 4
