from ._utils import memoryview_at
from .defs import *


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

        try:
            self._core.retro_set_environment.argtypes = [retro_environment_t]
            self._core.retro_set_environment.restype = None

            self._core.retro_set_video_refresh.argtypes = [retro_video_refresh_t]
            self._core.retro_set_video_refresh.restype = None

            self._core.retro_set_audio_sample.argtypes = [retro_audio_sample_t]
            self._core.retro_set_audio_sample.restype = None

            self._core.retro_set_audio_sample_batch.argtypes = [retro_audio_sample_batch_t]
            self._core.retro_set_audio_sample_batch.restype = None

            self._core.retro_set_input_poll.argtypes = [retro_input_poll_t]
            self._core.retro_set_input_poll.restype = None

            self._core.retro_set_input_state.argtypes = [retro_input_state_t]
            self._core.retro_set_input_state.restype = None

            self._core.retro_init.argtypes = []
            self._core.retro_init.restype = None

            self._core.retro_deinit.argtypes = []
            self._core.retro_deinit.restype = None

            self._core.retro_api_version.argtypes = []
            self._core.retro_api_version.restype = c_uint

            self._core.retro_get_system_info.argtypes = [POINTER(retro_system_info)]
            self._core.retro_get_system_info.restype = None

            self._core.retro_get_system_av_info.argtypes = [POINTER(retro_system_av_info)]
            self._core.retro_get_system_av_info.restype = None

            self._core.retro_set_controller_port_device.argtypes = [c_uint, c_uint]
            self._core.retro_set_controller_port_device.restype = None

            self._core.retro_reset.argtypes = []
            self._core.retro_reset.restype = None

            self._core.retro_run.argtypes = []
            self._core.retro_run.restype = None

            self._core.retro_serialize_size.argtypes = []
            self._core.retro_serialize_size.restype = c_size_t

            self._core.retro_serialize.argtypes = [c_void_p, c_size_t]
            self._core.retro_serialize.restype = c_bool

            self._core.retro_unserialize.argtypes = [c_void_p, c_size_t]
            self._core.retro_unserialize.restype = c_bool

            self._core.retro_cheat_reset.argtypes = []
            self._core.retro_cheat_reset.restype = None

            self._core.retro_cheat_set.argtypes = [c_uint, c_bool, String]
            self._core.retro_cheat_set.restype = None

            self._core.retro_load_game.argtypes = [POINTER(retro_game_info)]
            self._core.retro_load_game.restype = c_bool

            self._core.retro_load_game_special.argtypes = [c_uint, POINTER(retro_game_info), c_size_t]
            self._core.retro_load_game_special.restype = c_bool

            self._core.retro_unload_game.argtypes = []
            self._core.retro_unload_game.restype = None

            self._core.retro_get_region.argtypes = []
            self._core.retro_get_region.restype = c_uint

            self._core.retro_get_memory_data.argtypes = [c_uint]
            self._core.retro_get_memory_data.restype = POINTER(c_ubyte)
            self._core.retro_get_memory_data.errcheck = lambda v, *a: cast(v, c_void_p)

            self._core.retro_get_memory_size.argtypes = [c_uint]
            self._core.retro_get_memory_size.restype = c_size_t
        except AttributeError as e:
            raise ValueError(f"Couldn't find required symbol '{e.name}' in {self._core._name}") from e

        # Need to keep references to these objects to prevent them from being garbage collected,
        # otherwise the C function pointers to them will become invalid.
        self._environment: retro_environment_t | None = None
        self._video_refresh: retro_video_refresh_t | None = None
        self._audio_sample: retro_audio_sample_t | None = None
        self._audio_sample_batch: retro_audio_sample_batch_t | None = None
        self._input_poll: retro_input_poll_t | None = None
        self._input_state: retro_input_state_t | None = None

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
        GameInfoArray: Array = retro_game_info * len(info)
        info_array = GameInfoArray(*info)
        return self._core.retro_load_game_special(game_type, info_array, len(info))

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
        return memoryview_at(data, size, readonly=True)

    @property
    def path(self) -> str:
        return self._core._name
