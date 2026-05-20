"""
Protocol definition and supporting types for the content-loading driver interface.

.. seealso::

    :mod:`libretro.api.content`
        Provides the game info types and content override structures that content drivers manage.
"""

from abc import abstractmethod
from collections.abc import Sequence
from contextlib import AbstractContextManager
from ctypes import Array
from dataclasses import dataclass
from typing import NamedTuple, Protocol, runtime_checkable

from libretro.api import (
    Content,
    SubsystemContent,
    Subsystems,
    retro_game_info,
    retro_game_info_ext,
    retro_subsystem_info,
    retro_system_content_info_override,
    retro_system_info,
)


@dataclass(frozen=True)
class ContentAttributes:
    """
    Resolved content-loading attributes for a single content file.

    These attributes are derived from the system info,
    per-extension overrides, and subsystem ROM descriptors.
    """

    block_extract: bool
    """If :obj:`True`, the frontend should not extract this content from an archive."""
    persistent_data: bool
    """If :obj:`True`, the content buffer must remain valid for the lifetime of the core."""
    need_fullpath: bool
    """If :obj:`True`, the core requires a filesystem path rather than an in-memory buffer."""
    required: bool
    """If :obj:`True`, the content file is mandatory and loading must fail without it."""


class LoadedContentFile(NamedTuple):
    """A single content file that has been loaded and prepared for the core."""

    info: retro_game_info
    """The :class:`~libretro.api.content.retro_game_info` passed to :c:func:`retro_load_game`."""
    info_ext: retro_game_info_ext | None
    """Extended game info, if the core opted in via ``RETRO_ENVIRONMENT_GET_GAME_INFO_EXT``."""


LoadedContent = tuple[retro_subsystem_info | None, Sequence[LoadedContentFile] | None]


class ContentError(RuntimeError):
    """
    Raised when content cannot be loaded due to a policy violation
    (e.g., the core requires content but none was provided).
    """


@runtime_checkable
class ContentDriver(Protocol):
    """
    Protocol for drivers that load content for the core.

    Manages content attributes, subsystem support, and extended game info.

    .. seealso::

        :mod:`libretro.api.content`
            The C game info types and content loading structures that implementations of this protocol handle.
    """

    @abstractmethod
    def load(
        self, content: Content | SubsystemContent | None
    ) -> AbstractContextManager[LoadedContent]:
        """
        Load all content files.

        :param content: May be one of the following:

            - :obj:`None`, which will result in no content being loaded.
            - A :class:`zipfile.Path` object representing a file within a ZIP archive.
            - A :class:`str` or a :class:`~os.PathLike` object representing a file path.
              The loaded content will not be part of a subsystem.
              If :attr:`.retro_system_info.need_fullpath` is :obj:`False`
              and no override for this extension defines :attr:`.ContentAttributes.need_fullpath` as :obj:`True`,
              the driver will load the content as a file.
              Otherwise, the path will be provided to the core without opening the file.
            - A :class:`bytes`, :class:`bytearray`, :class:`memoryview`, or :class:`Buffer` object that represents content data.
              The loaded content will be passed directly to the core without being set to a path.
            - A :class:`.retro_game_info` object, which will be passed to the core as-is.
            - A :class:`.SubsystemContent` object, which contains multiple content files that together form a subsystem.


        :raises FileNotFoundError: If ``content`` is a path to a non-existent file.
        :raises ContentError: If loading :obj:`None` and the core requires content,
            or if ``content`` is a :class:`.retro_game_info`
            whose attributes are inconsistent with
            :attr:`~.retro_system_info.need_fullpath` and :attr:`~.retro_system_info.block_extract`.
        :raises RuntimeError: If called before :attr:`system_info` is set.
        :return: A context manager that yields a tuple containing the subsystem info and a sequence of loaded content files.
            Non-persistent content files will be closed when the context manager exits.

        .. note::
            All files not marked as persistent will be closed when the context manager exits.
            The ones that are persistent will be closed when the driver is destroyed.
        """
        ...

    @property
    @abstractmethod
    def enable_extended_info(self) -> bool:
        """
        Whether to populate and expose :class:`~libretro.api.content.retro_game_info_ext`
        to the core via ``RETRO_ENVIRONMENT_GET_GAME_INFO_EXT``.
        """
        ...

    @property
    @abstractmethod
    def game_info_ext(self) -> Array[retro_game_info_ext] | None:
        """
        The most recently loaded extended game info array,
        or :obj:`None` if extended info is disabled or no content has been loaded.
        """
        ...

    @property
    @abstractmethod
    def system_info(self) -> retro_system_info | None:
        """
        The system info provided by the core.

        .. seealso::
            :meth:`.Core.get_system_info`
                The method that cores use to provide this information.
        """
        ...

    @system_info.setter
    @abstractmethod
    def system_info(self, info: retro_system_info) -> None:
        """:param info: The :class:`~libretro.api.content.retro_system_info` returned by the core."""
        ...

    @property
    @abstractmethod
    def overrides(self) -> Sequence[retro_system_content_info_override] | None:
        """Per-extension content-info overrides registered by the core."""
        ...

    @overrides.setter
    @abstractmethod
    def overrides(self, overrides: Sequence[retro_system_content_info_override]) -> None:
        """:param overrides: The content-info overrides provided by the core."""
        ...

    @property
    @abstractmethod
    def subsystem_info(self) -> Subsystems | None:
        """Subsystem descriptors registered by the core, or :obj:`None` if none were registered."""
        ...

    @subsystem_info.setter
    @abstractmethod
    def subsystem_info(self, subsystems: Sequence[retro_subsystem_info]) -> None:
        """:param subsystems: The subsystem descriptors provided by the core."""
        ...

    @property
    @abstractmethod
    def support_no_game(self) -> bool | None:
        """
        Whether the core supports being run without any content.

        :obj:`None` if the core has not called ``RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME``.
        """
        ...

    @support_no_game.setter
    @abstractmethod
    def support_no_game(self, support: bool) -> None:
        """:param support: Whether the core supports no-content mode."""
        ...


__all__ = [
    "ContentDriver",
    "ContentAttributes",
    "LoadedContentFile",
    "LoadedContent",
    "ContentError",
]
