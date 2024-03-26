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

    @abstractmethod
    def get_rotation(self) -> Rotation: ...

    @abstractmethod
    def set_rotation(self, rotation: Rotation) -> bool: ...

    @property
    def rotation(self) -> Rotation:
        return self.get_rotation()

    @rotation.setter
    def rotation(self, rotation: Rotation) -> None:
        if not self.set_rotation(rotation):
            raise RuntimeError(f"Failed to set rotation to {rotation}")

    @property
    @abstractmethod
    def can_dupe(self) -> bool: ...

    @abstractmethod
    def get_pixel_format(self) -> PixelFormat: ...

    @abstractmethod
    def set_pixel_format(self, format: PixelFormat) -> bool: ...

    @property
    def pixel_format(self) -> PixelFormat:
        return self.get_pixel_format()

    @pixel_format.setter
    def pixel_format(self, format: PixelFormat) -> None:
        if not self.set_pixel_format(format):
            raise RuntimeError(f"Failed to set pixel format to {format}")

    @abstractmethod
    def get_hw_framebuffer(self) -> int: ...

    @abstractmethod
    def get_frame(self): ...

    @abstractmethod
    def get_frame_max(self): ...

    @abstractmethod
    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None: ...

    @abstractmethod
    def get_system_av_info(self) -> retro_system_av_info | None: ...

    @abstractmethod
    def set_system_av_info(self, av_info: retro_system_av_info) -> None: ...

    @property
    def system_av_info(self) -> retro_system_av_info | None:
        return self.get_system_av_info()

    @system_av_info.setter
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        self.set_system_av_info(av_info)

    @abstractmethod
    def set_geometry(self, geometry: retro_game_geometry) -> None: ...

    @abstractmethod
    def get_geometry(self) -> retro_game_geometry: ...

    @property
    def geometry(self) -> retro_game_geometry:
        return self.get_geometry()

    @geometry.setter
    def geometry(self, geometry: retro_game_geometry) -> None:
        self.set_geometry(geometry)

    @abstractmethod
    def get_software_framebuffer(self, width: int, height: int, flags: MemoryAccess) -> retro_framebuffer | None: ...

    @property
    @abstractmethod
    def hw_render_interface(self) -> retro_hw_render_interface | None: ...

    @abstractmethod
    def get_shared_context(self) -> bool: ...

    @abstractmethod
    def set_shared_context(self, value: bool) -> None: ...

    @property
    def shared_context(self) -> bool:
        return self.get_shared_context()

    @shared_context.setter
    def shared_context(self, value: bool) -> None:
        self.set_shared_context(value)

    @abstractmethod
    def context_reset(self) -> None: ...

    @abstractmethod
    def context_destroy(self) -> None: ...


__all__ = [
    'VideoDriver',
]
