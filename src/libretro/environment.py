from typing import *

from ._libretro import *
from .defs import Rotation, PixelFormat, Language


class Environment:
    def __init__(self, **kwargs):
        self._username: Optional[str] = "libretro.py"
        self._rotation: Rotation = Rotation.NONE
        self._system_directory = kwargs.get("system_directory", None)
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._support_no_game = False
        self._save_directory = kwargs.get("save_directory", None)
        self._language: Optional[Language] = None
        self._support_achievements = False


    def __call__(self, cmd: int, data: c_void_p) -> bool:
        # TODO: Implement
        pass

    @property
    def rotation(self) -> Rotation:
        return self._rotation

    @rotation.setter
    def rotation(self, value: Rotation):
        self._rotation = value

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