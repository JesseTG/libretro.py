"""Types and callbacks for using the emulated system's disk drives, if any."""

from ctypes import Structure, c_bool, c_size_t, c_uint
from dataclasses import dataclass
from typing import override

from libretro.api._utils import NullPointerToNoneMixin
from libretro.api.content import retro_game_info
from libretro.ctypes import (
    CBoolArg,
    CIntArg,
    CStringArg,
    TypedFunctionPointer,
    TypedPointer,
)

retro_set_eject_state_t = TypedFunctionPointer[c_bool, [CBoolArg]]
"""
Open or close the emulated console's virtual disk tray.

Registered by the :term:`core` and called by the :term:`frontend`
to swap the disk image currently inserted in the emulated drive.
The frontend may only change the disk image index while the tray is open.

:param ejected: :obj:`True` to open the tray, :obj:`False` to close it.
:return: :obj:`True` if the tray's state was changed (or was already in that state),
    :obj:`False` if the core could not change it.

Corresponds to :c:type:`retro_set_eject_state_t` in ``libretro.h``.
"""

retro_get_eject_state_t = TypedFunctionPointer[c_bool, []]
"""
Return whether the emulated disk tray is currently open.

Registered by the :term:`core` and called by the :term:`frontend`.

:return: :obj:`True` if the virtual disk tray is open,
    :obj:`False` if it is closed.

Corresponds to :c:type:`retro_get_eject_state_t` in ``libretro.h``.
"""

retro_get_image_index_t = TypedFunctionPointer[c_uint, []]
"""
Return the index of the currently inserted disk image.

Registered by the :term:`core` and called by the :term:`frontend`.

:return: The index of the inserted disk image (starting at 0),
    or a value greater than or equal to the result of :c:type:`retro_get_num_images_t`
    if no disk is inserted.

Corresponds to :c:type:`retro_get_image_index_t` in ``libretro.h``.
"""

retro_set_image_index_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint]]]
"""
Insert the disk image at the given index into the emulated drive.

Registered by the :term:`core` and called by the :term:`frontend`.
May only be called while the tray is open.

:param index: Index of the disk image to insert, starting at 0.
    A value greater than or equal to the result of :c:type:`retro_get_num_images_t`
    represents removing the disk without inserting another.
:return: :obj:`True` if the disk image was successfully set,
    :obj:`False` if the tray is closed or another error occurred.

Corresponds to :c:type:`retro_set_image_index_t` in ``libretro.h``.
"""

retro_get_num_images_t = TypedFunctionPointer[c_uint, []]
"""
Return the number of disk images available to the core.

Registered by the :term:`core` and called by the :term:`frontend`.

:return: The number of available disk images.

Corresponds to :c:type:`retro_get_num_images_t` in ``libretro.h``.
"""

retro_replace_image_index_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], TypedPointer[retro_game_info]]
]
"""
Replace the disk image at the given index with a new one.

Registered by the :term:`core` and called by the :term:`frontend`
while the tray is open.
Passing :obj:`None` for ``info`` removes the image at ``index`` from the playlist.

:param index: Index of the disk image to replace.
:param info: Pointer to a :class:`.retro_game_info` describing the new disk image,
    or :obj:`None` to remove the image at ``index`` from the playlist.
:return: :obj:`True` if the disk image was successfully replaced or removed,
    :obj:`False` if the tray is closed or another error occurred.

Corresponds to :c:type:`retro_replace_image_index_t` in ``libretro.h``.
"""

retro_add_image_index_t = TypedFunctionPointer[c_bool, []]
"""
Add a new empty slot to the core's internal disk image list.

Registered by the :term:`core` and called by the :term:`frontend`.
The new slot must be populated with :c:type:`retro_replace_image_index_t`
before it can be used.

:return: :obj:`True` if a new slot was added, :obj:`False` otherwise.

Corresponds to :c:type:`retro_add_image_index_t` in ``libretro.h``.
"""

retro_set_initial_image_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint], CStringArg]]
"""
Set the disk image to insert before content is loaded.

Registered by the :term:`core` and called by the :term:`frontend`
immediately before :meth:`.Core.load_game`,
so that the correct disk image from a multi-disk playlist
is inserted into the emulated drive.

:param index: Index of the disk image to insert at startup.
:param path: Filesystem path of the disk image to insert,
    used by the core to validate that ``index`` refers to the expected image.
:return: :obj:`True` if the initial image was set,
    :obj:`False` if the arguments are invalid
    or the core does not support this function.

Corresponds to :c:type:`retro_set_initial_image_t` in ``libretro.h``.
"""

retro_get_image_path_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], CStringArg, CIntArg[c_size_t]]
]
"""
Retrieve the filesystem path of a disk image.

Registered by the :term:`core` and called by the :term:`frontend`.

:param index: Index of the disk image whose path will be returned.
:param path: Buffer that receives the path,
    written as a :obj:`bytes` string (UTF-8 encoded if applicable).
:param len: Size of the ``path`` buffer in bytes.
:return: :obj:`True` if a path was successfully written into ``path``,
    :obj:`False` otherwise.

Corresponds to :c:type:`retro_get_image_path_t` in ``libretro.h``.
"""

