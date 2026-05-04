"""Core option definitions, values, categories, and internationalization.

Corresponds to the ``retro_core_option_*`` and ``retro_variable`` types
in ``libretro.h``. Defines option definitions, values, categories,
and internationalization wrappers for core configuration.

.. seealso:: :mod:`libretro.drivers.options`
"""

from copy import deepcopy
from ctypes import POINTER, Array, Structure, c_bool, c_char_p, pointer
from dataclasses import dataclass

from libretro.api._utils import MemoDict, deepcopy_array
from libretro.ctypes import TypedArray, TypedFunctionPointer, TypedPointer

RETRO_NUM_CORE_OPTION_VALUES_MAX = 128
"""Maximum number of values a single core option can have."""


retro_core_options_update_display_callback_t = TypedFunctionPointer[c_bool, []]
"""Called when the frontend should re-check option visibility."""


@dataclass(init=False, slots=True)
class retro_variable(Structure):
    """Corresponds to :c:type:`retro_variable` in ``libretro.h``.

    A key/value pair used for legacy core options (v0).

    >>> from libretro.api import retro_variable
    >>> v = retro_variable()
    >>> v.key is None
    True
    """

    key: bytes | None
    """The option's unique key."""
    value: bytes | None
    """The option's current value, or a pipe-delimited list of possible values."""

    _fields_ = (
        ("key", c_char_p),
        ("value", c_char_p),
    )

    def __deepcopy__(self, _):
        """Returns a copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_variable
        >>> copy.deepcopy(retro_variable()).key is None
        True
        """
        return retro_variable(self.key, self.value)


@dataclass(init=False, slots=True)
class retro_core_option_display(Structure):
    """Corresponds to :c:type:`retro_core_option_display` in ``libretro.h``.

    Controls whether a core option is visible in the frontend UI.

    >>> from libretro.api import retro_core_option_display
    >>> d = retro_core_option_display()
    >>> d.visible
    False
    """

    key: bytes | None
    """The unique key of the option to show or hide."""
    visible: bool
    """Whether the option should be visible to the player."""

    _fields_ = (
        ("key", c_char_p),
        ("visible", c_bool),
    )

    def __deepcopy__(self, _):
        """
        Returns a copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_option_display(self.key, self.visible)


@dataclass(init=False, slots=True)
class retro_core_option_value(Structure):
    """Corresponds to :c:type:`retro_core_option_value` in ``libretro.h``.

    A single selectable value for a core option.

    >>> from libretro.api import retro_core_option_value
    >>> v = retro_core_option_value()
    >>> v.value is None
    True
    """

    value: bytes | None
    """Internal value string."""
    label: bytes | None
    """Human-readable label, or ``None`` to display :attr:`value` as-is."""

    _fields_ = (
        ("value", c_char_p),
        ("label", c_char_p),
    )

    def __deepcopy__(self, _):
        """Returns a copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_option_value(self.value, self.label)


NUM_CORE_OPTION_VALUES_MAX = RETRO_NUM_CORE_OPTION_VALUES_MAX
"""Alias for :const:`RETRO_NUM_CORE_OPTION_VALUES_MAX`."""

CoreOptionArray = retro_core_option_value * RETRO_NUM_CORE_OPTION_VALUES_MAX
"""Fixed-size array type for :class:`retro_core_option_value` entries."""


@dataclass(init=False, slots=True)
class retro_core_option_definition(Structure):
    """Corresponds to :c:type:`retro_core_option_definition` in ``libretro.h``.

    Defines a single core option with a key, description, info text,
    possible values, and a default value (v1 options API).

    >>> from libretro.api import retro_core_option_definition
    >>> d = retro_core_option_definition()
    >>> d.key is None
    True
    """

    key: bytes | None
    """Unique key for this option."""
    desc: bytes | None
    """Human-readable description shown to the player."""
    info: bytes | None
    """Extended information or tooltip text."""
    values: Array[retro_core_option_value]
    """Array of possible values for this option."""
    default_value: bytes | None
    """Default value if not previously set."""

    _fields_ = (
        ("key", c_char_p),
        ("desc", c_char_p),
        ("info", c_char_p),
        ("values", CoreOptionArray),
        ("default_value", c_char_p),
    )

    def __deepcopy__(self, memo: MemoDict = None):
        """
        Returns a copy of this object, including all strings and subobjects.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_option_definition(
            self.key,
            self.desc,
            self.info,
            deepcopy_array(self.values, memo),
            self.default_value,
        )


@dataclass(init=False, slots=True)
class retro_core_options_intl(Structure):
    """Corresponds to :c:type:`retro_core_options_intl` in ``libretro.h``.

    Wraps US English and localized option definitions for v1 options.

    >>> from libretro.api import retro_core_options_intl
    >>> intl = retro_core_options_intl()
    >>> intl.us is None
    True
    """

    us: TypedPointer[retro_core_option_definition] | None
    """US English option definitions."""
    local: TypedPointer[retro_core_option_definition] | None
    """Localized option definitions."""

    _fields_ = (
        ("us", POINTER(retro_core_option_definition)),
        ("local", POINTER(retro_core_option_definition)),
    )

    def __deepcopy__(self, memo: MemoDict = None):
        """
        Returns a copy of this object, including all strings and subobjects.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_options_intl(
            pointer(deepcopy(self.us[0], memo)) if self.us else None,
            pointer(deepcopy(self.local[0], memo)) if self.local else None,
        )


