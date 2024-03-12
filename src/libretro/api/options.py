from abc import abstractmethod
from collections.abc import MappingView
from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable, AnyStr, Literal, Mapping

from .._utils import from_zero_terminated, as_bytes
from ..retro import *
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
            bytes(self.key.value) if self.key else None,
            bytes(self.desc.value) if self.desc else None,
            bytes(self.info.value) if self.info else None,
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


class retro_core_options_v2(Structure, metaclass=FieldsFromTypeHints):
    categories: POINTER(retro_core_option_v2_category)
    definitions: POINTER(retro_core_option_v2_definition)


class retro_core_options_v2_intl(Structure, metaclass=FieldsFromTypeHints):
    us: POINTER(retro_core_options_v2)
    local: POINTER(retro_core_options_v2)


retro_core_options_update_display_callback_t = CFUNCTYPE(c_bool, )


class retro_core_options_update_display_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_core_options_update_display_callback_t


CoreOptionDefinitionsV0 = Sequence[retro_variable] | None
CoreOptionDefinitionsV1 = Sequence[retro_core_option_definition] | retro_core_options_intl | None
CoreOptionDefinitionsV2 = retro_core_options_v2 | retro_core_options_v2_intl | None
CoreOptionDefinitions = CoreOptionDefinitionsV0 | CoreOptionDefinitionsV1 | CoreOptionDefinitionsV2


@dataclass
class OptionValue:
    value: bytes
    visible: bool


@runtime_checkable
class OptionState(Protocol):
    @abstractmethod
    def set_display(self, var: AnyStr, visible: bool): ...

    @property
    @abstractmethod
    def variable_updated(self) -> bool: ...

    @abstractmethod
    def get_version(self) -> int: ...

    @abstractmethod
    def set_options(self, options: CoreOptionDefinitions): ...

    @property
    @abstractmethod
    def supports_categories(self) -> bool: ...

    @abstractmethod
    def set_update_display_callback(self, callback: retro_core_options_update_display_callback | None): ...

    @abstractmethod
    def set_display(self, var: AnyStr, visible: bool): ...

    @abstractmethod
    def set_variable(self, var: AnyStr, value: AnyStr) -> bool: ...
    # RETRO_ENVIRONMENT_SET_VARIABLE


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
        self._categories_supported = version >= 2 if categories_supported is None else categories_supported
        self._variables: dict[bytes, OptionValue] = {
            as_bytes(k): OptionValue(as_bytes(v), True) for k, v in variables.items()
        } if variables else {}

        self._update_display_callback: retro_core_options_update_display_callback | None = None
        self._categories_us: tuple[retro_core_option_v2_category, ...] = ()
        self._options_us: tuple[retro_core_option_v2_definition, ...] = ()
        self._categories_intl: tuple[retro_core_option_v2_category, ...] = ()
        self._options_intl: tuple[retro_core_option_v2_definition, ...] = ()

    def get_variable(self, item: AnyStr) -> bytes | None:
        if not (self._options_us or self._options_intl):
            # Options can't be fetched until their definitions are set
            return None

        if not item:
            return None  # TODO: Is this behavior correct for GET_VARIABLE?

        key = as_bytes(item)
        if key not in self._variables:
            return None

        value = self._variables[key]




        # TODO: If this value is listed in the option definitions, return it; or else return the default value

        pass # RETRO_ENVIRONMENT_GET_VARIABLE

    @property
    def variable_updated(self) -> bool:
        pass

    def get_version(self) -> int:
        return self._version

    @property
    def supports_categories(self) -> bool:
        return self._categories_supported and self._version >= 2

    def set_options(self, options: CoreOptionDefinitions):
        match options:
            case retro_core_options_v2_intl() as options_v2_intl:
                options_v2_intl: retro_core_options_v2_intl

                us: retro_core_options_v2 | None = options_v2_intl.us.contents if options_v2_intl.us else None
                local: retro_core_options_v2 | None = options_v2_intl.local.contents if options_v2_intl.local else None

                self._categories_us = tuple(c for c in from_zero_terminated(us.categories)) if us else ()
                self._options_us = tuple(d for d in from_zero_terminated(us.definitions)) if us else ()
                self._categories_intl = tuple(c for c in from_zero_terminated(local.categories)) if local else ()
                self._options_intl = tuple(d for d in from_zero_terminated(local.definitions)) if local else ()
                # TODO: Check all pointers for NULL

            case retro_core_options_v2() as options_v2:
                options_v2: retro_core_options_v2

                self._categories_us = tuple(c for c in from_zero_terminated(options_v2.categories))
                self._options_us = tuple(d for d in from_zero_terminated(options_v2.definitions))
                self._categories_intl = ()
                self._options_intl = ()
                # TODO: Check all pointers for NULL

                return self._categories_supported

            case retro_core_options_intl() as options_intl:
                options_intl: retro_core_options_intl
                self._options = retro_core_options_v2_intl()
                # TODO: Copy all strings, convert to retro_core_options_v2_intl
                pass

            case [*rvars] if all(isinstance(v, retro_variable) for v in rvars):
                rvars: Sequence[retro_variable]
                # TODO: Implement
                # TODO: Copy all strings, convert to retro_core_options_v2

            case [*optdefs] if all(isinstance(d, retro_core_option_definition) for d in optdefs):
                optdefs: Sequence[retro_core_option_definition]
                # TODO: Implement
                # TODO: Copy all strings, convert to retro_core_options_v2

            case None:  # Empty array/no definitions = clear existing definitions
                self._options_us = ()
                self._options_intl = ()
                self._categories_us = ()
                self._categories_intl = ()

            case _:
                raise TypeError(f"Invalid type for options: {type(options)}")

    def set_update_display_callback(self, callback: retro_core_options_update_display_callback | None):
        match callback:
            case None:
                self._update_display_callback = None
            case retro_core_options_update_display_callback(callback=_) if not callback:
                self._update_display_callback = None
            case retro_core_options_update_display_callback(callback=callback):
                self._update_display_callback = callback
            # TODO: Handle type errors


    def set_display(self, var: AnyStr, visible: bool):
        pass


    def set_variable(self, item: str | bytes, value: str | bytes | OptionValue) -> bool:
        pass
        # TODO: Call the update display callback


# TODO: OptionState (dict[str, str])
# RETRO_ENVIRONMENT_GET_VARIABLE
# RETRO_ENVIRONMENT_SET_VARIABLES
# RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE
# RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION
# RETRO_ENVIRONMENT_SET_CORE_OPTIONS
# RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL
# RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY
# RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2
# RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL
# RETRO_ENVIRONMENT_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK
# RETRO_ENVIRONMENT_SET_VARIABLE