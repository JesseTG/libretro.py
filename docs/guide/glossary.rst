Glossary
========

This page defines important terms that are used throughout libretro.py's documentation.

.. glossary::

    callback
    callback function
        A function that's passed to a :term:`core` or :term:`frontend` at runtime,
        rather than at link-time like most C functions.

        .. note::
            Some libretro frontends link their cores statically due to platform limits.
            libretro.py isn't one of them --
            all cores must be loaded at runtime!

    content
        The data that's loaded into a :term:`core`,
        usually a :term:`ROM` containing a game.

    core
        An application wrapped in a library that exports the :term:`libretro` API.
        Usually an emulator, but sometimes a game engine or media player.
        Libretro cores are distributed as dynamically-loaded libraries on most platforms,
        including all those supported by libretro.py.

    driver
    backend
        An object that implements a subset of the :term:`libretro` API
        in terms of the :term:`protocol`\s defined in :mod:`libretro.drivers`.

        .. tip::
            libretro.py borrows this idea from :term:`RetroArch`,
            which uses this term similarly;
            most of its subsystems have multiple implementations
            that can be swapped out at runtime without the :term:`core` noticing.

            For example, the Windows build of RetroArch can use WASAPI or DirectAudio for sound output;
            both backends implement the same internal interface.


    environment call
    envcall
        A :term:`callback` function exposed to a :term:`core`
        that queries, modifies, or provides an interface to
        the :term:`frontend`'s runtime environment.

        All envcalls are invoked through the callback
        passed to :meth:`.Core.set_environment`
        (or equivalently, :c:type:`retro_environment_t`).

    frontend
        An application that loads and runs :term:`libretro` :term:`core`\s.
        :term:`RetroArch` is the most well-known libretro frontend,
        but many others exist.

    libretro
        A common interface between the :term:`frontend` and the :term:`core`;
        exposing a game or emulator with this interface
        allows it to benefit from a frontend's supported features
        without the author having to implement it themselves.
        Similar APIs such as `BizHawk <https://bizhawk.org/>`_
        and `Jolly Good <https://jgemu.gitlab.io>`_ exist,
        but these fall outside the scope of libretro.py.

    libretro.h
        The specific C header that defines the :term:`libretro` interface.
        Almost all types in :mod:`libretro.api` are based on this header.

        .. seealso::
            `libretro.h`_ on GitHub

    port
        A "slot" that accepts input from an abstract device like the :term:`RetroPad`.
        These usually correspond to an emulated platform's controller ports,
        but not necessarily.

    protocol
        Python term for an interface.
        It's convenient to define one as a :class:`~typing.Protocol` subclass,
        but not usually required.

    RetroArch
        RetroArch is the reference implementation of a libretro :term:`frontend`.
        Though it's the most popular, others exist -- including libretro.py!

    RetroPad
    gamepad
    joypad
    joystick
        The abstraction over a gamepad used by libretro.
        Modeled after a SNES controller with analog triggers and joysticks.
        All cores that use gamepads specify their input in terms of RetroPad buttons.

    ROM
    ROM image
    disk image
    dump
    ISO
        A digital backup of a game's **r**\ead-**o**\nly **m**\emory,
        including all of its code and data.
        Most :term:`core`\s accept one or more of these as :term:`content`.
        Sometimes called an ISO or a dump,
        especially for disk-based media.

        .. note::
            Although there are technical nuances in how these terms are used,
            the distinctions aren't relevant to libretro.py unless otherwise noted.


    subsystem
        A secondary platform that augments the primary platform a core emulates.

.. _libretro.h: https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h