import ctypes
from typing import *

from .core import Core
from ._libretro import *
from .defs import Rotation, PixelFormat, Language, EnvironmentCall
from .input import InputState
from .audio import AudioState
from .video import VideoState


class Environment:
    def __init__(
            self,
            core: Core | str | CDLL,
            audio: AudioState,
            input: InputState,
            video: VideoState,
            **kwargs
    ):
        if core is None:
            raise ValueError("Core cannot be None")

        if audio is None:
            raise ValueError("AudioState cannot be None")

        if input is None:
            raise ValueError("InputState cannot be None")

        if video is None:
            raise ValueError("VideoState cannot be None")

        if isinstance(core, Core):
            self._core = core
        else:
            self._core = Core(core)

        self._audio = audio
        self._input = input
        self._video = video
        self._overrides: Dict[int, Any] = {}

        self._rotation: Optional[Rotation] = Rotation.NONE
        self._overscan: Optional[bool] = False
        self._performance_level: Optional[int] = None
        self._username: Optional[str] = "libretro.py"
        self._system_directory = kwargs.get("system_directory", None)
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._input_descriptors: Sequence[retro_input_descriptor] = []
        self._support_no_game = False
        self._save_directory = kwargs.get("save_directory", None)
        self._language: Optional[Language] = None
        self._support_achievements = False

    @property
    def core(self) -> Core:
        return self._core

    @property
    def audio(self) -> AudioState:
        return self._audio

    @property
    def input(self) -> InputState:
        return self._input

    @property
    def video(self) -> VideoState:
        return self._video

    @property
    def rotation(self) -> Optional[Rotation]:
        return self._rotation

    @rotation.setter
    def rotation(self, value: Rotation):
        self._rotation = value

    @rotation.deleter
    def rotation(self):
        self._rotation = None

    @property
    def overscan(self) -> Optional[bool]:
        return self._overscan

    @overscan.setter
    def overscan(self, value: bool):
        self._overscan = value

    @overscan.deleter
    def overscan(self):
        self._overscan = None

    @property
    def performance_level(self) -> Optional[int]:
        return self._performance_level

    @performance_level.setter
    def performance_level(self, value: int):
        self._performance_level = value

    @performance_level.deleter
    def performance_level(self):
        self._performance_level = None

    @property
    def system_directory(self) -> Optional[str]:
        return self._system_directory

    @system_directory.setter
    def system_directory(self, value: str):
        self._system_directory = value

    @system_directory.deleter
    def system_directory(self):
        self._system_directory = None

    @property
    def pixel_format(self) -> PixelFormat:
        return self._pixel_format

    @pixel_format.setter
    def pixel_format(self, value: PixelFormat):
        self._pixel_format = value

    @pixel_format.deleter
    def pixel_format(self):
        self._pixel_format = PixelFormat.RGB1555

    @property
    def input_descriptors(self) -> Sequence[retro_input_descriptor]:
        return self._input_descriptors

    @input_descriptors.setter
    def input_descriptors(self, value: Sequence[retro_input_descriptor]):
        self._input_descriptors = list(value)

    @input_descriptors.deleter
    def input_descriptors(self):
        self._input_descriptors = None

    @property
    def support_no_game(self) -> bool:
        return self._support_no_game

    @support_no_game.setter
    def support_no_game(self, value: bool):
        self._support_no_game = value

    @support_no_game.deleter
    def support_no_game(self):
        self._support_no_game = False

    @property
    def save_directory(self) -> Optional[str]:
        return self._save_directory

    @save_directory.setter
    def save_directory(self, value: str):
        self._save_directory = value

    @save_directory.deleter
    def save_directory(self):
        self._save_directory = None

    @property
    def username(self) -> Optional[str]:
        return self._username

    @username.setter
    def username(self, value: str):
        self._username = value

    @username.deleter
    def username(self):
        self._username = None

    @property
    def language(self) -> Optional[Language]:
        return self._language

    @language.setter
    def language(self, value: Language):
        self._language = value

    @language.deleter
    def language(self):
        self._language = None

    def environment(self, cmd: int, data: c_void_p) -> bool:
        if cmd in self._overrides:
            return self._overrides[cmd](data)

        match cmd:
            case EnvironmentCall.SetRotation:
                if self._rotation is not None:
                    # If the rotation envcall isn't disabled...
                    ptr = cast(data, POINTER(c_uint))
                    self._rotation = Rotation(ptr.contents)
                    return True

            case EnvironmentCall.GetOverscan:
                if self._overscan is not None:
                    # If the overscan envcall isn't disabled...
                    ptr = cast(data, POINTER(c_bool))
                    ptr.contents = self._overscan
                    return True

            case EnvironmentCall.SetPerformanceLevel:
                if self._performance_level is not None:
                    # If the performance level envcall isn't disabled...
                    ptr = cast(data, POINTER(c_uint))
                    self._performance_level = ptr.contents
                    return True

            case EnvironmentCall.GetSystemDirectory:
                if self._system_directory is not None:
                    # If the system directory envcall isn't disabled...
                    ptr = cast(data, POINTER(c_char_p))
                    ptr.contents = self._system_directory.encode()
                    return True

            case EnvironmentCall.SetPixelFormat:
                ptr = cast(data, POINTER(enum_retro_pixel_format))
                self._pixel_format = PixelFormat(ptr.contents)
                return True

            case EnvironmentCall.SetInputDescriptors:
                if self._input_descriptors is not None:
                    # If the input descriptors envcall isn't disabled...
                    ptr = cast(data, POINTER(retro_input_descriptor))
                    self._input_descriptors = []
                    i = 0
                    while ptr[i].contents.description is not None:
                        self._input_descriptors.append(ptr[i].contents)
                        i += 1

                    return True

            case EnvironmentCall.SetSupportNoGame:
                if self._support_no_game is not None:
                    # If the no-content envcall isn't disabled...
                    ptr = cast(data, POINTER(c_bool))
                    self._support_no_game = ptr.contents
                    return True

        print(f"Unsupported environment call {cmd}")
        return False
