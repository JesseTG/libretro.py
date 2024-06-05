import sys

if sys.version_info >= (3, 12):
    from collections.abc import Buffer
    from typing import override
else:
    from typing_extensions import Buffer, override

__all__ = [
    "Buffer",
    "override",
]
