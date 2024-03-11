import mmap
from contextlib import contextmanager
from ctypes import *
from os import PathLike
from typing import Callable

from .retro import retro_device_power, PowerState, RETRO_POWERSTATE_NO_ESTIMATE


def full_power() -> retro_device_power:
    return retro_device_power(PowerState.PLUGGED_IN, RETRO_POWERSTATE_NO_ESTIMATE, 100)


def as_bytes(value: str | bytes | None) -> bytes | None:
    if isinstance(value, str):
        return value.encode('utf-8')
    return value


def array_from_null_terminated(ptr, when: Callable[[Structure], bool]) -> list[Structure]:
    result: list[Structure] = []
    i = 0
    while when(ptr[i]):
        result.append(ptr[i])
        i += 1

    return result


@contextmanager
def mmap_file(path: str | PathLike):
    with open(path, "r+b", buffering=0) as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY) as m:
            view = memoryview(m)
            yield view
            view.release()
            # If we don't release the memoryview manually,
            # we'll get a BufferError when the context manager exits
        f.close()


# When https://github.com/python/cpython/issues/112015 is merged,
# use ctypes.memoryview_at instead of this hack
# taken from https://stackoverflow.com/a/72968176/1089957
pythonapi.PyMemoryView_FromMemory.argtypes = (c_char_p, c_ssize_t, c_int)
pythonapi.PyMemoryView_FromMemory.restype = py_object


def memoryview_at(address: c_char_p | c_void_p | int, size: c_ssize_t | int, readonly=False):
    flags = c_int(0x100 if readonly else 0x200)
    return pythonapi.PyMemoryView_FromMemory(cast(address, c_char_p), c_ssize_t(size), flags)
