from abc import abstractmethod
from typing import NewType, Protocol, runtime_checkable

import libretro.api.netpacket
from libretro.api.netpacket import NetpacketFlags, retro_netpacket_callback

ClientID = NewType("ClientID", int)

LOCAL = ClientID(0)
BROADCAST = ClientID(libretro.api.netpacket.BROADCAST)


@runtime_checkable
class NetpacketDriver(Protocol):
    @property
    @abstractmethod
    def callback(self) -> retro_netpacket_callback | None: ...

    @callback.setter
    @abstractmethod
    def callback(self, value: retro_netpacket_callback) -> None: ...

    @callback.deleter
    @abstractmethod
    def callback(self) -> None: ...

    @property
    @abstractmethod
    def version(self) -> bytes | None: ...

    @version.setter
    @abstractmethod
    def version(self, value: bytes) -> None: ...

    @version.deleter
    @abstractmethod
    def version(self) -> None: ...

    @abstractmethod
    def start(self, client_id: ClientID) -> None: ...

    @abstractmethod
    def receive(self, buf: memoryview, client_id: ClientID) -> None: ...

    @abstractmethod
    def stop(self, client_id: ClientID) -> None: ...

    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def connected(self, client_id: ClientID) -> bool: ...

    @abstractmethod
    def disconnected(self, client_id: ClientID) -> None: ...

    @abstractmethod
    def _send(self, flags: NetpacketFlags, buf: memoryview, client_id: ClientID) -> None: ...

    @abstractmethod
    def _poll_receive(self) -> None: ...


__all__ = ["NetpacketDriver"]
