"""
:class:`~typing.Protocol` definition for input drivers.

.. seealso::

    :mod:`libretro.api.input`
        The matching :mod:`ctypes` types, device identifiers, and callback definitions.
"""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from libretro.api import (
    InputDevice,
    InputDeviceFlag,
    Key,
    KeyModifier,
    Port,
    retro_controller_description,
    retro_input_descriptor,
    retro_keyboard_callback,
)


@runtime_checkable
class InputDriver(Protocol):
    """
    Protocol for drivers that provide input device state to a core.

    .. seealso::

        :mod:`libretro.api.input`
            The matching :mod:`ctypes` types, device identifiers, and callback definitions.
    """

    @abstractmethod
    def poll(self) -> None:
        """
        Sample fresh input state for the upcoming frame.

        Called by the session once per frame before the core's
        :meth:`.Core.run` so subsequent :meth:`state` queries see consistent input.

        .. seealso::

            :data:`~libretro.api.input.retro_input_poll_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def state(self, port: Port, device: InputDevice, index: int, id: int) -> int:
        """
        Return the current state of a single input control.

        :param port: The input port being queried.
        :param device: The input device class registered to ``port``.
        :param index: Sub-device index (e.g. analog stick number).
        :param id: Button or axis identifier within the device class.
        :return: The control's current state, encoded per libretro's input conventions.

        .. seealso::

            :data:`~libretro.api.input.retro_input_state_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @property
    @abstractmethod
    def descriptors(self) -> Sequence[retro_input_descriptor] | None:
        """
        The input descriptors registered by the core, if any.

        Set by the core via ``RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS``
        to advertise the buttons and axes it actually consumes.

        :param descriptors: The sequence of descriptors registered by the core.
        :raises UnsupportedEnvCall: If this driver does not accept input descriptors.

        .. seealso::

            :class:`~libretro.api.input.retro_input_descriptor`
                The C struct that this attribute holds.
        """
        ...

    @descriptors.setter
    @abstractmethod
    def descriptors(self, descriptors: Sequence[retro_input_descriptor]) -> None:
        """See :attr:`descriptors`."""
        ...

    @property
    @abstractmethod
    def keyboard_callback(self) -> retro_keyboard_callback | None:
        """
        The keyboard callback registered by the core, if any.

        Set by the core via ``RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK``
        to receive key-down/key-up events.
        :obj:`None` if the core has not registered a keyboard callback.

        :param callback: The callback to register.
        :raises UnsupportedEnvCall: If this driver does not support keyboard input.

        .. seealso::

            :class:`~libretro.api.input.retro_keyboard_callback`
                The C struct registered by the core that contains this callback.
        """
        ...

    @keyboard_callback.setter
    @abstractmethod
    def keyboard_callback(self, callback: retro_keyboard_callback) -> None:
        """See :attr:`keyboard_callback`."""
        ...

    def keyboard_event(
        self, down: bool, keycode: Key, character: int | str | bytes, modifiers: KeyModifier
    ) -> None:
        """
        Forward a keyboard event to the registered :attr:`keyboard_callback`, if any.

        :param down: :obj:`True` for key-down, :obj:`False` for key-up.
        :param keycode: The libretro key identifier.
        :param character: The Unicode codepoint (or encoded form) produced by the key,
            for keys that produce text.
        :param modifiers: Bitmask of active modifier keys at the time of the event.
        """
        callback = self.keyboard_callback
        if callback:
            callback(down, keycode, character, modifiers)

    @property
    @abstractmethod
    def device_capabilities(self) -> InputDeviceFlag | None:
        """
        Bitmask of input device classes supported by this driver.

        Returned to the core in response to
        ``RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES``.
        :obj:`None` if the driver does not advertise device capabilities.

        :param capabilities: The capability bitmask to advertise.
        :raises UnsupportedEnvCall: If this driver does not advertise device capabilities.

        .. seealso::

            :class:`~libretro.api.input.InputDeviceFlag`
                The bit flags that compose this bitmask.
        """
        ...

    @device_capabilities.setter
    @abstractmethod
    def device_capabilities(self, capabilities: InputDeviceFlag) -> None:
        """See :attr:`device_capabilities`."""
        ...

    @device_capabilities.deleter
    @abstractmethod
    def device_capabilities(self) -> None:
        """See :attr:`device_capabilities`."""
        ...

    @property
    @abstractmethod
    def controller_info(self) -> Sequence[retro_controller_description] | None:
        """
        Per-port controller descriptions registered by the core, if any.

        Set by the core via ``RETRO_ENVIRONMENT_SET_CONTROLLER_INFO``
        to advertise the controllers each port can be configured to emulate.

        :param info: The controller descriptions registered by the core.
        :raises UnsupportedEnvCall: If this driver does not accept controller info.

        .. seealso::

            :class:`~libretro.api.input.retro_controller_description`
                The C struct that this attribute holds.
        """
        ...

    @controller_info.setter
    @abstractmethod
    def controller_info(self, info: Sequence[retro_controller_description]) -> None:
        """See :attr:`controller_info`."""
        ...

    @property
    @abstractmethod
    def bitmasks_supported(self) -> bool | None:
        """
        Whether the driver supports the joypad-bitmask state encoding.

        Returned to the core in response to ``RETRO_ENVIRONMENT_GET_INPUT_BITMASKS``.
        :obj:`None` if the driver does not advertise bitmask support either way.

        :param bitmask_supported: :obj:`True` if the driver supports joypad bitmasks.
        :raises UnsupportedEnvCall: If this driver does not advertise bitmask support.
        """
        ...

    @bitmasks_supported.setter
    @abstractmethod
    def bitmasks_supported(self, bitmask_supported: bool) -> None:
        """See :attr:`bitmasks_supported`."""
        ...

    @bitmasks_supported.deleter
    @abstractmethod
    def bitmasks_supported(self) -> None:
        """See :attr:`bitmasks_supported`."""
        ...

    @property
    @abstractmethod
    def max_users(self) -> int | None:
        """
        The maximum number of input ports this driver advertises to the core.

        Returned to the core in response to ``RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS``.
        :obj:`None` if the driver does not advertise a maximum.

        :param max_users: The maximum number of input ports to advertise.
        :raises UnsupportedEnvCall: If this driver does not advertise a maximum.
        """
        ...

    @max_users.setter
    @abstractmethod
    def max_users(self, max_users: int) -> None:
        """See :attr:`max_users`."""
        ...

    @max_users.deleter
    @abstractmethod
    def max_users(self) -> None:
        """See :attr:`max_users`."""
        ...


__all__ = ["InputDriver"]