@dataclass(init=False, slots=True)
class retro_core_option_v2_category(Structure):
    """Corresponds to :c:type:`retro_core_option_v2_category` in ``libretro.h``.

    Groups related options under a named category (v2 options API).

    >>> from libretro.api import retro_core_option_v2_category
    >>> cat = retro_core_option_v2_category()
    >>> cat.key is None
    True
    """

    key: bytes | None
    """Unique key for this category."""
    desc: bytes | None
    """Human-readable description shown to the player."""
    info: bytes | None
    """Extended information about this category."""

    _fields_ = (
        ("key", c_char_p),
        ("desc", c_char_p),
        ("info", c_char_p),
    )

    def __deepcopy__(self, _):
        """
        Returns a copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_option_v2_category(self.key, self.desc, self.info)


@dataclass(init=False, slots=True)
class retro_core_option_v2_definition(Structure):
    """Corresponds to :c:type:`retro_core_option_v2_definition` in ``libretro.h``.

    Defines a single core option with category support (v2 options API).

    >>> from libretro.api import retro_core_option_v2_definition
    >>> d = retro_core_option_v2_definition()
    >>> d.key is None
    True
    """

    key: bytes | None
    """Unique key for this option."""
    desc: bytes | None
    """Human-readable description shown to the player."""
    desc_categorized: bytes | None
    """Shorter description for display under its category."""
    info: bytes | None
    """Extended information or tooltip text."""
    info_categorized: bytes | None
    """Shorter tooltip text for display under its category."""
    category_key: bytes | None
    """Key of the category this option belongs to, or ``None``."""
    values: TypedArray[retro_core_option_value]
    """Array of possible values for this option."""
    default_value: bytes | None
    """Default value if not previously set."""

    _fields_ = (
        ("key", c_char_p),
        ("desc", c_char_p),
        ("desc_categorized", c_char_p),
        ("info", c_char_p),
        ("info_categorized", c_char_p),
        ("category_key", c_char_p),
        ("values", CoreOptionArray),
        ("default_value", c_char_p),
    )

    def __deepcopy__(self, memo: MemoDict = None):
        """
        Returns a copy of this object, including all strings and subobjects.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_option_v2_definition(
            self.key,
            self.desc,
            self.desc_categorized,
            self.info,
            self.info_categorized,
            self.category_key,
            deepcopy_array(self.values, memo),
            self.default_value,
        )


@dataclass(init=False, slots=True)
class retro_core_options_v2(Structure):
    """Corresponds to :c:type:`retro_core_options_v2` in ``libretro.h``.

    Top-level container for v2 option categories and definitions.

    >>> from libretro.api import retro_core_options_v2
    >>> v2 = retro_core_options_v2()
    >>> v2.categories is None
    True
    """

    categories: TypedPointer[retro_core_option_v2_category] | None
    """Array of option categories, terminated by a zeroed-out entry."""
    definitions: TypedPointer[retro_core_option_v2_definition] | None
    """Array of option definitions, terminated by a zeroed-out entry."""

    _fields_ = (
        ("categories", POINTER(retro_core_option_v2_category)),
        ("definitions", POINTER(retro_core_option_v2_definition)),
    )

    def __deepcopy__(self, memo: MemoDict = None):
        """
        Returns a copy of this object, including all strings and subobjects.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_options_v2(
            pointer(deepcopy(self.categories[0], memo)) if self.categories else None,
            pointer(deepcopy(self.definitions[0], memo)) if self.definitions else None,
        )


@dataclass(init=False, slots=True)
class retro_core_options_v2_intl(Structure):
    """Corresponds to :c:type:`retro_core_options_v2_intl` in ``libretro.h``.

    Wraps US English and localized v2 option sets.

    >>> from libretro.api import retro_core_options_v2_intl
    >>> intl = retro_core_options_v2_intl()
    >>> intl.us is None
    True
    """

    us: TypedPointer[retro_core_options_v2] | None
    """US English option definitions and categories."""
    local: TypedPointer[retro_core_options_v2] | None
    """Localized option definitions and categories."""

    _fields_ = (
        ("us", POINTER(retro_core_options_v2)),
        ("local", POINTER(retro_core_options_v2)),
    )

    def __deepcopy__(self, memo: MemoDict = None):
        """Returns a copy of this object, including all strings and subobjects.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_options_v2_intl(
            pointer(deepcopy(self.us[0], memo)) if self.us else None,
            pointer(deepcopy(self.local[0], memo)) if self.local else None,
        )


@dataclass(init=False, slots=True)
class retro_core_options_update_display_callback(Structure):
    """Corresponds to :c:type:`retro_core_options_update_display_callback` in ``libretro.h``.

    Wraps a callback that the frontend calls to determine
    whether to refresh option visibility.

    >>> from libretro.api import retro_core_options_update_display_callback
    >>> cb = retro_core_options_update_display_callback()
    >>> cb.callback is None
    True
    """

    callback: retro_core_options_update_display_callback_t | None
    """Called by the frontend to request a visibility update for core options."""

    _fields_ = (("callback", retro_core_options_update_display_callback_t),)

    def __call__(self) -> bool:
        """Invokes the callback.

        :raises ValueError: If no callback has been set.
        :returns: ``True`` if the display should be updated.
        """
        if not self.callback:
            raise ValueError("No callback has been set")

        return bool(self.callback())

    def __deepcopy__(self, _):
        """
        Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.
        """
        return retro_core_options_update_display_callback(self.callback)


__all__ = [
    "retro_variable",
    "retro_core_option_display",
    "retro_core_option_value",
    "CoreOptionArray",
    "retro_core_option_definition",
    "retro_core_options_intl",
    "retro_core_option_v2_category",
    "retro_core_option_v2_definition",
    "retro_core_options_v2",
    "retro_core_options_v2_intl",
    "retro_core_options_update_display_callback",
    "retro_core_options_update_display_callback_t",
    "NUM_CORE_OPTION_VALUES_MAX",
]
