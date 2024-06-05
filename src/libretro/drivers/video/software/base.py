from abc import ABC
from collections.abc import Set
from typing import final

from libretro._typing import override
from libretro.api.video.context import HardwareContext, retro_hw_render_callback
from libretro.api.video.render import retro_hw_render_interface
from libretro.error import UnsupportedEnvCall

from ..driver import VideoDriver

_EMPTY = frozenset((HardwareContext.NONE,))


class SoftwareVideoDriver(VideoDriver, ABC):
    """
    A base class for software-only video drivers.

    Provides common overrides that would be the same
    for all software-only drivers.
    """

    @property
    @override
    @final
    def supported_contexts(self) -> Set[HardwareContext]:
        """
        :return: A set containing only ``HardwareContext.NONE``.
        """
        return _EMPTY

    @property
    @override
    @final
    def active_context(self) -> HardwareContext:
        """
        :return: ``HardwareContext.NONE``.
        """
        return HardwareContext.NONE

    @property
    @override
    @final
    def preferred_context(self) -> HardwareContext | None:
        return HardwareContext.NONE

    @preferred_context.setter
    @override
    @final
    def preferred_context(self, context: HardwareContext) -> None:
        if context != HardwareContext.NONE:
            raise RuntimeError("Software-rendered drivers only support HardwareContext.NONE")

    @preferred_context.deleter
    @override
    @final
    def preferred_context(self) -> None:
        raise RuntimeError("Software-rendered drivers only support HardwareContext.NONE")

    @override
    @final
    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        """
        :return: ``None``, as software-rendered drivers don't need any hardware context.
        """
        return None

    @property
    @override
    @final
    def current_framebuffer(self) -> int | None:
        """
        :return: ``None``, as software-rendered drivers don't have a hardware framebuffer.
        """
        return None

    @override
    @final
    def get_proc_address(self, sym: bytes) -> int | None:
        """
        :return: ``None``, as software-rendered drivers don't have any hardware functions to call.
        """
        return None

    @property
    @override
    @final
    def can_dupe(self) -> bool | None:
        return True

    @can_dupe.setter
    @override
    @final
    def can_dupe(self, value: bool) -> None:
        raise RuntimeError("Software-rendered drivers always support frame duplication")

    @can_dupe.deleter
    @override
    @final
    def can_dupe(self) -> None:
        raise RuntimeError("Software-rendered drivers always support frame duplication")

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
    @override
    @final
    def shared_context(self, value: bool) -> None:
        # Software-rendered drivers don't need any hardware context
        raise UnsupportedEnvCall("Shared context is not supported")


__all__ = ["SoftwareVideoDriver"]
