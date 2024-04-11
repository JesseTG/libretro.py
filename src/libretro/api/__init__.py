"""
This module contains types that directly correspond to the libretro API,

All ``retro_`` classes in this package are ctypes wrappers around their equivalents in
`libretro-common <https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h>`_.

Unless otherwise noted, all structs can be copied with ``copy.deepcopy``;
the struct itself and its fields (including strings and buffers) are all deep-copied.
For example:

.. code-block:: python

        import copy
        from libretro.api import retro_controller_description

        desc = retro_controller_description(b'Game Pad', 5)
        desc_copy = copy.deepcopy(desc)

        assert desc == desc_copy

        desc.desc = b'Another Game Pad'
        assert desc != desc_copy

Additionally, all `c_char_p` fields are converted to Python `bytes` objects when accessed.
"""

from .audio import *
from .av import *