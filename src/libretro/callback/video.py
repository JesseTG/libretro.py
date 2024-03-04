from abc import abstractmethod
from ctypes import *
from typing import Protocol


class VideoCallbacks(Protocol):
    @abstractmethod
    def refresh(self, data: c_void_p, width: c_uint, height: c_uint, pitch: c_size_t): ...


class VideoState(VideoCallbacks):
    pass