from ctypes import Structure, c_bool, c_char_p, c_int, c_size_t, c_uint16
from dataclasses import dataclass
from enum import IntFlag

from libretro.typing import CBoolArg, CIntArg, TypedFunctionPointer, c_void_ptr

RETRO_NETPACKET_UNRELIABLE = 0
RETRO_NETPACKET_RELIABLE = 1 << 0
RETRO_NETPACKET_UNSEQUENCED = 1 << 1
RETRO_NETPACKET_FLUSH_HINT = 1 << 2
RETRO_NETPACKET_BROADCAST = 0xFFFF


retro_netpacket_send_t = TypedFunctionPointer[
    None, [CIntArg[c_int], c_void_ptr, CIntArg[c_size_t], CIntArg[c_uint16], CBoolArg]
]
retro_netpacket_receive_t = TypedFunctionPointer[
    None, [c_void_ptr, CIntArg[c_size_t], CIntArg[c_uint16]]
]
retro_netpacket_stop_t = TypedFunctionPointer[None, []]
retro_netpacket_poll_t = TypedFunctionPointer[None, []]
retro_netpacket_poll_receive_t = TypedFunctionPointer[None, []]
retro_netpacket_connected_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint16]]]
retro_netpacket_disconnected_t = TypedFunctionPointer[None, [CIntArg[c_uint16]]]
retro_netpacket_start_t = TypedFunctionPointer[
    None, [CIntArg[c_uint16], retro_netpacket_send_t, retro_netpacket_poll_receive_t]
]


class NetpacketFlags(IntFlag):
    UNRELIABLE = RETRO_NETPACKET_UNRELIABLE
    RELIABLE = RETRO_NETPACKET_RELIABLE
    UNSEQUENCED = RETRO_NETPACKET_UNSEQUENCED
    FLUSH_HINT = RETRO_NETPACKET_FLUSH_HINT


BROADCAST = RETRO_NETPACKET_BROADCAST


@dataclass(init=False, slots=True)
class retro_netpacket_callback(Structure):
    start: retro_netpacket_start_t | None
    receive: retro_netpacket_receive_t | None
    stop: retro_netpacket_stop_t | None
    poll: retro_netpacket_poll_t | None
    connected: retro_netpacket_connected_t | None
    disconnected: retro_netpacket_disconnected_t | None
    protocol_version: bytes | None

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
