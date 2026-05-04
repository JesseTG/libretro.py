"""
Network packet exchange interface types for multiplayer.

.. seealso:: :mod:`libretro.drivers.netpacket`
"""

from ctypes import Structure, c_bool, c_char_p, c_int, c_size_t, c_uint16
from dataclasses import dataclass
from enum import IntFlag

from libretro.ctypes import CBoolArg, CIntArg, TypedFunctionPointer, c_void_ptr

RETRO_NETPACKET_UNRELIABLE = 0
RETRO_NETPACKET_RELIABLE = 1 << 0
RETRO_NETPACKET_UNSEQUENCED = 1 << 1
RETRO_NETPACKET_FLUSH_HINT = 1 << 2
RETRO_NETPACKET_BROADCAST = 0xFFFF


retro_netpacket_send_t = TypedFunctionPointer[
    None, [CIntArg[c_int], c_void_ptr, CIntArg[c_size_t], CIntArg[c_uint16], CBoolArg]
]
"""Sends a network packet to a client."""

retro_netpacket_receive_t = TypedFunctionPointer[
    None, [c_void_ptr, CIntArg[c_size_t], CIntArg[c_uint16]]
]
"""Called when a network packet is received."""

retro_netpacket_stop_t = TypedFunctionPointer[None, []]
"""Called when the network session is stopped."""

retro_netpacket_poll_t = TypedFunctionPointer[None, []]
"""Called to poll for network events."""

retro_netpacket_poll_receive_t = TypedFunctionPointer[None, []]
"""Called to poll for received packets."""

retro_netpacket_connected_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint16]]]
"""Called when a client connects. Returns ``True`` to accept."""

retro_netpacket_disconnected_t = TypedFunctionPointer[None, [CIntArg[c_uint16]]]
"""Called when a client disconnects."""

retro_netpacket_start_t = TypedFunctionPointer[
    None, [CIntArg[c_uint16], retro_netpacket_send_t, retro_netpacket_poll_receive_t]
]
"""Called to start the network session with a client ID, send function, and poll function."""


class NetpacketFlags(IntFlag):
    """Flags controlling network packet delivery.

    >>> from libretro.api import NetpacketFlags
    >>> NetpacketFlags.RELIABLE
    <NetpacketFlags.RELIABLE: 1>
    """

    UNRELIABLE = RETRO_NETPACKET_UNRELIABLE
    RELIABLE = RETRO_NETPACKET_RELIABLE
    UNSEQUENCED = RETRO_NETPACKET_UNSEQUENCED
    FLUSH_HINT = RETRO_NETPACKET_FLUSH_HINT


BROADCAST = RETRO_NETPACKET_BROADCAST
"""Client ID that targets all connected clients."""


@dataclass(init=False, slots=True)
class retro_netpacket_callback(Structure):
    """Corresponds to :c:type:`retro_netpacket_callback` in ``libretro.h``.

    A set of callbacks for network packet exchange.

    >>> from libretro.api import retro_netpacket_callback
    >>> cb = retro_netpacket_callback()
    >>> cb.start is None
    True
    """

    start: retro_netpacket_start_t | None
    """Called when a multiplayer session starts."""
    receive: retro_netpacket_receive_t | None
    """Called when a network packet is received."""
    stop: retro_netpacket_stop_t | None
    """Called when the multiplayer session ends. Optional."""
    poll: retro_netpacket_poll_t | None
    """Called each frame to poll for network events. Optional."""
    connected: retro_netpacket_connected_t | None
    """Called when a new player connects. Host only. Optional."""
    disconnected: retro_netpacket_disconnected_t | None
    """Called when a player disconnects. Host only. Optional."""
    protocol_version: bytes | None
    """Protocol version string for compatibility checks. Optional."""

    _fields_ = (
        ("start", retro_netpacket_start_t),
        ("receive", retro_netpacket_receive_t),
        ("stop", retro_netpacket_stop_t),
        ("poll", retro_netpacket_poll_t),
        ("connected", retro_netpacket_connected_t),
        ("disconnected", retro_netpacket_disconnected_t),
        ("protocol_version", c_char_p),
    )

    def __deepcopy__(self, _):
        """Returns a deep copy of this object, including all strings.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_netpacket_callback
        >>> copy.deepcopy(retro_netpacket_callback()).start is None
        True
        """
        return retro_netpacket_callback(
            self.start,
            self.receive,
            self.stop,
            self.poll,
            self.connected,
            self.disconnected,
            self.protocol_version,
        )


__all__ = [
    "retro_netpacket_callback",
    "retro_netpacket_send_t",
    "retro_netpacket_start_t",
    "retro_netpacket_receive_t",
    "retro_netpacket_stop_t",
    "retro_netpacket_poll_t",
    "retro_netpacket_connected_t",
    "retro_netpacket_disconnected_t",
    "NetpacketFlags",
    "BROADCAST",
]
