import re
from collections.abc import Collection, Mapping, MutableMapping
from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, override

from libretro.api._utils import as_bytes, from_zero_terminated
from libretro.api.options import (
    CoreOptionArray,
    retro_core_option_definition,
    retro_core_option_v2_category,
    retro_core_option_v2_definition,
    retro_core_option_value,
    retro_core_options_intl,
    retro_core_options_update_display_callback,
    retro_core_options_v2,
    retro_core_options_v2_intl,
    retro_variable,
)

from .driver import OptionDriver

_SET_VARS = re.compile(rb"(?P<desc>[^;]+); (?P<values>.+)")


@dataclass
class _Option:
    value: bytes
    visible: bool


class DictOptionDriver(OptionDriver):
    _version: Literal[0, 1, 2]
    _options: dict[bytes, _Option]
    _categories_supported: bool
    _variables_dirty: bool
    _update_display_callback: retro_core_options_update_display_callback | None
    _categories_us: dict[bytes, retro_core_option_v2_category]
    _options_us: dict[bytes, retro_core_option_v2_definition]
    _categories_intl: dict[bytes, retro_core_option_v2_category]
    _options_intl: dict[bytes, retro_core_option_v2_definition]

    def __init__(
        self,
        version: int = 2,
        categories_supported: bool | None = None,
        variables: Mapping[str, str] | Mapping[bytes, bytes] | None = None,
    ):
        if version not in (0, 1, 2):
            raise ValueError(f"Expected a core option version of 0, 1, or 2; got {version}")

        self._version = version
        self._variables_dirty = True
        self._categories_supported = (
            version >= 2 if categories_supported is None else categories_supported
        )

        self._options = {}
        if variables:
            for k, v in variables.items():
                self._options[as_bytes(k)] = _Option(as_bytes(v), True)

        self._update_display_callback = None
        self._categories_us = {}
        self._options_us = {}
        self._categories_intl = {}
        self._options_intl = {}

    @override
    def get_variable(self, key: bytes) -> bytes | None:
        if not self._options_us or not key:
            # Options can't be fetched until their definitions are set
            return None

        if key not in self._options_us:
            # For invalid keys, return None
            return None

        self._variables_dirty = False

        if key not in self._options:
            # If this option exists but hasn't been set yet,
            # return the default value and save it to the dict
            value = self._options_us[key].default_value
            assert (
                value is not None
            ), f"Option {key!r} has no default value, it should've been filtered out when initializing"
            self._options[key] = _Option(value=value, visible=True)
            return value

        # The option does exist, let's get it and ensure it's valid
        value = self._options[key].value

        registered_values = (v.value for v in self._options_us[key].values)
        if value not in registered_values:
            # Return the default value if the current value isn't in the definition,
            # but don't actually change the value in the dict
            # (RetroArch does this to handle cases like updated options)
            value = self._options_us[key].default_value
            assert (
                value is not None
            ), f"Option {key!r} has no default value, it should've been filtered out when initializing"

        return value

    @override
    def set_variables(self, variables: Collection[retro_variable] | None):
        self._categories_us.clear()
        self._categories_intl.clear()
        self._options_intl.clear()
        self._options_us.clear()

        for v in variables or ():
            if v.key and v.value and (match := _SET_VARS.match(v.value)):
                key = v.key
                desc = match["desc"]
                values = match["values"].split(b"|")
                options = CoreOptionArray(*(retro_core_option_value(v, None) for v in values))
                self._options_us[key] = retro_core_option_v2_definition(
                    key=v.key,
                    desc=desc,
                    desc_categorized=None,
                    info=None,
                    info_categorized=None,
                    category_key=None,
                    values=options,
                    default_value=values[0],
                )

        self._variables_dirty = True

    @property
    @override
    def variable_updated(self) -> bool:
        return bool(self._variables_dirty and self._options_us)

    @property
    @override
    def version(self) -> Literal[0, 1, 2]:
        return self._version

    @override
    def set_options(self, options: Collection[retro_core_option_definition] | None):
        self._categories_us.clear()
        self._categories_intl.clear()
        self._options_intl.clear()
        self._options_us.clear()

        for o in options or ():
            if o.key:
                # Make a copy of the key so it stays valid even when the core is unloaded!
                opt = retro_core_option_v2_definition(
                    key=o.key,
                    desc=o.desc,
                    desc_categorized=None,
                    info=o.info,
                    info_categorized=None,
                    category_key=None,
                    values=o.values,
                    default_value=o.default_value,
                )
                self._options_us[o.key] = opt

        self._variables_dirty = True

    @override
    def set_options_intl(self, options: retro_core_options_intl | None):
        self._categories_us.clear()
        self._categories_intl.clear()
        self._options_us.clear()
        self._options_intl.clear()

        if options and options.us:
            for o in from_zero_terminated(options.us):
                if key := o.key:
                    self._options_us[key] = retro_core_option_v2_definition(
                        key=o.key,
                        desc=o.desc,
                        desc_categorized=None,
                        info=o.info,
                        info_categorized=None,
                        category_key=None,
                        values=o.values,
                        default_value=o.default_value,
                    )

            for o in from_zero_terminated(options.local):
                if key := o.key:
                    self._options_intl[key] = retro_core_option_v2_definition(
                        key=o.key,
                        desc=o.desc,
                        desc_categorized=None,
                        info=o.info,
                        info_categorized=None,
                        category_key=None,
                        values=o.values,
                        default_value=o.default_value,
                    )

        self._variables_dirty = True

    @override
    def set_display(self, key: bytes, visible: bool):
        if not key or not self._options_us:
            # No good if any value was NULL or if no option was registered
            return

        if key not in self._options_us:
            # For invalid keys, do nothing
            return

        if key in self._options:
            self._options[key].visible = visible
        else:
            # If this option exists but hasn't been set yet,
            # return the default value and save it to the dict
            value = self._options_us[key].default_value
            assert (
                value is not None
            ), f"Option {key!r} has no default value, it should've been filtered out when initializing"
            self._options[key] = _Option(value=value, visible=visible)

    @override
    def set_options_v2(self, options: retro_core_options_v2 | None):
        self._categories_us.clear()
        self._categories_intl.clear()
        self._options_us.clear()
        self._options_intl.clear()

        if options and options.definitions:
            for c in from_zero_terminated(options.categories):
                if c.key:
                    self._categories_us[c.key] = deepcopy(c)

            for o in from_zero_terminated(options.definitions):
                if o.key:
                    self._options_us[o.key] = deepcopy(o)

        self._variables_dirty = True

    @override
    def set_options_v2_intl(self, options: retro_core_options_v2_intl | None):
        self._categories_us.clear()
        self._options_us.clear()
        self._categories_intl.clear()
        self._options_intl.clear()
        if options and options.us and options.us.contents.definitions:
            for c in from_zero_terminated(options.us.contents.categories):
                if c.key:
                    self._categories_us[c.key] = deepcopy(c)

            for o in from_zero_terminated(options.us.contents.definitions):
                if o.key:
                    self._options_us[o.key] = deepcopy(o)

            if options.local:
                for c in from_zero_terminated(options.local.contents.categories):
                    if c.key:
                        self._categories_intl[c.key] = deepcopy(c)

                for o in from_zero_terminated(options.local.contents.definitions):
                    if o.key:
                        self._options_intl[o.key] = deepcopy(o)

        self._variables_dirty = True

    @property
    @override
    def update_display_callback(
        self,
    ) -> retro_core_options_update_display_callback | None:
        return self._update_display_callback

    @update_display_callback.setter
    @override
    def update_display_callback(self, callback: retro_core_options_update_display_callback | None):
        match callback:
            case None:
                self._update_display_callback = None
            case retro_core_options_update_display_callback(callback=c) if not c:
                self._update_display_callback = None
            case retro_core_options_update_display_callback(callback=c):
                self._update_display_callback = retro_core_options_update_display_callback(c)
            case _:
                raise TypeError(
                    f"Expected a retro_core_options_update_display_callback, got {callback!r}"
                )

    @override
    def set_variable(self, var: bytes, value: bytes) -> bool:
        if not var or not value or not self._options_us:
            # No good if any value was NULL or if no option was registered
            return False

        if var not in self._options_us:
            return False

        values = self._options_us[var].values
        if not any(value == v.value for v in values):
            return False

        if var in self._options:
            self._options[var].value = value
        else:
            self._options[var] = _Option(value=value, visible=True)

        self._variables_dirty = True

        return True

    @property
    @override
    def supports_categories(self) -> bool:
        return self._categories_supported and self._version >= 2

    class VariableMapping(MutableMapping[bytes, bytes]):
        """
        Doesn't fully implement MutableMapping since the semantics
        aren't exactly the same as a normal dict (e.g. setting an invalid value doesn't actually set it),
        but core options can be mutated with __setitem__ and __delitem__.
        """

        def __init__(self, options: "DictOptionDriver"):
            self._options = options

        @override
        def __getitem__(self, key: str | bytes) -> bytes:
            """
            Get the value of an option variable by key,
            or its default value if it hasn't been set yet.

            :param key: The key of the variable to get
            :return: The value of the variable, or its default value if it hasn't been set.
            :raises KeyError: If no option with the given key has been registered
            """
            k = as_bytes(key)
            default = self._options._options_us[k].default_value
            assert (
                default is not None
            ), f"Option {k!r} has no default value, it should've been filtered out when it was registered"
            option = self._options._options.get(k, None)

            return option.value if option else default

        def __setitem__(self, key: str | bytes, value: str | bytes):
            """
            Set the value of an option variable by key.

            :param key: The key of the variable to set
            :param value: The value to set for the variable.
            str and bytes are accepted,
            but the value will always be stored as bytes.

            Values that haven't been registered can be set,
            but will only be exposed to the core
            if it registers an option with that key and value later on.
            """
            k = as_bytes(key)
            v = as_bytes(value)

            option_def = self._options._options_us.get(k, None)
            is_value_valid = option_def is not None and any(
                v == opt.value for opt in option_def.values
            )

            if existing_option := self._options._options.get(k, None):
                existing_option.value = v
            else:
                self._options._options[k] = _Option(value=v, visible=True)

            if option_def and is_value_valid:
                if self._options._update_display_callback:
                    self._options._update_display_callback()

                self._options._variables_dirty = True

        def __delitem__(self, key: str | bytes):
            """
            Delete an option variable by key;
            future attempts to get this variable will return its default value until it's set again.
            If the option isn't set, this does nothing.
            """
            k = as_bytes(key)
            if k in self._options._options:
                del self._options._options[k]

        @override
        def __len__(self):
            return len(self._options._options_us)

        @override
        def __iter__(self):
            yield from self._options._options_us.keys()

    @property
    @override
    def variables(self) -> VariableMapping:
        return DictOptionDriver.VariableMapping(self)

    class VisibilityMapping(Mapping[bytes, bool]):
        def __init__(self, options: "DictOptionDriver"):
            self._options = options

        def __getitem__(self, key: str | bytes) -> bool:
            k = as_bytes(key)
            if k not in self._options._options_us:
                raise KeyError(f"No option with key {k!r} has been registered")

            option = self._options._options.get(k, None)

            return option.visible if option else True

        def __len__(self):
            return len(self._options._options_us)

        def __iter__(self):
            yield from self._options._options_us.keys()

    @property
    def visibility(self) -> VisibilityMapping:
        return DictOptionDriver.VisibilityMapping(self)

    @property
    def categories(self) -> Mapping[bytes, retro_core_option_v2_category] | None:
        return MappingProxyType(self._categories_us) if self.supports_categories else None

    @property
    def definitions(self) -> Mapping[bytes, retro_core_option_v2_definition] | None:
        return MappingProxyType(self._options_us)


__all__ = [
    "DictOptionDriver",
]
