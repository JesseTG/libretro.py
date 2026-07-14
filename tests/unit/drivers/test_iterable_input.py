"""
Unit tests for :class:`libretro.drivers.input.iterable.IterableInputDriver`.

These tests focus on the *callable* form of the driver's input source
(``InputStateGenerator = Callable[[], InputStateIterator]``):
a zero-argument callable that, when invoked, yields per-frame poll results.
Every yielded result flows through the ``isinstance(result, InputPollResult)``
check in :meth:`IterableInputDriver.state`, which regressed on Python 3.13
when ``DeviceState`` was declared with a ``type`` alias (see issue #28).
"""

from __future__ import annotations

from collections.abc import Iterator

from libretro.api.input import (
    DeviceIdJoypad,
    InputDevice,
    InputDeviceFlag,
    JoypadState,
)
from libretro.api.input.device import Port
from libretro.drivers.input.iterable import (
    InputPollResult,
    IterableInputDriver,
    PortState,
)


def test_input_poll_result_is_usable_with_isinstance() -> None:
    """``InputPollResult`` must remain a runtime-checkable union (regression for issue #28)."""
    # A ``type`` alias member would make this raise ``TypeError``.
    assert isinstance(42, InputPollResult)
    assert isinstance(True, InputPollResult)
    assert isinstance(None, InputPollResult)
    assert isinstance(JoypadState(), InputPollResult)
    assert isinstance(PortState(), InputPollResult)
    assert not isinstance(1.5, InputPollResult)


def test_callable_source_is_invoked_lazily() -> None:
    """The callable source is not called until the first :meth:`poll`."""
    calls = 0

    def source() -> Iterator[int]:
        nonlocal calls
        calls += 1
        yield 1

    driver = IterableInputDriver(source)
    assert calls == 0, "Constructing the driver must not invoke the source"

    driver.poll()
    assert calls == 1, "The first poll must invoke the source exactly once"

    driver.poll()
    assert calls == 1, "Subsequent polls must not re-invoke the source"


def test_callable_source_scalar_is_exposed_to_all_ports() -> None:
    """A scalar yielded by the callable is returned verbatim for every port and id."""

    def source() -> Iterator[int]:
        yield 42

    driver = IterableInputDriver(source)
    driver.poll()

    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 42
    assert driver.state(Port(3), InputDevice.JOYPAD, 0, DeviceIdJoypad.B) == 42


def test_callable_source_bool_is_coerced_to_int() -> None:
    """A yielded ``bool`` is exposed as its integer value."""

    def source() -> Iterator[bool]:
        yield True
        yield False

    driver = IterableInputDriver(source)

    driver.poll()
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 1

    driver.poll()
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0


def test_callable_source_none_yields_zero() -> None:
    """A yielded ``None`` produces 0 for all queries."""

    def source() -> Iterator[None]:
        yield None

    driver = IterableInputDriver(source)
    driver.poll()
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0


def test_callable_source_device_state_is_exposed_to_all_ports() -> None:
    """A single ``JoypadState`` yielded by the callable is exposed to every port."""

    def source() -> Iterator[JoypadState]:
        yield JoypadState(a=True)

    driver = IterableInputDriver(source)
    driver.poll()

    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 1
    assert driver.state(Port(1), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 1
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.B) == 0


def test_callable_source_sequence_maps_to_ports_by_index() -> None:
    """A sequence yielded by the callable maps each element to the port at its index."""

    def source() -> Iterator[list[JoypadState]]:
        yield [JoypadState(b=True), JoypadState(y=True)]

    driver = IterableInputDriver(source)
    driver.poll()

    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.B) == 1
    assert driver.state(Port(1), InputDevice.JOYPAD, 0, DeviceIdJoypad.Y) == 1
    # Cross-port lookups default to 0.
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.Y) == 0
    # A port beyond the sequence length defaults to 0.
    assert driver.state(Port(2), InputDevice.JOYPAD, 0, DeviceIdJoypad.B) == 0


def test_callable_source_port_state_routes_by_device() -> None:
    """A yielded ``PortState`` routes each device query to its matching sub-state."""

    def source() -> Iterator[PortState]:
        yield PortState(joypad=JoypadState(start=True))

    driver = IterableInputDriver(source)
    driver.poll()

    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.START) == 1
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0
    # A device the PortState leaves unset defaults to 0.
    assert driver.state(Port(0), InputDevice.MOUSE, 0, 0) == 0


def test_callable_source_advances_one_step_per_poll() -> None:
    """Each :meth:`poll` advances exactly one step through the callable's iterator."""

    def source() -> Iterator[int]:
        yield 1
        yield 2
        yield 3

    driver = IterableInputDriver(source)

    for expected in (1, 2, 3):
        driver.poll()
        assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == expected


def test_callable_source_defaults_to_zero_when_exhausted() -> None:
    """Once the callable's iterator is exhausted, all queries default to 0."""

    def source() -> Iterator[int]:
        yield 7

    driver = IterableInputDriver(source)

    driver.poll()
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 7

    driver.poll()  # Iterator exhausted; poll result becomes None.
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0


def test_callable_source_out_of_range_port_defaults_to_zero() -> None:
    """Ports at or beyond ``max_users`` default to 0 even for a scalar result."""

    def source() -> Iterator[int]:
        yield 99

    driver = IterableInputDriver(source, max_users=2)
    driver.poll()

    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 99
    assert driver.state(Port(2), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0


def test_callable_source_respects_device_capabilities() -> None:
    """A device excluded from ``device_capabilities`` defaults to 0."""

    def source() -> Iterator[JoypadState]:
        yield JoypadState(a=True)

    driver = IterableInputDriver(source, device_capabilities=InputDeviceFlag.JOYPAD)
    driver.poll()

    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 1
    # The joypad state carries no mouse data, and the mouse device is not enabled anyway.
    assert driver.state(Port(0), InputDevice.MOUSE, 0, 0) == 0


def test_callable_source_empty_sequence_yields_zero() -> None:
    """An empty sequence yielded by the callable produces 0 for all queries."""

    def source() -> Iterator[list[JoypadState]]:
        yield []

    driver = IterableInputDriver(source)
    driver.poll()
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0


def test_empty_iterable_source_defaults_to_zero() -> None:
    """An iterable that yields nothing leaves every query at 0 without error."""
    driver = IterableInputDriver(())
    driver.poll()
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0


def test_empty_callable_iterable_defaults_to_zero() -> None:
    """A callable that returns an iterable that yields nothing leaves every query at 0 without error."""
    driver = IterableInputDriver(lambda: (x for x in ()))
    driver.poll()
    assert driver.state(Port(0), InputDevice.JOYPAD, 0, DeviceIdJoypad.A) == 0
