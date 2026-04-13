from ctypes import Structure, c_bool, c_int, c_int16, c_size_t, c_uint, c_uint64
from dataclasses import dataclass

from libretro.ctypes import CBoolArg, CIntArg, TypedFunctionPointer, TypedPointer

RETRO_MICROPHONE_INTERFACE_VERSION = 1
INTERFACE_VERSION = RETRO_MICROPHONE_INTERFACE_VERSION


@dataclass(init=False, slots=True)
class retro_microphone(Structure):
    id: int

    _fields_ = (("id", c_uint64),)


@dataclass(init=False, slots=True)
class retro_microphone_params(Structure):
    rate: int

    _fields_ = (("rate", c_uint),)

    def __deepcopy__(self, _):
        return retro_microphone_params(self.rate)


retro_open_mic_t = TypedFunctionPointer[
    TypedPointer[retro_microphone], [TypedPointer[retro_microphone_params]]
]
retro_close_mic_t = TypedFunctionPointer[None, [TypedPointer[retro_microphone]]]
retro_get_mic_params_t = TypedFunctionPointer[
    c_bool, [TypedPointer[retro_microphone], TypedPointer[retro_microphone_params]]
]
retro_set_mic_state_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_microphone], CBoolArg]]
retro_get_mic_state_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_microphone]]]
retro_read_mic_t = TypedFunctionPointer[
    c_int, [TypedPointer[retro_microphone], TypedPointer[c_int16], CIntArg[c_size_t]]
]


@dataclass(init=False, slots=True)
class retro_microphone_interface(Structure):
    interface_version: int
    open_mic: retro_open_mic_t | None
    close_mic: retro_close_mic_t | None
    get_params: retro_get_mic_params_t | None
    set_mic_state: retro_set_mic_state_t | None
    get_mic_state: retro_get_mic_state_t | None
    read_mic: retro_read_mic_t | None

    _fields_ = (
        ("interface_version", c_uint),
        ("open_mic", retro_open_mic_t),
        ("close_mic", retro_close_mic_t),
        ("get_params", retro_get_mic_params_t),
        ("set_mic_state", retro_set_mic_state_t),
        ("get_mic_state", retro_get_mic_state_t),
        ("read_mic", retro_read_mic_t),
    )

    def __init__(
        self,
        interface_version: int,
        open_mic: retro_open_mic_t | None = None,
        close_mic: retro_close_mic_t | None = None,
        get_params: retro_get_mic_params_t | None = None,
        set_mic_state: retro_set_mic_state_t | None = None,
        get_mic_state: retro_get_mic_state_t | None = None,
        read_mic: retro_read_mic_t | None = None,
    ):
        self.interface_version = interface_version
        self.open_mic = open_mic or retro_open_mic_t()
        self.close_mic = close_mic or retro_close_mic_t()
        self.get_params = get_params or retro_get_mic_params_t()
        self.set_mic_state = set_mic_state or retro_set_mic_state_t()
        self.get_mic_state = get_mic_state or retro_get_mic_state_t()
        self.read_mic = read_mic or retro_read_mic_t()

    def __deepcopy__(self, _):
        return retro_microphone_interface(
            self.interface_version,
            self.open_mic,
            self.close_mic,
            self.get_params,
            self.set_mic_state,
            self.get_mic_state,
            self.read_mic,
        )


__all__ = [
    "INTERFACE_VERSION",
    "retro_microphone",
    "retro_microphone_params",
    "retro_open_mic_t",
    "retro_close_mic_t",
    "retro_get_mic_params_t",
    "retro_set_mic_state_t",
    "retro_get_mic_state_t",
    "retro_read_mic_t",
    "retro_microphone_interface",
]
