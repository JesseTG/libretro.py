import sys

if sys.version_info >= (3, 13):
    from collections.abc import Buffer
    from warnings import deprecated
else:
    from typing_extensions import Buffer, deprecated

__all__ = ("Buffer", "deprecated")
