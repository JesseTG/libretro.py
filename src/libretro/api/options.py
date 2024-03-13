from abc import abstractmethod
from copy import deepcopy
from ctypes import *
from collections.abc import MutableMapping
import re
from typing import Protocol, Sequence, runtime_checkable, AnyStr, Literal, Mapping, overload

from .._utils import from_zero_terminated, as_bytes, FieldsFromTypeHints
from ..h import RETRO_NUM_CORE_OPTION_VALUES_MAX


class retro_variable(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    value: c_char_p


class retro_core_option_display(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    visible: c_bool


class retro_core_option_value(Structure, metaclass=FieldsFromTypeHints):
    value: c_char_p
    label: c_char_p

    def __deepcopy__(self, _):
        return retro_core_option_value(
            bytes(self.value) if self.value else None,
            bytes(self.label) if self.label else None,
        )


CoreOptionArray = retro_core_option_value * RETRO_NUM_CORE_OPTION_VALUES_MAX

class retro_core_option_definition(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    desc: c_char_p
    info: c_char_p
    values: retro_core_option_value * RETRO_NUM_CORE_OPTION_VALUES_MAX
    default_value: c_char_p


class retro_core_options_intl(Structure, metaclass=FieldsFromTypeHints):
    us: POINTER(retro_core_option_definition)
    local: POINTER(retro_core_option_definition)


class retro_core_option_v2_category(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    desc: c_char_p
    info: c_char_p

    def __deepcopy__(self, _):
        return retro_core_option_v2_category(
            bytes(self.key) if self.key else None,
            bytes(self.desc) if self.desc else None,
            bytes(self.info) if self.info else None,
        )


class retro_core_option_v2_definition(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    desc: c_char_p
    desc_categorized: c_char_p
    info: c_char_p
    info_categorized: c_char_p
    category_key: c_char_p
    values: retro_core_option_value * RETRO_NUM_CORE_OPTION_VALUES_MAX
    default_value: c_char_p

    def __deepcopy__(self, _):
        arraytype = retro_core_option_value * RETRO_NUM_CORE_OPTION_VALUES_MAX
        return retro_core_option_v2_definition(
            bytes(self.key) if self.key else None,
            bytes(self.desc) if self.desc else None,
            bytes(self.desc_categorized) if self.desc_categorized else None,
            bytes(self.info) if self.info else None,
            bytes(self.info_categorized) if self.info_categorized else None,
            bytes(self.category_key) if self.category_key else None,
            arraytype.from_buffer_copy(self.values),
            bytes(self.default_value) if self.default_value else None,
        )


class retro_core_options_v2(Structure, metaclass=FieldsFromTypeHints):
    categories: POINTER(retro_core_option_v2_category)
    definitions: POINTER(retro_core_option_v2_definition)


class retro_core_options_v2_intl(Structure, metaclass=FieldsFromTypeHints):
    us: POINTER(retro_core_options_v2)
    local: POINTER(retro_core_options_v2)


retro_core_options_update_display_callback_t = CFUNCTYPE(c_bool)


class retro_core_options_update_display_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_core_options_update_display_callback_t

    def __call__(self) -> bool:
        if not self.callback:
            raise ValueError("No callback has been set")

        return bool(self.callback())


_SET_VARS = re.compile(br"(?P<desc>[^;]+); (?P<values>.+)")


@runtime_checkable
class OptionState(Protocol):
    @abstractmethod
    def get_variable(self, item: bytes) -> bytes | None: ...

    @abstractmethod
    def set_variables(self, variables: Sequence[retro_variable] | None): ...

    @abstractmethod
    def get_variable_update(self) -> bool: ...

    @abstractmethod
    def get_version(self) -> int: ...

    @abstractmethod
    def set_options(self, options: Sequence[retro_core_option_definition] | None): ...

    @abstractmethod
    def set_options_intl(self, options: retro_core_options_intl | None): ...

    @abstractmethod
    def set_display(self, var: bytes, visible: bool): ...

    @abstractmethod
    def set_options_v2(self, options: retro_core_options_v2 | None): ...

    @abstractmethod
    def set_options_v2_intl(self, options: retro_core_options_v2_intl | None): ...

    @abstractmethod
    def set_update_display_callback(self, callback: retro_core_options_update_display_callback | None): ...

    @abstractmethod
    def set_variable(self, var: bytes, value: bytes) -> bool: ...

    @property
    def variable_updated(self) -> bool:
        return self.get_variable_update()

    @property
    def version(self):
        return self.get_version()

    @property
    @abstractmethod
    def update_display_callback(self) -> retro_core_options_update_display_callback | None: ...

    @property
    @abstractmethod
    def supports_categories(self) -> bool: ...

    @property
    @abstractmethod
    def variables(self) -> MutableMapping[AnyStr, bytes]: ...

    @property
    @abstractmethod
    def visibility(self) -> Mapping[AnyStr, bool]: ...

    @property
    @abstractmethod
    def categories(self) -> Mapping[bytes, retro_core_option_v2_category] | None: ...

    @property
    @abstractmethod
    def definitions(self) -> Mapping[bytes, retro_core_option_v2_definition] | None: ...


class StandardOptionState(OptionState):
    def __init__(
            self,
            version: Literal[0, 1, 2] = 2,
            categories_supported: bool | None = None,
            variables: Mapping[AnyStr, AnyStr] | None = None,
    ):
        if version not in {0, 1, 2}:
            raise ValueError(f"Expected a core option version of 0, 1, or 2; got {version}")

        self._version = version
        self._variables_dirty = True
        self._categories_supported = version >= 2 if categories_supported is None else categories_supported

        self._variables: dict[bytes, bytes] = {
            as_bytes(k): as_bytes(v) for k, v in variables.items()
        } if variables else {}

        self._visibility: dict[bytes, bool] = {
            as_bytes(k): True for k in variables
        } if variables else {}

        self._update_display_callback: retro_core_options_update_display_callback | None = None
        self._categories_us: dict[bytes, retro_core_option_v2_category] = {}
        self._options_us: dict[bytes, retro_core_option_v2_definition] = {}
        self._categories_intl: dict[bytes, retro_core_option_v2_category] = {}
        self._options_intl: dict[bytes, retro_core_option_v2_definition] = {}

    def get_variable(self, item: bytes) -> bytes | None:
        if not self._options_us or not item:
            # Options can't be fetched until their definitions are set
            return None

        self._variables_dirty = False

        key = as_bytes(item)

        if key not in self._options_us:
            # For invalid keys, return None
            return None

        if key not in self._variables:
            # For unset options, return the default value
            return string_at(self._options_us[key].default_value)

        value = self._variables[key]

        if value not in (string_at(v.value) for v in self._options_us[key].values if v):
            # For invalid values, return None
            return string_at(self._options_us[key].default_value)

        return self._variables[key]

    def set_variables(self, variables: Sequence[retro_variable] | None):
        self._categories_us.clear()
        self._categories_intl.clear()
        self._options_intl.clear()
        self._options_us.clear()

        if variables:
            for v in variables:
                match = _SET_VARS.match(v.value)
                desc: bytes = match["desc"]
                values: list[bytes] = match["values"].split(b"|")
                key = bytes(v.key)
                optsarray: CoreOptionArray = CoreOptionArray()
                for i, value in enumerate(values):
                    optsarray[i] = retro_core_option_value(value, None)

                opt = retro_core_option_v2_definition(key, desc, None, None, None, None, optsarray, values[0])
                self._options_us[key] = opt

        self._variables_dirty = True

    def get_variable_update(self) -> bool:
        return self._variables_dirty

    def get_version(self) -> int:
        return self._version

    def set_options(self, options: Sequence[retro_core_option_definition] | None):
        self._categories_us.clear()
        self._categories_intl.clear()
        self._options_intl.clear()
        self._options_us.clear()

        if options:
            for o in options:
                key = bytes(o.key)
                # Make a copy of the key so it stays valid even when the core is unloaded!
                opt = retro_core_option_v2_definition(o.key, o.desc, None, o.info, None, None, o.values, o.default_value)
                self._options_us[key] = opt

        self._variables_dirty = True

    def set_options_intl(self, options: retro_core_options_intl | None):
        self._categories_us.clear()
        self._categories_intl.clear()
        if not options or not options.us:
            self._options_us.clear()
            self._options_intl.clear()
        else:
            self._options_us = {bytes(o.key): deepcopy(o) for o in from_zero_terminated(options.us.contents)}

            if options.local:
                self._options_intl = {bytes(o.key): deepcopy(o) for o in from_zero_terminated(options.local.contents)}

        self._variables_dirty = True

    def set_display(self, var: AnyStr, visible: bool):
        if not var or not self._options_us:
            # No good if any value was NULL or if no option was registered
            return

        key = as_bytes(var)
        self._visibility[key] = visible

    def set_options_v2(self, options: retro_core_options_v2 | None):
        self._categories_intl.clear()
        self._options_intl.clear()

        if options and options.definitions:
            self._categories_us = {bytes(c.key): deepcopy(c) for c in from_zero_terminated(options.categories)}
            self._options_us = {bytes(o.key): deepcopy(o) for o in from_zero_terminated(options.definitions)}
        else:
            self._categories_us.clear()
            self._options_us.clear()

        self._variables_dirty = True

    def set_options_v2_intl(self, options: retro_core_options_v2_intl | None):
        if not options or not options.us or not options.us.contents.definitions:
            self._categories_us.clear()
            self._options_us.clear()
            self._categories_intl.clear()
            self._options_intl.clear()
        else:
            us: retro_core_options_v2 = options.us.contents

            self._categories_us = {bytes(c.key): deepcopy(c) for c in from_zero_terminated(us.categories)}
            self._options_us = {bytes(o.key): deepcopy(o) for o in from_zero_terminated(us.definitions)}

            if options.local:
                local: retro_core_options_v2 = options.local.contents

                self._categories_intl = {bytes(c.key): deepcopy(c) for c in from_zero_terminated(local.categories)}
                self._options_intl = {bytes(o.key): deepcopy(o) for o in from_zero_terminated(local.definitions)}

        self._variables_dirty = True

    def set_update_display_callback(self, callback: retro_core_options_update_display_callback | None):
        match callback:
            case None:
                self._update_display_callback = None
            case retro_core_options_update_display_callback(callback=c) if not c:
                self._update_display_callback = None
            case retro_core_options_update_display_callback(callback=c):
                self._update_display_callback = retro_core_options_update_display_callback(c)
            case _:
                raise TypeError(f"Expected a retro_core_options_update_display_callback, got {callback!r}")

    def set_variable(self, item: AnyStr, value: AnyStr) -> bool:
        if not item or not value or not self._options_us:
            # No good if any value was NULL or if no option was registered
            return False

        key = as_bytes(item)
        if key not in self._options_us:
            return False

        val = as_bytes(value)
        values: Array = self._options_us[key].values
        if not any(val == string_at(v.value) for v in values):
            return False

        self._variables[key] = val
        self._variables_dirty = True

    @property
    def update_display_callback(self) -> retro_core_options_update_display_callback | None:
        return self._update_display_callback

    @property
    def supports_categories(self) -> bool:
        return self._categories_supported and self._version >= 2

    class _VariableMapping(MutableMapping[AnyStr, bytes]):
        def __init__(self, options: 'StandardOptionState'):
            self._options = options

        def __getitem__(self, key: AnyStr) -> bytes:
            k = as_bytes(key)
            default = self._options._options_us[k].default_value
            return self._options._variables.get(k, default)

        def __setitem__(self, key: bytes, value: bytes):
            k = as_bytes(key)
            self._options._variables[k] = value
            if self._options._update_display_callback:
                self._options._update_display_callback()

            self._options._variables_dirty = True

        def __delitem__(self, key: bytes):
            k = as_bytes(key)
            del self._options._variables[k]

        def __len__(self):
            return len(self._options._options_us)

        def __iter__(self):
            yield from self._options._options_us.keys()


    @property
    def variables(self) -> MutableMapping[AnyStr, bytes]:
        return StandardOptionState._VariableMapping(self)

    class _VisibilityMapping(Mapping[AnyStr, bool]):
        def __init__(self, options: 'StandardOptionState'):
            self._options = options

        def __getitem__(self, key: AnyStr) -> bool:
            k = as_bytes(key)
            return self._options._visibility.get(k, True)

        def __len__(self):
            return len(self._options._options_us)

        def __iter__(self):
            yield from self._options._options_us.keys()

    @property
    def visibility(self) -> Mapping[AnyStr, bool]:
        return StandardOptionState._VisibilityMapping(self)

    @property
    def categories(self) -> Mapping[bytes, retro_core_option_v2_category] | None:
        return self._categories_us if self.supports_categories else None

    @property
    def definitions(self) -> Mapping[bytes, retro_core_option_v2_definition] | None:
        return self._options_us

