from abc import abstractmethod
from collections import deque
from collections.abc import Sequence
from ctypes import POINTER, byref, c_int16, c_void_p, cast, memmove, sizeof
from typing import NamedTuple, Protocol, runtime_checkable

from libretro.api._utils import memoryview_at
from libretro.api.microphone import (
    retro_close_mic_t,
    retro_get_mic_params_t,
    retro_get_mic_state_t,
    retro_microphone,
    retro_microphone_interface,
    retro_microphone_params,
    retro_open_mic_t,
    retro_read_mic_t,
    retro_set_mic_state_t,
)


@runtime_checkable
class Microphone(Protocol):
    @abstractmethod
    def __init__(self, params: retro_microphone_params | None):
        self._as_parameter_ = id(self)

    def __del__(self) -> None:
        self.close()

    @abstractmethod
    def close(self) -> None: ...

    @property
    @abstractmethod
    def params(self) -> retro_microphone_params | None: ...

    @abstractmethod
    def read(self, frames: int) -> Sequence[int]: ...

    @property
    @abstractmethod
    def state(self) -> bool: ...

    @state.setter
    @abstractmethod
    def state(self, value: bool) -> None: ...


@runtime_checkable
class MicrophoneDriver(Protocol):
    # We want to keep the samples in a queue so that generators
    # don't have to be mindful of yielding the exact right amount of samples
    class __MicHandle(NamedTuple):
        handle: Microphone
        buffer: deque[int]

    @abstractmethod
    def __init__(self):
        interface = retro_microphone_interface()
        interface.interface_version = self.version
        interface.open_mic = retro_open_mic_t(self.__open_mic)
        interface.close_mic = retro_close_mic_t(self.__close_mic)
        interface.get_params = retro_get_mic_params_t(self.__get_params)
        interface.set_mic_state = retro_set_mic_state_t(self.__set_state)
        interface.get_mic_state = retro_get_mic_state_t(self.__get_state)
        interface.read_mic = retro_read_mic_t(self.__read_mic)
        self.__microphones: dict[int, MicrophoneDriver.__MicHandle] = {}
        self._as_parameter_ = interface

    @property
    @abstractmethod
    def version(self) -> int: ...

    @abstractmethod
    def open_mic(self, params: retro_microphone_params | None) -> Microphone: ...

    def __open_mic(self, params: POINTER(retro_microphone_params)) -> POINTER(retro_microphone):
        mic_params: retro_microphone_params | None = params[0] if params else None

        mic = self.open_mic(mic_params)
        if not mic:
            return None

        if not isinstance(mic, Microphone):
            raise TypeError(f"Expected a Microphone, got {type(mic).__name__}")

        address = id(mic)
        self.__microphones[address] = MicrophoneDriver.__MicHandle(mic, deque())

        return address

    def __close_mic(self, mic: POINTER(retro_microphone)) -> None:
        if not mic:
            return

        try:
            address: int = cast(mic, c_void_p).value
            handle = self.__microphones.pop(address, None)
            if not handle:
                return

            assert isinstance(handle, MicrophoneDriver.__MicHandle)
            assert isinstance(handle.handle, Microphone)

            handle.handle.close()
            del handle
        except Exception as e:
            # TODO: Log error
            return

    def __get_params(
        self, mic: POINTER(retro_microphone), params: POINTER(retro_microphone_params)
    ) -> bool:
        if not mic or not params:
            return False

        try:
            address: int = cast(mic, c_void_p).value
            handle = self.__microphones.get(address, None)
            if not handle:
                return False

            assert isinstance(handle, MicrophoneDriver.__MicHandle)
            assert isinstance(handle.handle, Microphone)
            returned_params = handle.handle.params

            if not returned_params:
                return False

            if not isinstance(returned_params, retro_microphone_params):
                raise TypeError(
                    f"Expected a retro_microphone_params, got {type(returned_params).__name__}"
                )

            memmove(params, byref(returned_params), sizeof(retro_microphone_params))
            return True
        except Exception as e:
            # TODO: Log error
            return False

    def __set_state(self, mic: POINTER(retro_microphone), state: bool) -> bool:
        if not mic:
            return False

        try:
            address: int = cast(mic, c_void_p).value
            handle = self.__microphones.get(address, None)
            if not handle:
                return False

            assert isinstance(handle, MicrophoneDriver.__MicHandle)
            assert isinstance(handle.handle, Microphone)
            handle.handle.state = state
            return True
        except Exception as e:
            # TODO: Log error
            return False

    def __get_state(self, mic: POINTER(retro_microphone)) -> bool:
        if not mic:
            return False

        try:
            address: int = cast(mic, c_void_p).value
            handle = self.__microphones.get(address, None)
            if not handle:
                return False

            assert isinstance(handle, MicrophoneDriver.__MicHandle)
            assert isinstance(handle.handle, Microphone)
            return handle.handle.state
        except Exception as e:
            # TODO: Log error
            return False

    def __read_mic(
        self, mic: POINTER(retro_microphone), frames: POINTER(c_int16), num_samples: int
    ) -> int:
        if not mic or not frames:
            return -1

        try:
            address: int = cast(mic, c_void_p).value
            handle = self.__microphones.get(address, None)
            if not handle:
                return -1

            assert isinstance(handle, MicrophoneDriver.__MicHandle)
            assert isinstance(handle.handle, Microphone)
            assert num_samples >= 0

            if not handle.handle.state:
                return -1

            if not num_samples:
                return 0

            new_samples = handle.handle.read(num_samples)
            if new_samples:
                # If the generator yielded any samples...
                handle.buffer.extendleft(new_samples)

            byteview = memoryview_at(frames, num_samples * sizeof(c_int16))
            # First get a view of the bytes so we can cast it to a view of 16-bit ints
            frameview = byteview.cast("h")  # signed 16-bit int
            assert len(frameview) == num_samples

            samples_to_give = min(num_samples, len(handle.buffer))
            for i in range(samples_to_give):
                frameview[i] = handle.buffer.pop()

            return samples_to_give
        except Exception as e:
            # TODO: Log error
            return -1


__all__ = ["Microphone", "MicrophoneDriver"]