retro_get_image_label_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], CStringArg, CIntArg[c_size_t]]
]
"""
Retrieve a friendly display label for a disk image.

Registered by the :term:`core` and called by the :term:`frontend`
to obtain a human-readable label that helps the player choose
which disk image to insert.

:param index: Index of the disk image whose label will be returned.
:param path: Buffer that receives the label, written as a :obj:`bytes` string.
:param len: Size of the ``path`` buffer in bytes.
:return: :obj:`True` if a label was successfully written into ``path``,
    :obj:`False` otherwise.

Corresponds to :c:type:`retro_get_image_label_t` in ``libretro.h``.
"""


@dataclass(init=False, slots=True)
class retro_disk_control_callback(Structure, NullPointerToNoneMixin):
    """
    Corresponds to :c:type:`retro_disk_control_callback` in ``libretro.h``.

    A set of callbacks for basic disk image management.

    >>> from libretro.api import retro_disk_control_callback
    >>> cb = retro_disk_control_callback()
    >>> cb.set_eject_state is None
    True
    """

    set_eject_state: retro_set_eject_state_t | None
    """Opens or closes the virtual disk tray."""
    get_eject_state: retro_get_eject_state_t | None
    """Returns the current eject state of the disk tray."""
    get_image_index: retro_get_image_index_t | None
    """Returns the index of the currently inserted disk image."""
    set_image_index: retro_set_image_index_t | None
    """Selects a disk image by index."""
    get_num_images: retro_get_num_images_t | None
    """Returns the total number of available disk images."""
    replace_image_index: retro_replace_image_index_t | None
    """Replaces the disk image at the given index."""
    add_image_index: retro_add_image_index_t | None
    """Adds a new empty disk image slot."""

    _fields_ = (
        ("set_eject_state", retro_set_eject_state_t),
        ("get_eject_state", retro_get_eject_state_t),
        ("get_image_index", retro_get_image_index_t),
        ("set_image_index", retro_set_image_index_t),
        ("get_num_images", retro_get_num_images_t),
        ("replace_image_index", retro_replace_image_index_t),
        ("add_image_index", retro_add_image_index_t),
    )

    def __deepcopy__(self, _):
        """
        Return a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_disk_control_callback
        >>> cb = retro_disk_control_callback()
        >>> copy.deepcopy(cb).set_eject_state is None
        True
        """
        return retro_disk_control_callback(
            set_eject_state=self.set_eject_state,
            get_eject_state=self.get_eject_state,
            get_image_index=self.get_image_index,
            set_image_index=self.set_image_index,
            get_num_images=self.get_num_images,
            replace_image_index=self.replace_image_index,
            add_image_index=self.add_image_index,
        )


@dataclass(init=False, slots=True)
class retro_disk_control_ext_callback(retro_disk_control_callback):
    """
    Corresponds to :c:type:`retro_disk_control_ext_callback` in ``libretro.h``.

    Extends :class:`retro_disk_control_callback` with additional functions
    for initial image selection, image paths, and labels.

    >>> from libretro.api import retro_disk_control_ext_callback
    >>> cb = retro_disk_control_ext_callback()
    >>> cb.set_initial_image is None
    True
    """

    set_initial_image: retro_set_initial_image_t | None
    """Sets the initial disk image to insert at startup. Optional."""
    get_image_path: retro_get_image_path_t | None
    """Retrieves the filesystem path of a disk image. Optional."""
    get_image_label: retro_get_image_label_t | None
    """Retrieves the display label of a disk image. Optional."""

    _fields_ = (
        ("set_initial_image", retro_set_initial_image_t),
        ("get_image_path", retro_get_image_path_t),
        ("get_image_label", retro_get_image_label_t),
    )

    @override
    def __deepcopy__(self, _):
        """
        Return a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_disk_control_ext_callback
        >>> cb = retro_disk_control_ext_callback()
        >>> copy.deepcopy(cb).set_initial_image is None
        True
        """
        return retro_disk_control_ext_callback(
            set_eject_state=self.set_eject_state,
            get_eject_state=self.get_eject_state,
            get_image_index=self.get_image_index,
            set_image_index=self.set_image_index,
            get_num_images=self.get_num_images,
            replace_image_index=self.replace_image_index,
            add_image_index=self.add_image_index,
            set_initial_image=self.set_initial_image,
            get_image_path=self.get_image_path,
            get_image_label=self.get_image_label,
        )


__all__ = [
    "retro_disk_control_callback",
    "retro_disk_control_ext_callback",
    "retro_set_eject_state_t",
    "retro_get_eject_state_t",
    "retro_get_image_index_t",
    "retro_set_image_index_t",
    "retro_get_num_images_t",
    "retro_replace_image_index_t",
    "retro_add_image_index_t",
    "retro_set_initial_image_t",
    "retro_get_image_path_t",
    "retro_get_image_label_t",
]
