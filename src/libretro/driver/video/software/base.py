from abc import ABC
from collections.abc import Set
from typing import final, override

from ..driver import VideoDriver
from libretro.api.proc import retro_proc_address_t
from libretro.error import UnsupportedEnvCall
from libretro.api.video.render import retro_hw_render_interface
from libretro.api.video.context import retro_hw_render_callback, HardwareContext

_EMPTY = frozenset()


class AbstractSoftwareVideoDriver(VideoDriver, ABC):
    @final
    def init_callback(self, callback: retro_hw_render_callback) -> bool:
        # Software-rendered drivers don't need retro_hw_render_callback
        return False

    @property
    @override
    @final
    def supported_contexts(self) -> Set[HardwareContext]:
        return _EMPTY

    @property
    @override
    @final
    def active_context(self) -> HardwareContext | None:
        return None

    @property
    @final
    def can_dupe(self) -> bool:
        return True

    @final
    def get_hw_framebuffer(self) -> int:
        return 0

    @final
    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        return None

    @property
    @final
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        return None

    @property
    @override
    @final
    def shared_context(self) -> bool:
        return False

    @shared_context.setter
    @final
    def shared_context(self, value: bool) -> None:
        # Software-rendered drivers don't need any hardware context
        raise UnsupportedEnvCall("Shared context is not supported")

    @final
    def context_reset(self) -> None:
        # There's no context to reset
        pass

    @final
    def context_destroy(self) -> None:
        # There's no context to destroy
        pass


__all__ = ['AbstractSoftwareVideoDriver']
