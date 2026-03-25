from abc import ABC
from collections.abc import Set
from typing import Literal, final, override

from libretro.api.video.context import HardwareContext, retro_hw_render_callback
from libretro.api.video.render import retro_hw_render_interface

from ..driver import UnsupportedContextError, VideoDriver

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
    def supported_contexts(self) -> Set[Literal[HardwareContext.NONE]]:
        """
        :return: A set containing only ``HardwareContext.NONE``.
        """
        return _EMPTY

    @property
    @override
    @final
    def active_context(self) -> Literal[HardwareContext.NONE]:
        """
        :return: ``HardwareContext.NONE``.
        """
        return HardwareContext.NONE

    @property
    @override
    @final
    def preferred_context(self) -> Literal[HardwareContext.NONE]:
        return HardwareContext.NONE

    @override
    @final
    def set_context(self, callback: retro_hw_render_callback) -> None:
        """
        No-op if the context type is ``HardwareContext.NONE``; raises a RuntimeError otherwise.
        """
        if callback.context_type != HardwareContext.NONE:
            raise UnsupportedContextError(
                "Software-rendered drivers only support HardwareContext.NONE"
            )

    @property
    @override
    @final
    def current_framebuffer(self) -> None:
        """
        :return: ``None``, as software-rendered drivers don't have a hardware framebuffer.
        """
        return None

    @override
    @final
    def get_proc_address(self, sym: bytes) -> None:
        """
        :return: ``None``, as software-rendered drivers don't have any hardware functions to call.
        """
        return None

    @property
    @override
    @final
    def can_dupe(self) -> bool | None:
        return True

    @property
    @override
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
        raise NotImplementedError("Shared context is not supported by software-rendered drivers")


__all__ = ["SoftwareVideoDriver"]
