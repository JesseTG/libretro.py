from abc import abstractmethod
from ctypes import c_void_p
from typing import Protocol, runtime_checkable

from ..render.defs import retro_hw_render_interface
from ..context.defs import retro_hw_render_callback
from ..defs import Rotation, PixelFormat, MemoryAccess, retro_framebuffer
from ...av.defs import retro_game_geometry, retro_system_av_info
from ...proc import retro_proc_address_t
from ...._utils import memoryview_at


@runtime_checkable
class VideoDriver(Protocol):
    def refresh(self, data: c_void_p, width: int, height: int, pitch: int) -> None:
        if data:
            view = memoryview_at(data, pitch * height, readonly=True)
            assert len(view) == pitch * height, f"Expected view to have {pitch * height} bytes, got {len(view)} bytes"
            self._refresh(view, width, height, pitch)
        else:
            self._refresh(None, width, height, pitch)

    @abstractmethod
    def _refresh(self, data: memoryview | None, width: int, height: int, pitch: int) -> None: ...

    @abstractmethod
    def init_callback(self, callback: retro_hw_render_callback) -> bool: ...

    @property
    @abstractmethod
    def rotation(self) -> Rotation: ...

    @rotation.setter
    @abstractmethod
    def rotation(self, rotation: Rotation) -> None: ...

    @property
    @abstractmethod
    def can_dupe(self) -> bool: ...

    @property
    @abstractmethod
    def pixel_format(self) -> PixelFormat: ...

    @pixel_format.setter
    @abstractmethod
    def pixel_format(self, format: PixelFormat) -> None: ...

    @abstractmethod
    def get_hw_framebuffer(self) -> int: ...

    @property
    @abstractmethod
    def frame(self): ...

    @property
    @abstractmethod
    def frame_max(self): ...

    @abstractmethod
    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None: ...

    @property
    @abstractmethod
    def system_av_info(self) -> retro_system_av_info | None: ...

    @system_av_info.setter
    @abstractmethod
    def system_av_info(self, av_info: retro_system_av_info) -> None: ...

    @property
    @abstractmethod
    def geometry(self) -> retro_game_geometry: ...

    @geometry.setter
    @abstractmethod
    def geometry(self, geometry: retro_game_geometry) -> None: ...

    @abstractmethod
    def get_software_framebuffer(self, width: int, height: int, flags: MemoryAccess) -> retro_framebuffer | None: ...

    @property
    @abstractmethod
    def hw_render_interface(self) -> retro_hw_render_interface | None: ...

    @property
    @abstractmethod
    def shared_context(self) -> bool: ...

    @shared_context.setter
    @abstractmethod
    def shared_context(self, value: bool) -> None: ...

    @abstractmethod
    def context_reset(self) -> None: ...

    @abstractmethod
    def context_destroy(self) -> None: ...


__all__ = [
    'VideoDriver',
]
