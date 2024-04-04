from ctypes import CFUNCTYPE, c_bool, c_int, c_size_t, c_uint16, c_void_p, Structure

from .._utils import FieldsFromTypeHints

retro_netpacket_send_t = CFUNCTYPE(None, c_int, c_void_p, c_size_t, c_uint16, c_bool)
retro_netpacket_start_t = CFUNCTYPE(None, c_uint16, retro_netpacket_send_t)
retro_netpacket_receive_t = CFUNCTYPE(None, c_void_p, c_size_t, c_uint16)
retro_netpacket_stop_t = CFUNCTYPE(None)
retro_netpacket_poll_t = CFUNCTYPE(None)
retro_netpacket_connected_t = CFUNCTYPE(c_bool, c_uint16)
retro_netpacket_disconnected_t = CFUNCTYPE(None, c_uint16)


class retro_netpacket_callback(Structure, metaclass=FieldsFromTypeHints):
    start: retro_netpacket_start_t
    receive: retro_netpacket_receive_t
    stop: retro_netpacket_stop_t
    poll: retro_netpacket_poll_t
    connected: retro_netpacket_connected_t
    disconnected: retro_netpacket_disconnected_t


__all__ = [
    "retro_netpacket_callback",
    'retro_netpacket_send_t',
    'retro_netpacket_start_t',
    'retro_netpacket_receive_t',
    'retro_netpacket_stop_t',
    'retro_netpacket_poll_t',
    'retro_netpacket_connected_t',
    'retro_netpacket_disconnected_t',
]