from ctypes import CDLL
from typing import *

from ._libretro import *
from .defs import *

class Core:
    def __init__(self, core: CDLL):
        # TODO: Load the core when passed as a DLL, a file, or a path
        self._core: CDLL = core
        self._callbacks = None
        self._rotation = Rotation.NONE
        self._overscan = False

    def set_environment(self, env: retro_environment_t):
        self._core.retro_set_environment(env)

    def set_video_refresh(self, video: retro_video_refresh_t):
        self._core.retro_set_video_refresh(video)

    def set_audio_sample(self, audio: retro_audio_sample_t):
        self._core.retro_set_audio_sample(audio)

    def set_audio_sample_batch(self, audio: retro_audio_sample_batch_t):
        self._core.retro_set_audio_sample_batch(audio)

    def set_input_poll(self, poll: retro_input_poll_t):
        self._core.retro_set_input_poll(poll)

    def set_input_state(self, state: retro_input_state_t):
        self._core.retro_set_input_state(state)

    def init(self):
        self._core.retro_init()

    def deinit(self):
        self._core.retro_deinit()

    def api_version(self) -> int:
        return self._core.retro_api_version()

    def get_system_info(self) -> retro_system_info:
        pass

    def get_system_av_info(self) -> retro_system_av_info:
        pass

    def set_controller_port_device(self, port: int, device: int):
        self._core.retro_set_controller_port_device(port, device)

    def reset(self):
        self._core.retro_reset()

    def run(self):
        self._core.retro_run()

    def serialize_size(self) -> int:
        return self._core.retro_serialize_size()

    def serialize(self, data: bytearray) -> bool:
        pass

    def unserialize(self, data: bytes) -> bool:
        pass

    def cheat_reset(self):
        self._core.retro_cheat_reset()

    def cheat_set(self, index: int, enabled: bool, code: str) -> None:
        pass

    def load_game(self, game: retro_game_info) -> bool:
        pass

    def load_game_special(self, game_type: int, info: retro_game_info, num_info: int) -> bool:
        pass

    def unload_game(self) -> None:
        pass

    def get_region(self) -> int:
        return self._core.retro_get_region()

    def get_memory_data(self, id: int) -> Any:
        pass

    def get_memory_size(self, id: int) -> int:
        pass

    def _env(self, cmd: int, data: Any) -> bool:
        pass
