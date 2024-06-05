from socket import AddressFamily, SocketKind, socket

from libretro._typing import override
from libretro.api.netpacket import NetpacketFlags, retro_netpacket_callback

from .driver import ClientID, NetpacketDriver


class SocketNetpacketDriver(NetpacketDriver):
    def __init__(
        self, client_id: ClientID, family: AddressFamily, kind: SocketKind, proto=0
    ) -> None:
        self._socket = socket(family, kind)

    def __del__(self):
        self._socket.close()
        del self._socket

    @property
    @override
    def callback(self) -> retro_netpacket_callback | None: ...

    @callback.setter
    @override
    def callback(self, value: retro_netpacket_callback) -> None: ...

    @callback.deleter
    @override
    def callback(self) -> None: ...

    @property
    @override
    def version(self) -> bytes | None: ...

    @version.setter
    @override
    def version(self, value: bytes) -> None: ...

    @version.deleter
    @override
    def version(self) -> None: ...

    def start(self, client_id: ClientID) -> None:
        pass

    def receive(self, buf: memoryview, client_id: ClientID) -> None:
        pass

    def stop(self, client_id: ClientID) -> None:
        pass

    def poll(self) -> None:
        pass

    def connected(self, client_id: ClientID) -> bool:
        pass

    def disconnected(self, client_id: ClientID) -> None:
        pass

    def _send(self, flags: NetpacketFlags, buf: memoryview, client_id: ClientID) -> None:
        pass

    def _poll_receive(self) -> None:
        pass
