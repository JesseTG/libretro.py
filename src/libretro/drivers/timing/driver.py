"""
:class:`~typing.Protocol` definition for frame and audio timing drivers.

.. seealso::

    :mod:`libretro.api.timing`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.timing import (
    retro_fastforwarding_override,
    retro_frame_time_callback,
    retro_throttle_state,
)


@runtime_checkable
class TimingDriver(Protocol):
    """
    Protocol for drivers that expose frame and audio timing information to a core.

    .. seealso::

        :mod:`libretro.api.timing`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @property
    @abstractmethod
    def frame_time_callback(self) -> retro_frame_time_callback | None:
        """
        The frame-time callback registered by the core, if any.

        Set via ``RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK``.
        :obj:`None` if the core has not registered one.

        :param value: The frame-time callback to register.
        :raises UnsupportedEnvCall: If this driver does not support the frame-time callback.

        .. seealso::

            :class:`~libretro.api.timing.retro_frame_time_callback`
                The C struct registered by the core that contains this callback.
        """
        ...

    @frame_time_callback.setter
    @abstractmethod
    def frame_time_callback(self, value: retro_frame_time_callback) -> None:
        """See :attr:`frame_time_callback`."""
        ...

    def frame_time(self, time: int | None) -> None:
        """
        Invoke the registered :attr:`frame_time_callback`, if any.

        :param time: Microseconds elapsed since the previous frame,
            or :obj:`None` to use the callback's configured reference time.
        """
        callback = self.frame_time_callback
        if callback:
            callback(time if time is not None else callback.reference)

    @property
    @abstractmethod
    def fastforwarding_override(self) -> retro_fastforwarding_override | None:
        """
        The fast-forward override requested by the core, if any.

        Set via ``RETRO_ENVIRONMENT_SET_FASTFORWARDING_OVERRIDE``.

        :param value: The fast-forward override to register.
        :raises UnsupportedEnvCall: If this driver does not support fast-forward overrides.

        .. seealso::

            :class:`~libretro.api.timing.retro_fastforwarding_override`
                The C struct describing the override.
        """
        ...

    @fastforwarding_override.setter
    @abstractmethod
    def fastforwarding_override(self, value: retro_fastforwarding_override) -> None:
        """See :attr:`fastforwarding_override`."""
        ...

    @property
    @abstractmethod
    def throttle_state(self) -> retro_throttle_state | None:
        """
        The current throttle state reported to the core.

        Returned to the core in response to ``RETRO_ENVIRONMENT_GET_THROTTLE_STATE``.

        :param value: The throttle state to report.
        :raises UnsupportedEnvCall: If this driver does not report a throttle state.

        .. seealso::

            :class:`~libretro.api.timing.retro_throttle_state`
                The C struct describing the throttle state.
        """
        ...

    @throttle_state.setter
    @abstractmethod
    def throttle_state(self, value: retro_throttle_state) -> None:
        """See :attr:`throttle_state`."""
        ...

    @throttle_state.deleter
    @abstractmethod
    def throttle_state(self) -> None:
        """See :attr:`throttle_state`."""
        ...

    @property
    @abstractmethod
    def target_refresh_rate(self) -> float | None:
        """
        The frontend's target refresh rate in Hz, if any.

        Returned to the core in response to ``RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE``.
        :obj:`None` if no target refresh rate is configured.

        :param value: The target refresh rate in Hz.
        :raises UnsupportedEnvCall: If this driver does not report a target refresh rate.
        """
        ...

    @target_refresh_rate.setter
    @abstractmethod
    def target_refresh_rate(self, value: float) -> None:
        """See :attr:`target_refresh_rate`."""
        ...

    @target_refresh_rate.deleter
    @abstractmethod
    def target_refresh_rate(self) -> None:
        """See :attr:`target_refresh_rate`."""
        ...


__all__ = ["TimingDriver"]
