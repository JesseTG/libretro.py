"""
:class:`~typing.Protocol` definition for the network packet interface used by netplay-aware cores.

.. seealso::

    :mod:`libretro.api.netpacket`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from typing import NewType, Protocol, runtime_checkable

from libretro.api.netpacket import (
    RETRO_NETPACKET_BROADCAST,
    NetpacketFlags,
    retro_netpacket_callback,
)

ClientID = NewType("ClientID", int)

LOCAL = ClientID(0)
BROADCAST = ClientID(RETRO_NETPACKET_BROADCAST)


@runtime_checkable
class NetpacketDriver(Protocol):
    """
    Protocol for drivers that route the netplay packet callbacks of netplay-aware cores.

    .. seealso::

        :mod:`libretro.api.netpacket`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @property
    @abstractmethod
    def callback(self) -> retro_netpacket_callback | None:
        """
        The netplay packet callbacks registered by the core, if any.

        Set by the core via ``RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE``.
        :obj:`None` if the core has not registered netplay support.

        :param value: The callbacks struct registered by the core.
        :raises UnsupportedEnvCall: If this driver does not support netplay packets.

        .. seealso::

            :class:`~libretro.api.netpacket.retro_netpacket_callback`
                The C struct registered by the core that contains these callbacks.
        """
        ...

    @callback.setter
    @abstractmethod
    def callback(self, value: retro_netpacket_callback) -> None:
        """See :attr:`callback`."""
        ...

    @callback.deleter
    @abstractmethod
    def callback(self) -> None:
        """See :attr:`callback`."""
        ...

    @property
    @abstractmethod
    def version(self) -> bytes | None:
        """
        The netplay protocol version advertised by the core, if any.

        Used by the netplay layer to reject incompatible peers.

        :param value: The protocol version string to advertise.
        :raises UnsupportedEnvCall: If this driver does not advertise a protocol version.
        """
        ...

    @version.setter
    @abstractmethod
    def version(self, value: bytes) -> None:
        """See :attr:`version`."""
        ...

    @version.deleter
    @abstractmethod
    def version(self) -> None:
        """See :attr:`version`."""
        ...

    @abstractmethod
    def start(self, client_id: ClientID) -> None:
        """
        Notify the core that a netplay session has begun for ``client_id``.

        :param client_id: The client identifier whose session is starting.
        """
        ...

    @abstractmethod
    def receive(self, buf: memoryview, client_id: ClientID) -> None:
        """
        Deliver a received netplay packet to the core.

        :param buf: The packet payload.
        :param client_id: The client that sent the packet.
        """
        ...

    @abstractmethod
    def stop(self, client_id: ClientID) -> None:
        """
        Notify the core that the netplay session for ``client_id`` has ended.

        :param client_id: The client identifier whose session is ending.
        """
        ...

    @abstractmethod
    def poll(self) -> None:
        """Drain pending netplay packets and forward them to the core."""
        ...

    @abstractmethod
    def connected(self, client_id: ClientID) -> bool:
        """
        Notify the core that ``client_id`` has connected to the netplay session.

        :param client_id: The newly connected client.
        :return: :obj:`True` if the connection was accepted by the core.
        """
        ...

    @abstractmethod
    def disconnected(self, client_id: ClientID) -> None:
        """
        Notify the core that ``client_id`` has disconnected from the netplay session.

        :param client_id: The client that disconnected.
        """
        ...

    @abstractmethod
    def _send(self, flags: NetpacketFlags, buf: memoryview, client_id: ClientID) -> None:
        """
        Send a packet from the core to a peer.

        :param flags: Delivery flags such as reliability or ordering hints.
        :param buf: The packet payload to send.
        :param client_id: Recipient client, or :data:`BROADCAST` to send to all peers.
        """
        ...

    @abstractmethod
    def _poll_receive(self) -> None:
        """Pump pending netplay receive operations from the underlying transport."""
        ...


__all__ = ["NetpacketDriver"]
