from copy import deepcopy
from ctypes import CFUNCTYPE, POINTER, Array, Structure, c_bool, c_char_p, pointer
from dataclasses import dataclass

from libretro.api._utils import FieldsFromTypeHints, deepcopy_array

RETRO_NUM_CORE_OPTION_VALUES_MAX = 128

retro_core_options_update_display_callback_t = CFUNCTYPE(c_bool)


@dataclass(init=False)
class retro_variable(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    value: c_char_p

    def __deepcopy__(self, _):
        return retro_variable(self.key, self.value)


@dataclass(init=False)
class retro_core_option_display(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    visible: c_bool

    def __deepcopy__(self, _):
        return retro_core_option_display(self.key, self.visible)


@dataclass(init=False)
class retro_core_option_value(Structure, metaclass=FieldsFromTypeHints):
    value: c_char_p
    label: c_char_p

    def __deepcopy__(self, _):
        return retro_core_option_value(self.value, self.label)


NUM_CORE_OPTION_VALUES_MAX = RETRO_NUM_CORE_OPTION_VALUES_MAX
CoreOptionArray: type[Array] = retro_core_option_value * RETRO_NUM_CORE_OPTION_VALUES_MAX


@dataclass(init=False)
class retro_core_option_definition(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    desc: c_char_p
    info: c_char_p
    values: CoreOptionArray
    default_value: c_char_p

    def __deepcopy__(self, memo):
        return retro_core_option_definition(
            self.key,
            self.desc,
            self.info,
            deepcopy_array(self.values, NUM_CORE_OPTION_VALUES_MAX, memo),
            self.default_value,
        )


@dataclass(init=False)
class retro_core_options_intl(Structure, metaclass=FieldsFromTypeHints):
    us: POINTER(retro_core_option_definition)
    local: POINTER(retro_core_option_definition)

    def __deepcopy__(self, memo):
        return retro_core_options_intl(
            pointer(deepcopy(self.us[0], memo)) if self.us else None,
            pointer(deepcopy(self.local[0], memo)) if self.local else None,
        )


@dataclass(init=False)
class retro_core_option_v2_category(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    desc: c_char_p
    info: c_char_p

    def __deepcopy__(self, _):
        return retro_core_option_v2_category(self.key, self.desc, self.info)


@dataclass(init=False)
class retro_core_option_v2_definition(Structure, metaclass=FieldsFromTypeHints):
    key: c_char_p
    desc: c_char_p
    desc_categorized: c_char_p
    info: c_char_p
    info_categorized: c_char_p
    category_key: c_char_p
    values: CoreOptionArray
    default_value: c_char_p

    def __deepcopy__(self, memo):
        return retro_core_option_v2_definition(
            self.key,
            self.desc,
            self.desc_categorized,
            self.info,
            self.info_categorized,
            self.category_key,
            deepcopy_array(self.values, NUM_CORE_OPTION_VALUES_MAX, memo),
            self.default_value,
        )


@dataclass(init=False)
class retro_core_options_v2(Structure, metaclass=FieldsFromTypeHints):
    categories: POINTER(retro_core_option_v2_category)
    definitions: POINTER(retro_core_option_v2_definition)

    def __deepcopy__(self, memo):
        return retro_core_options_v2(
            pointer(deepcopy(self.categories[0], memo)) if self.categories else None,
            pointer(deepcopy(self.definitions[0], memo)) if self.definitions else None,
        )


@dataclass(init=False)
class retro_core_options_v2_intl(Structure, metaclass=FieldsFromTypeHints):
    us: POINTER(retro_core_options_v2)
    local: POINTER(retro_core_options_v2)

    def __deepcopy__(self, memo):
        return retro_core_options_v2_intl(
            pointer(deepcopy(self.us[0], memo)) if self.us else None,
            pointer(deepcopy(self.local[0], memo)) if self.local else None,
        )


@dataclass(init=False)
class retro_core_options_update_display_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_core_options_update_display_callback_t

    def __call__(self) -> bool:
        if not self.callback:
            raise ValueError("No callback has been set")

        return bool(self.callback())

    def __deepcopy__(self, _):
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
