"""
Sample libretro cores bundled with libretro.py for testing and demonstration.

Cores are organized by category under :mod:`libretro.samples`:

* :mod:`libretro.samples.audio` — audio output samples.
* :mod:`libretro.samples.input` — input-handling samples.
* :mod:`libretro.samples.midi` — MIDI I/O samples.
* :mod:`libretro.samples.tests` — general-purpose reference cores.
* :mod:`libretro.samples.video` — video-rendering samples.
* :mod:`libretro.samples.custom` — small cores written specifically for libretro.py's test suite.

Each core is exposed as a :class:`~libretro.core.Core` object on the
appropriate subpackage,
constructed lazily the first time it is imported by name.
Importing the subpackage itself loads nothing;
``from libretro.samples.input import button_test`` is what triggers the
underlying shared library to be loaded and cached.

When libretro.py was installed from a pure-Python wheel
(for example on a platform we haven't built sample cores for),
accessing one of these names raises :class:`ImportError` with a message
explaining that the sample cores are not bundled for the current
platform.

.. seealso::

    :class:`~libretro.core.Core`
        The class returned by each sample-core name.
"""
