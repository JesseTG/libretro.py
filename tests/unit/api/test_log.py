"""Unit tests for :mod:`libretro.api.log`."""

from __future__ import annotations

import copy
import logging

from libretro.api import LogLevel, retro_log_callback


def test_log_level_to_logging_level() -> None:
    assert LogLevel.DEBUG.logging_level == logging.DEBUG
    assert LogLevel.INFO.logging_level == logging.INFO
    assert LogLevel.WARNING.logging_level == logging.WARN
    assert LogLevel.ERROR.logging_level == logging.ERROR


def test_retro_log_callback_default() -> None:
    cb = retro_log_callback()
    assert not cb.log


def test_retro_log_callback_deepcopy() -> None:
    cb = retro_log_callback()
    dup = copy.deepcopy(cb)
    assert dup is not cb
    assert not dup.log
