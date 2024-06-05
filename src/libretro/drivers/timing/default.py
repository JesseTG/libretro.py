from libretro._typing import override
from libretro.api.timing import (
    retro_fastforwarding_override,
    retro_frame_time_callback,
    retro_throttle_state,
)

from .driver import TimingDriver


class DefaultTimingDriver(TimingDriver):
    def __init__(
        self,
        throttle_state: retro_throttle_state | None = None,
        target_refresh_rate: float | None = 60.0,
    ):
        if not isinstance(throttle_state, retro_throttle_state) and throttle_state is not None:
            raise TypeError(
                f"throttle_state must be a retro_throttle_state or None, not {type(throttle_state).__name__}"
            )

        if not isinstance(target_refresh_rate, float) and target_refresh_rate is not None:
            raise TypeError(
                f"target_refresh_rate must be a float or None, not {type(target_refresh_rate).__name__}"
            )

        self._frame_time_callback: retro_frame_time_callback | None = None
        self._fastforwarding_override: retro_fastforwarding_override | None = None
        self._throttle_state: retro_throttle_state | None = throttle_state
        self._target_refresh_rate: float | None = target_refresh_rate

    @property
    @override
    def frame_time_callback(self) -> retro_frame_time_callback | None:
        return self._frame_time_callback

    @frame_time_callback.setter
    @override
    def frame_time_callback(self, value: retro_frame_time_callback) -> None:
        if not isinstance(value, retro_frame_time_callback):
            raise TypeError(
                f"value must be a retro_frame_time_callback, not {type(value).__name__}"
            )

        self._frame_time_callback = value

    @property
    @override
    def fastforwarding_override(self) -> retro_fastforwarding_override | None:
        return self._fastforwarding_override

    @fastforwarding_override.setter
    @override
    def fastforwarding_override(self, value: retro_fastforwarding_override) -> None:
        if not isinstance(value, retro_fastforwarding_override):
            raise TypeError(
                f"value must be a retro_fastforwarding_override, not {type(value).__name__}"
            )

        self._fastforwarding_override = value

    @property
    @override
    def throttle_state(self) -> retro_throttle_state | None:
        return self._throttle_state

    @throttle_state.setter
    @override
    def throttle_state(self, value: retro_throttle_state) -> None:
        if not isinstance(value, retro_throttle_state):
            raise TypeError(f"value must be a retro_throttle_state, not {type(value).__name__}")

        self._throttle_state = value

    @throttle_state.deleter
    @override
    def throttle_state(self) -> None:
        self._throttle_state = None

    @property
    @override
    def target_refresh_rate(self) -> float | None:
        return self._target_refresh_rate

    @target_refresh_rate.setter
    @override
    def target_refresh_rate(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError(f"value must be a float, not {type(value).__name__}")

        self._target_refresh_rate = value

    @target_refresh_rate.deleter
    @override
    def target_refresh_rate(self) -> None:
        self._target_refresh_rate = None


__all__ = ["DefaultTimingDriver"]
