"""Unit tests for :class:`StandardContentDriver`'s extension matching."""

from __future__ import annotations

from pathlib import Path

import pytest

from libretro.api import retro_system_content_info_override, retro_system_info
from libretro.drivers import ContentError, StandardContentDriver

CONTENT = b"content"


def driver(valid_extensions: bytes) -> StandardContentDriver:
    content = StandardContentDriver()
    content.system_info = retro_system_info(
        library_name=b"TestCore",
        library_version=b"1.0",
        valid_extensions=valid_extensions,
        need_fullpath=True,
        block_extract=False,
    )
    return content


@pytest.mark.parametrize(
    ("valid_extensions", "filename"),
    [(b"pdf|cbz", "UPPER.PDF"), (b"PDF|CBZ", "lower.pdf"), (b"pdf|cbz", "Mixed.Cbz")],
)
def test_content_extensions_ignore_case(
    tmp_path: Path, valid_extensions: bytes, filename: str
) -> None:
    """RetroArch accepts content whose extension differs in case from the core's list."""
    path = tmp_path / filename
    path.write_bytes(CONTENT)

    with driver(valid_extensions).load(path) as (_, files):
        assert files is not None
        assert files[0].info.path == bytes(path)


def test_unsupported_extension_is_still_rejected(tmp_path: Path) -> None:
    path = tmp_path / "notes.TXT"
    path.write_bytes(CONTENT)

    with pytest.raises(ContentError), driver(b"pdf|cbz").load(path):
        pass


def test_content_info_override_ignores_case(tmp_path: Path) -> None:
    """An override for ``pdf`` applies to ``.PDF`` files."""
    path = tmp_path / "UPPER.PDF"
    path.write_bytes(CONTENT)
    content = driver(b"pdf|cbz")
    content.overrides = [
        retro_system_content_info_override(extensions=b"pdf", need_fullpath=False)
    ]

    with content.load(path) as (_, files):
        assert files is not None
        # The override doesn't need a full path, so the driver loads the file's data.
        assert files[0].info.size == len(CONTENT)
