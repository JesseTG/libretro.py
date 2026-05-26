"""Unit tests for :mod:`libretro.api.message`."""

from __future__ import annotations

import copy

from libretro.api import (
    LogLevel,
    MessageTarget,
    MessageType,
    retro_message,
    retro_message_ext,
)


def test_retro_message_kwarg_init() -> None:
    msg = retro_message(msg=b"loaded", frames=60)
    assert msg.msg == b"loaded"
    assert msg.frames == 60


def test_retro_message_defaults_are_zero() -> None:
    msg = retro_message()
    assert msg.msg is None
    assert msg.frames == 0


def test_retro_message_deepcopy() -> None:
    msg = retro_message(msg=b"loaded", frames=60)
    dup = copy.deepcopy(msg)
    assert dup is not msg
    assert dup.msg == msg.msg
    assert dup.frames == msg.frames


def test_retro_message_ext_kwarg_init_all_fields() -> None:
    msg = retro_message_ext(
        msg=b"loading",
        duration=2500,
        priority=10,
        level=LogLevel.INFO,
        target=MessageTarget.OSD,
        type=MessageType.NOTIFICATION,
        progress=50,
    )
    assert msg.msg == b"loading"
    assert msg.duration == 2500
    assert msg.priority == 10
    assert msg.level == LogLevel.INFO
    assert msg.target == MessageTarget.OSD
    assert msg.type == MessageType.NOTIFICATION
    assert msg.progress == 50


def test_retro_message_ext_progress_can_be_negative() -> None:
    msg = retro_message_ext(progress=-1)
    assert msg.progress == -1


def test_retro_message_ext_deepcopy_preserves_all_fields() -> None:
    msg = retro_message_ext(msg=b"hi", duration=500, priority=5, progress=10)
    dup = copy.deepcopy(msg)
    assert dup is not msg
    assert dup.msg == msg.msg
    assert dup.duration == msg.duration
    assert dup.priority == msg.priority
    assert dup.progress == msg.progress


def test_message_target_enum_round_trips() -> None:
    assert MessageTarget.ALL.value == 0
    assert MessageTarget.OSD.value == 1
    assert MessageTarget.LOG.value == 2


def test_message_type_enum_round_trips() -> None:
    assert MessageType.NOTIFICATION.value == 0
    assert MessageType.NOTIFICATION_ALT.value == 1
    assert MessageType.STATUS.value == 2
    assert MessageType.PROGRESS.value == 3
