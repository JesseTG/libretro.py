"""
Pre-built test scenarios that exercise a libretro core end-to-end.

Each module in this package wraps a different stage of a core's lifecycle
(loading, init, callback registration, content loading, running)
in a function suitable for use from a test runner or CLI tool.

.. seealso::

    :class:`.Session`
        The high-level harness these scenarios drive.
"""
