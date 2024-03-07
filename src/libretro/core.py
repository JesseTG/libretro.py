from ctypes import CDLL, cdll, pythonapi, c_char_p, c_ssize_t, c_int, py_object
from typing import *

from ._libretro import *
from .defs import *

# When https://github.com/python/cpython/issues/112015 is merged,
# use ctypes.memoryview_at instead of this hack
# taken from https://stackoverflow.com/a/72968176/1089957
pythonapi.PyMemoryView_FromMemory.argtypes = (c_char_p, c_ssize_t, c_int)
pythonapi.PyMemoryView_FromMemory.restype = py_object


# noinspection PyStatementEffect
def validate_core(core: CDLL) -> None:
    try:
        core.retro_set_environment
        core.retro_set_video_refresh
        core.retro_set_audio_sample
        core.retro_set_audio_sample_batch
        core.retro_set_input_poll
        core.retro_set_input_state
        core.retro_init
        core.retro_deinit
        core.retro_api_version
        core.retro_get_system_info
        core.retro_get_system_av_info
        core.retro_set_controller_port_device
        core.retro_reset
        core.retro_run
        core.retro_serialize_size
        core.retro_serialize
        core.retro_unserialize
        core.retro_cheat_reset
        core.retro_cheat_set
        core.retro_load_game
        core.retro_load_game_special
        core.retro_unload_game
        core.retro_get_region
        core.retro_get_memory_data
        core.retro_get_memory_size
    except AttributeError as e:
        raise ValueError(f"Couldn't find required symbol '{e.name}' from {core._name}") from e

# TODO: Implement context manager protocol
class Core:
    """
    A thin wrapper around a libretro core.
    Can be used to call the core's public interface,
    but does not manage its life cycle.
    """

    def __init__(self, core: CDLL | str):
        """
        Create a new Core instance.

        Parameters:
            core: The core to wrap. Can be a path to a shared library or a CDLL instance.
        """
        if isinstance(core, str):
            self._core = cdll.LoadLibrary(core)
        else:
            self._core = core

        validate_core(self._core)

        # Need to keep references to these objects to prevent them from being garbage collected,
        # otherwise the C function pointers to them will become invalid.
        self._environment: retro_environment_t | None = None
        self._video_refresh: retro_video_refresh_t | None = None
        self._audio_sample: retro_audio_sample_t | None = None
        self._audio_sample_batch: retro_audio_sample_batch_t | None = None
        self._input_poll: retro_input_poll_t | None = None
        self._input_state: retro_input_state_t | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del self._core
        return False

    def set_environment(self, env: retro_environment_t) -> None:
        self._environment = retro_environment_t(env)
        self._core.retro_set_environment(self._environment)

    def set_video_refresh(self, video: retro_video_refresh_t) -> None:
        self._video_refresh = retro_video_refresh_t(video)
        self._core.retro_set_video_refresh(self._video_refresh)

    def set_audio_sample(self, audio: retro_audio_sample_t) -> None:
        self._audio_sample = retro_audio_sample_t(audio)
        self._core.retro_set_audio_sample(self._audio_sample)

    def set_audio_sample_batch(self, audio: retro_audio_sample_batch_t) -> None:
        self._audio_sample_batch = retro_audio_sample_batch_t(audio)
        self._core.retro_set_audio_sample_batch(self._audio_sample_batch)

    def set_input_poll(self, poll: retro_input_poll_t) -> None:
        self._input_poll = retro_input_poll_t(poll)
        self._core.retro_set_input_poll(self._input_poll)

    def set_input_state(self, state: retro_input_state_t) -> None:
        self._input_state = retro_input_state_t(state)
        self._core.retro_set_input_state(self._input_state)

    def init(self):
        self._core.retro_init()

    def deinit(self):
        """
        Calls `retro_deinit` on the core.

        Note:
            This function is not implicitly called when the Core instance is deleted.
        """
        self._core.retro_deinit()

    def api_version(self) -> int:
        return self._core.retro_api_version()

    def get_system_info(self) -> retro_system_info:
        system_info = retro_system_info()
        self._core.retro_get_system_info(byref(system_info))
        return system_info

    def get_system_av_info(self) -> retro_system_av_info:
        system_av_info = retro_system_av_info()
        self._core.retro_get_system_av_info(byref(system_av_info))
        return system_av_info

    def set_controller_port_device(self, port: int, device: int):
        self._core.retro_set_controller_port_device(port, device)

    def reset(self):
        self._core.retro_reset()

    def run(self):
        self._core.retro_run()

    def serialize_size(self) -> int:
        return self._core.retro_serialize_size()

    def serialize(self, data: bytearray) -> bool:
        return self._core.retro_serialize(data, len(data))

    def unserialize(self, data: bytes | bytearray | memoryview) -> bool:
        return self._core.retro_unserialize(data, len(data))

    def cheat_reset(self):
        self._core.retro_cheat_reset()

    def cheat_set(self, index: int, enabled: bool, code: bytes | bytearray | memoryview):
        self._core.retro_cheat_set(index, enabled, code)

    def load_game(self, game: retro_game_info | None) -> bool:
        return self._core.retro_load_game(byref(game) if game else None)

    def load_game_special(self, game_type: int, info: Sequence[retro_game_info]) -> bool:
        return self._core.retro_load_game_special(game_type, info, len(info))

    def unload_game(self):
        self._core.retro_unload_game()

    def get_region(self) -> Region:
        return Region(self._core.retro_get_region())

    def get_memory_data(self, id: int) -> c_void_p | None:
        return self._core.retro_get_memory_data(id)

    def get_memory_size(self, id: int) -> int:
        return self._core.retro_get_memory_size(id)

    def get_memory(self, id: int) -> memoryview | None:
        data = self.get_memory_data(id)
        if not data:
            return None

        size = self.get_memory_size(id)
        return pythonapi.PyMemoryView_FromMemory(data, size, 0x200)
        # 0x200 = read/write, 0x100 = read-only


    @property
    def path(self) -> str:
        return self._core._name
