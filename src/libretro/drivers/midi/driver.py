from abc import abstractmethod
from ctypes import c_uint8
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from warnings import deprecated

from libretro.api.midi import (
    retro_midi_flush_t,
    retro_midi_input_enabled_t,
    retro_midi_interface,
    retro_midi_output_enabled_t,
    retro_midi_read_t,
    retro_midi_write_t,
)

if TYPE_CHECKING:
    from libretro.typing import IntPointer


@runtime_checkable
class MidiDriver(Protocol):
    @property
    @deprecated("Set the function pointers in the EnvironmentDriver instead of the MidiDriver")
    def _as_parameter_(self) -> retro_midi_interface:
        return retro_midi_interface(
            input_enabled=retro_midi_input_enabled_t(self.__input_enabled),
            output_enabled=retro_midi_output_enabled_t(self.__output_enabled),
            read=retro_midi_read_t(self.__read),
            write=retro_midi_write_t(self.__write),
            flush=retro_midi_flush_t(self.__flush),
        )

    @property
    @abstractmethod
    def input_enabled(self) -> bool: ...

    @property
    @abstractmethod
    def output_enabled(self) -> bool: ...

    @abstractmethod
    def read(self) -> int | None: ...

    @abstractmethod
    def write(self, byte: int, delta_time: int) -> bool: ...

    @abstractmethod
    def flush(self) -> bool: ...

    def __input_enabled(self) -> bool:
        return self.input_enabled

    def __output_enabled(self) -> bool:
        return self.output_enabled

    def __read(self, byte: IntPointer[c_uint8]) -> bool:
        if not byte:
            return False

        if not self.input_enabled:
            return False

        match self.read():
            case int(i):
                byte[0] = i
                return True
            case None:
                return False
            case e:
                raise TypeError(f"Expected an int or None, got: {type(e).__name__}")

    def __write(self, byte: int, delta_time: int) -> bool:
        if not self.output_enabled:
            return False

        return self.write(byte, delta_time)

    def __flush(self) -> bool:
        return self.flush()


__all__ = ["MidiDriver"]
