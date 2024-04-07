from typing import override

from .driver import TimingDriver
from libretro.api.timing import retro_frame_time_callback, retro_fastforwarding_override, retro_throttle_state


class DefaultTimingDriver(TimingDriver):
    def __init__(self, throttle_state: retro_throttle_state | None = None, target_refresh_rate: float | None = 60.0):
        self._frame_time_callback: retro_frame_time_callback | None = None
        self._fastforwarding_override: retro_fastforwarding_override | None = None
        self._throttle_state: retro_throttle_state | None = None
        self._target_refresh_rate: float | None = target_refresh_rate

    @override
    def frame_time_callback(self) -> retro_frame_time_callback | None:
        return None

    @frame_time_callback.setter
    def frame_time_callback(self, value: retro_frame_time_callback | None) -> None:
        pass

    @property
    @override
    def fastforwarding_override(self) -> retro_fastforwarding_override | None:
        return None

    @property
    def throttle_state(self) -> retro_throttle_state | None:
        pass

    @property
    def target_refresh_rate(self) -> float | None:
        pass


__all__ = ['DefaultTimingDriver']
