"""Unit tests for :mod:`libretro.drivers.sensor.iterable`."""

from __future__ import annotations

from dataclasses import fields

from libretro.api import Port, Sensor, SensorAction
from libretro.drivers import IterableSensorDriver, PortInput, Vector3

ACCELEROMETER = Vector3(0.5, -0.25, 0.75)
GYROSCOPE = Vector3(1.0, -2.0, 3.0)


def _enable_all(driver: IterableSensorDriver, port: Port) -> None:
    for action in (
        SensorAction.ACCELEROMETER_ENABLE,
        SensorAction.GYROSCOPE_ENABLE,
        SensorAction.ILLUMINANCE_ENABLE,
    ):
        assert driver.set_sensor_state(port, action, 60)


def test_port_input_declares_every_reading_as_a_field() -> None:
    assert [f.name for f in fields(PortInput)] == ["accelerometer", "gyroscope", "illuminance"]


def test_port_input_defaults_to_zero() -> None:
    port_input = PortInput()
    assert port_input.accelerometer == Vector3()
    assert port_input.gyroscope == Vector3()
    assert port_input.illuminance == 0.0


def test_port_input_accepts_keywords() -> None:
    port_input = PortInput(accelerometer=ACCELEROMETER, gyroscope=GYROSCOPE, illuminance=400.0)
    assert port_input.accelerometer == ACCELEROMETER
    assert port_input.gyroscope == GYROSCOPE
    assert port_input.illuminance == 400.0


def test_port_input_accepts_positional_arguments() -> None:
    assert PortInput(ACCELEROMETER, GYROSCOPE, 400.0) == PortInput(
        accelerometer=ACCELEROMETER, gyroscope=GYROSCOPE, illuminance=400.0
    )


def test_port_input_indexes_by_sensor() -> None:
    port_input = PortInput(ACCELEROMETER, GYROSCOPE, 400.0)
    assert port_input[Sensor.ACCELEROMETER_X] == 0.5
    assert port_input[Sensor.ACCELEROMETER_Y] == -0.25
    assert port_input[Sensor.ACCELEROMETER_Z] == 0.75
    assert port_input[Sensor.GYROSCOPE_X] == 1.0
    assert port_input[Sensor.GYROSCOPE_Y] == -2.0
    assert port_input[Sensor.GYROSCOPE_Z] == 3.0
    assert port_input[Sensor.ILLUMINANCE] == 400.0


def test_driver_reports_port_input_readings() -> None:
    driver = IterableSensorDriver([PortInput(ACCELEROMETER, GYROSCOPE, 400.0)])
    _enable_all(driver, Port(0))
    driver.poll()

    readings = {sensor: driver.get_sensor_input(Port(0), sensor) for sensor in Sensor}
    assert readings == {
        Sensor.ACCELEROMETER_X: 0.5,
        Sensor.ACCELEROMETER_Y: -0.25,
        Sensor.ACCELEROMETER_Z: 0.75,
        Sensor.GYROSCOPE_X: 1.0,
        Sensor.GYROSCOPE_Y: -2.0,
        Sensor.GYROSCOPE_Z: 3.0,
        Sensor.ILLUMINANCE: 400.0,
    }


def test_driver_reports_each_port_its_own_port_input() -> None:
    other = Vector3(-1.0, -1.0, -1.0)
    driver = IterableSensorDriver([[PortInput(ACCELEROMETER), PortInput(other)]])
    _enable_all(driver, Port(0))
    _enable_all(driver, Port(1))
    driver.poll()

    assert driver.get_sensor_input(Port(0), Sensor.ACCELEROMETER_X) == 0.5
    assert driver.get_sensor_input(Port(1), Sensor.ACCELEROMETER_X) == -1.0


def test_driver_reports_zero_for_disabled_sensors() -> None:
    driver = IterableSensorDriver([PortInput(ACCELEROMETER, GYROSCOPE, 400.0)])
    assert driver.set_sensor_state(Port(0), SensorAction.ACCELEROMETER_ENABLE, 60)
    driver.poll()

    assert driver.get_sensor_input(Port(0), Sensor.ACCELEROMETER_X) == 0.5
    assert driver.get_sensor_input(Port(0), Sensor.GYROSCOPE_X) == 0.0
    assert driver.get_sensor_input(Port(0), Sensor.ILLUMINANCE) == 0.0
