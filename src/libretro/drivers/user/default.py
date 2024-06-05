from libretro._typing import override
from libretro.api.user import Language

from .driver import UserDriver


class DefaultUserDriver(UserDriver):
    def __init__(
        self,
        username: str | bytes | None = "libretro.py",
        language: Language | None = Language.ENGLISH,
    ):
        self.username = username
        self.language = Language(language)

    @property
    @override
    def username(self) -> bytes | None:
        return self._username

    @username.setter
    def username(self, username: str | bytes | None) -> None:
        match username:
            case None:
                self._username: bytes | None = None
            case str():
                self._username: bytes | None = username.encode()
            case bytes():
                self._username: bytes | None = username
            case _:
                raise TypeError(f"Expected str, bytes, or None, got {type(username).__name__}")

    @username.deleter
    def username(self) -> None:
        self._username = None

    @property
    @override
    def language(self) -> Language | None:
        return self._language

    @language.setter
    def language(self, language: Language | None) -> None:
        if not isinstance(language, (Language, int, type(None))):
            raise TypeError(f"Expected Language or int or None, got {type(language).__name__}")

        self._language = Language(language)

    @language.deleter
    def language(self) -> None:
        self._language = None


__all__ = ["DefaultUserDriver"]
