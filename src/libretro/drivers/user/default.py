"""
A user driver with configurable username and language.

.. seealso::

    :mod:`libretro.api.user`
        Defines the language and username types this driver supplies.
"""

from typing import override

from libretro.api.user import Language

from .driver import UserDriver


class DefaultUserDriver(UserDriver):
    """A :class:`.UserDriver` with configurable username and language."""

    def __init__(
        self,
        username: str | bytes | None = "libretro.py",
        language: Language | None = Language.ENGLISH,
    ):
        """
        :param username: The player username to expose to cores.
            :class:`str` values are encoded to :class:`bytes` via UTF-8.
            :obj:`None` disables ``RETRO_ENVIRONMENT_GET_USERNAME``.
        :param language: The UI language to expose to cores.
            Defaults to :attr:`~libretro.api.user.Language.ENGLISH`.
        :raises TypeError: If either argument is not of the expected type.
        """
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
