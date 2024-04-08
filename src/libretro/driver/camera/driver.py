from typing import Protocol, runtime_checkable
from libretro.api.camera import *


@runtime_checkable
class CameraDriver(Protocol):
    pass


__all__ = ["CameraDriver"]