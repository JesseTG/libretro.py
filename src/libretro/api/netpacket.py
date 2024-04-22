from ctypes import CFUNCTYPE, Structure, c_bool, c_int, c_size_t, c_uint16, c_void_p
from dataclasses import dataclass
from enum import IntFlag

from libretro.api._utils import FieldsFromTypeHints

RETRO_NETPACKET_UNRELIABLE = 0
RETRO_NETPACKET_RELIABLE = 1 << 0
RETRO_NETPACKET_UNSEQUENCED = 1 << 1
RETRO_NETPACKET_FLUSH_HINT = 1 << 2
RETRO_NETPACKET_BROADCAST = 0xFFFF

retro_netpacket_send_t = CFUNCTYPE(None, c_int, c_void_p, c_size_t, c_uint16, c_bool)
retro_netpacket_start_t = CFUNCTYPE(None, c_uint16, retro_netpacket_send_t)
retro_netpacket_receive_t = CFUNCTYPE(None, c_void_p, c_size_t, c_uint16)
retro_netpacket_stop_t = CFUNCTYPE(None)
retro_netpacket_poll_t = CFUNCTYPE(None)
retro_netpacket_poll_receive_t = CFUNCTYPE(None)
retro_netpacket_connected_t = CFUNCTYPE(c_bool, c_uint16)
retro_netpacket_disconnected_t = CFUNCTYPE(None, c_uint16)


class NetpacketFlags(IntFlag):
    UNRELIABLE = RETRO_NETPACKET_UNRELIABLE
    RELIABLE = RETRO_NETPACKET_RELIABLE
    UNSEQUENCED = RETRO_NETPACKET_UNSEQUENCED
    FLUSH_HINT = RETRO_NETPACKET_FLUSH_HINT


BROADCAST = RETRO_NETPACKET_BROADCAST


@dataclass(init=False)
class retro_netpacket_callback(Structure, metaclass=FieldsFromTypeHints):
    start: retro_netpacket_start_t
    receive: retro_netpacket_receive_t
    stop: retro_netpacket_stop_t
    poll: retro_netpacket_poll_t
    connected: retro_netpacket_connected_t
    disconnected: retro_netpacket_disconnected_t

    def __deepcopy__(self, _):
        return retro_netpacket_callback(
            self.start,
            self.receive,
            self.stop,
            self.poll,
            self.connected,
            self.disconnected,
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
