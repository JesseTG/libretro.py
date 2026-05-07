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
"""
Send a network packet to one or all connected players.

Registered by the :term:`frontend` and called by the :term:`core`.
A single packet may carry up to 64 KB of data.

:param flags: A bitmask of :class:`.NetpacketFlags` values
    that controls reliability, sequencing, and flushing.
:param buf: A :class:`.c_void_ptr` to the packet data,
    or :obj:`None` (combined with ``len`` of ``0``) to flush previously buffered packets.
:param len: Length of the data in ``buf``, in bytes.
:param client_id: Recipient player's client ID,
    or :data:`BROADCAST` to send to every connected player.

Corresponds to :c:type:`retro_netpacket_send_t` in ``libretro.h``.
"""

retro_netpacket_receive_t = TypedFunctionPointer[
    None, [c_void_ptr, CIntArg[c_size_t], CIntArg[c_uint16]]
]
"""
Deliver a packet received from another player to the core.

Registered by the :term:`core` and called by the :term:`frontend`
when a packet arrives from another player.

:param buf: A :class:`.c_void_ptr` to the received packet data.
:param len: Length of the packet in ``buf``, in bytes.
:param client_id: Client ID of the player that sent the packet.

Corresponds to :c:type:`retro_netpacket_receive_t` in ``libretro.h``.
"""

retro_netpacket_stop_t = TypedFunctionPointer[None, []]
"""
Notify the core that the multiplayer session has ended.

Registered by the :term:`core` and called by the :term:`frontend`.
After this call returns, the function pointers passed to
:c:type:`retro_netpacket_start_t` are no longer valid.

Corresponds to :c:type:`retro_netpacket_stop_t` in ``libretro.h``.
"""

retro_netpacket_poll_t = TypedFunctionPointer[None, []]
"""
Allow the core to send packets between calls to :c:func:`retro_run`.

Registered by the :term:`core` and called by the :term:`frontend`
once per frame to update the multiplayer session.

Corresponds to :c:type:`retro_netpacket_poll_t` in ``libretro.h``.
"""

retro_netpacket_poll_receive_t = TypedFunctionPointer[None, []]
"""
Drain any pending incoming packets without waiting for the end of the frame.

Registered by the :term:`frontend` and called by the :term:`core`
to receive packets immediately rather than waiting for the next frame.

Corresponds to :c:type:`retro_netpacket_poll_receive_t` in ``libretro.h``.
"""

retro_netpacket_connected_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint16]]]
"""
Notify the host's core that a new player has connected.

Registered by the :term:`core` and called by the :term:`frontend`
on the host side only.
The core may reject the new player by returning :obj:`False`.

:param client_id: Client ID of the newly-connected player.
:return: :obj:`True` to accept the connection,
    :obj:`False` to drop the player.

Corresponds to :c:type:`retro_netpacket_connected_t` in ``libretro.h``.
"""

retro_netpacket_disconnected_t = TypedFunctionPointer[None, [CIntArg[c_uint16]]]
"""
Notify the host's core that a player has disconnected.

Registered by the :term:`core` and called by the :term:`frontend`
on the host side only.

:param client_id: Client ID of the player that disconnected.

Corresponds to :c:type:`retro_netpacket_disconnected_t` in ``libretro.h``.
"""

retro_netpacket_start_t = TypedFunctionPointer[
    None, [CIntArg[c_uint16], retro_netpacket_send_t, retro_netpacket_poll_receive_t]
]
"""
Notify the core that a multiplayer session has started.

Registered by the :term:`core` and called by the :term:`frontend`
once the local player has joined the session.
The core should retain ``send_fn`` (and optionally ``poll_receive_fn``)
for use until :c:type:`retro_netpacket_stop_t` is called.

:param client_id: Local player's client ID;
    ``0`` if the local player is the host.
:param send_fn: A :c:type:`retro_netpacket_send_t` that the core uses to send packets.
:param poll_receive_fn: A :c:type:`retro_netpacket_poll_receive_t`
    that the core uses for synchronous receives.

Corresponds to :c:type:`retro_netpacket_start_t` in ``libretro.h``.
"""


class NetpacketFlags(IntFlag):
    """
    Flags controlling network packet delivery.

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
    """
    Corresponds to :c:type:`retro_netpacket_callback` in ``libretro.h``.

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
        """
        Return a deep copy of this object, including all strings.
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
