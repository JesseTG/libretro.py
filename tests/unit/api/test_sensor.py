"""Unit tests for :mod:`libretro.api.sensor`."""

from __future__ import annotations

import copy

import pytest

from libretro.api import (
    Sensor,
    SensorAction,
    SensorType,
    retro_sensor_interface,
)


def test_retro_sensor_interface_default() -> None:
    iface = retro_sensor_interface()
    assert not iface.set_sensor_state
    assert not iface.get_sensor_input


def test_retro_sensor_interface_deepcopy() -> None:
    iface = retro_sensor_interface()
    dup = copy.deepcopy(iface)
    assert dup is not iface
    assert not dup.set_sensor_state


def test_sensor_action_enabled_property() -> None:
    assert SensorAction.ACCELEROMETER_ENABLE.enabled is True
    assert SensorAction.ACCELEROMETER_DISABLE.enabled is False
    assert SensorAction.GYROSCOPE_ENABLE.enabled is True
    assert SensorAction.GYROSCOPE_DISABLE.enabled is False
    assert SensorAction.ILLUMINANCE_ENABLE.enabled is True
    assert SensorAction.ILLUMINANCE_DISABLE.enabled is False


@pytest.mark.parametrize(
    ("action", "sensor"),
    [
        (SensorAction.ACCELEROMETER_ENABLE, SensorType.ACCELEROMETER),
        (SensorAction.ACCELEROMETER_DISABLE, SensorType.ACCELEROMETER),
        (SensorAction.GYROSCOPE_ENABLE, SensorType.GYROSCOPE),
        (SensorAction.GYROSCOPE_DISABLE, SensorType.GYROSCOPE),
        (SensorAction.ILLUMINANCE_ENABLE, SensorType.ILLUMINANCE),
        (SensorAction.ILLUMINANCE_DISABLE, SensorType.ILLUMINANCE),
    ],
)
def test_sensor_action_sensor_type(action: SensorAction, sensor: SensorType) -> None:
    assert action.sensor_type == sensor


@pytest.mark.parametrize(
    ("reading", "sensor_type"),
    [
        (Sensor.ACCELEROMETER_X, SensorType.ACCELEROMETER),
        (Sensor.ACCELEROMETER_Y, SensorType.ACCELEROMETER),
        (Sensor.ACCELEROMETER_Z, SensorType.ACCELEROMETER),
        (Sensor.GYROSCOPE_X, SensorType.GYROSCOPE),
        (Sensor.GYROSCOPE_Y, SensorType.GYROSCOPE),
        (Sensor.GYROSCOPE_Z, SensorType.GYROSCOPE),
        (Sensor.ILLUMINANCE, SensorType.ILLUMINANCE),
    ],
)
def test_sensor_reading_type(reading: Sensor, sensor_type: SensorType) -> None:
    assert reading.type == sensor_type
