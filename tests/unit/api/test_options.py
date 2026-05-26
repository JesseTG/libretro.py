"""Unit tests for :mod:`libretro.api.options`."""

from __future__ import annotations

import copy

import pytest

from libretro.api import (
    retro_core_option_definition,
    retro_core_option_display,
    retro_core_option_v2_category,
    retro_core_option_v2_definition,
    retro_core_option_value,
    retro_core_options_intl,
    retro_core_options_update_display_callback,
    retro_core_options_v2,
    retro_core_options_v2_intl,
    retro_variable,
)


def test_retro_variable_kwarg_init() -> None:
    v = retro_variable(key=b"libretro_test_opt", value=b"enabled")
    assert v.key == b"libretro_test_opt"
    assert v.value == b"enabled"


def test_retro_variable_defaults() -> None:
    v = retro_variable()
    assert v.key is None
    assert v.value is None


def test_retro_variable_deepcopy() -> None:
    v = retro_variable(key=b"x", value=b"on")
    dup = copy.deepcopy(v)
    assert dup is not v
    assert dup.key == v.key
    assert dup.value == v.value


def test_retro_core_option_display_kwarg_init() -> None:
    d = retro_core_option_display(key=b"foo", visible=True)
    assert d.key == b"foo"
    assert d.visible is True


def test_retro_core_option_display_default_invisible() -> None:
    d = retro_core_option_display()
    assert d.visible is False


def test_retro_core_option_display_deepcopy() -> None:
    d = retro_core_option_display(key=b"foo", visible=True)
    dup = copy.deepcopy(d)
    assert dup is not d
    assert dup.key == d.key
    assert dup.visible == d.visible


def test_retro_core_option_value_kwarg_init() -> None:
    v = retro_core_option_value(value=b"on", label=b"Enabled")
    assert v.value == b"on"
    assert v.label == b"Enabled"


def test_retro_core_option_value_deepcopy() -> None:
    v = retro_core_option_value(value=b"on", label=b"Enabled")
    dup = copy.deepcopy(v)
    assert dup is not v
    assert dup.value == v.value
    assert dup.label == v.label


def test_retro_core_option_definition_kwarg_init() -> None:
    d = retro_core_option_definition(
        key=b"opt",
        desc=b"Option",
        info=b"Tooltip text",
        default_value=b"on",
    )
    assert d.key == b"opt"
    assert d.desc == b"Option"
    assert d.info == b"Tooltip text"
    assert d.default_value == b"on"


def test_retro_core_option_definition_deepcopy() -> None:
    d = retro_core_option_definition(key=b"opt", desc=b"Option", default_value=b"on")
    dup = copy.deepcopy(d)
    assert dup is not d
    assert dup.key == d.key
    assert dup.default_value == d.default_value


def test_retro_core_options_intl_defaults() -> None:
    intl = retro_core_options_intl()
    assert not intl.us
    assert not intl.local


def test_retro_core_options_intl_deepcopy() -> None:
    intl = retro_core_options_intl()
    dup = copy.deepcopy(intl)
    assert dup is not intl


def test_retro_core_option_v2_category_kwarg_init() -> None:
    cat = retro_core_option_v2_category(key=b"audio", desc=b"Audio", info=b"Audio options")
    assert cat.key == b"audio"
    assert cat.desc == b"Audio"
    assert cat.info == b"Audio options"


def test_retro_core_option_v2_category_deepcopy() -> None:
    cat = retro_core_option_v2_category(key=b"x", desc=b"X", info=b"i")
    dup = copy.deepcopy(cat)
    assert dup is not cat
    assert dup.key == cat.key


def test_retro_core_option_v2_definition_kwarg_init() -> None:
    d = retro_core_option_v2_definition(
        key=b"opt",
        desc=b"Option",
        desc_categorized=b"Opt",
        info=b"Info",
        info_categorized=b"i",
        category_key=b"audio",
        default_value=b"on",
    )
    assert d.key == b"opt"
    assert d.desc_categorized == b"Opt"
    assert d.category_key == b"audio"
    assert d.default_value == b"on"


def test_retro_core_option_v2_definition_deepcopy() -> None:
    d = retro_core_option_v2_definition(key=b"x", default_value=b"on")
    dup = copy.deepcopy(d)
    assert dup is not d
    assert dup.key == d.key
    assert dup.default_value == d.default_value


def test_retro_core_options_v2_defaults() -> None:
    v2 = retro_core_options_v2()
    assert not v2.categories
    assert not v2.definitions


def test_retro_core_options_v2_intl_defaults() -> None:
    intl = retro_core_options_v2_intl()
    assert not intl.us
    assert not intl.local


def test_retro_core_options_update_display_callback_default() -> None:
    cb = retro_core_options_update_display_callback()
    assert not cb.callback


def test_retro_core_options_update_display_callback_raises_when_unset() -> None:
    cb = retro_core_options_update_display_callback()
    with pytest.raises(ValueError):
        cb()


def test_retro_core_options_update_display_callback_deepcopy() -> None:
    cb = retro_core_options_update_display_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert not dup.callback
