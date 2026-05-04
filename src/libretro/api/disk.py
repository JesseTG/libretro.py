"""
Types and callbacks for using the emulated system's disk drives, if any.
"""

from ctypes import Structure, c_bool, c_size_t, c_uint
from dataclasses import dataclass
from typing import override

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
Opens or closes the virtual disk tray.

:param ejected: :obj:`True` to open the tray, :obj:`False` to close it.
:returns: :obj:`True` on success, :obj:`False` on failure.
"""

retro_get_eject_state_t = TypedFunctionPointer[c_bool, []]
"""
Retrieves the current eject state of the emulated disk drive.

:returns: :obj:`True` if the tray is open.
"""

retro_get_image_index_t = TypedFunctionPointer[c_uint, []]
"""
Returns the index of the currently inserted disk image.
"""

retro_set_image_index_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint]]]
"""Selects a disk image by index."""

retro_get_num_images_t = TypedFunctionPointer[c_uint, []]
"""Returns the total number of disk images available."""

retro_replace_image_index_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], TypedPointer[retro_game_info]]
]
"""Replaces the disk image at the given index."""

retro_add_image_index_t = TypedFunctionPointer[c_bool, []]
"""Adds a new empty disk image slot."""

retro_set_initial_image_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint], CStringArg]]
"""Sets the initial disk image to insert at startup."""

retro_get_image_path_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], CStringArg, CIntArg[c_size_t]]
]
"""Retrieves the filesystem path of a disk image."""

retro_get_image_label_t = TypedFunctionPointer[
    c_bool, [CIntArg[c_uint], CStringArg, CIntArg[c_size_t]]
]
"""Retrieves the display label of a disk image."""


@dataclass(init=False, slots=True)
class retro_disk_control_callback(Structure):
    """Corresponds to :c:type:`retro_disk_control_callback` in ``libretro.h``.

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
        Returns a copy of this object.
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
    """Corresponds to :c:type:`retro_disk_control_ext_callback` in ``libretro.h``.

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
        Returns a copy of this object.
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
