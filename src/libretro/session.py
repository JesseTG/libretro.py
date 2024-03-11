import itertools
import logging
import sys
import mmap
from contextlib import contextmanager
from ctypes import *

from .retro import retro_game_info
from .api.log import LogCallback, StandardLogger
from .api.message import MessageInterface, LoggerMessageInterface
from .core import Core
from .api.audio import AudioCallbacks, AudioState, ArrayAudioState
from .api.environment import EnvironmentCallback
from .api.input import *
from .api.video import VideoCallbacks, SoftwareVideoState, VideoState
from .defs import *

from ._utils import *

class _DoNotLoad: pass

DoNotLoad = _DoNotLoad()


class Session(EnvironmentCallback):
    def __init__(
            self,
            core: Core | str,
            audio: AudioState,
            input_state: InputState,
            video: VideoState,
            # TODO: Support for an env override function
            # TODO: Support for core options

            content: Content | SpecialContent | _DoNotLoad | None = None,
            overscan: bool = False,
            message: MessageInterface | None = None,
            system_dir: Directory | None = None,
            log_callback: LogCallback | None = None,
            core_assets_dir: Directory | None = None,
            save_dir: Directory | None = None,
            username: str | None = "libretro.py",
            language: Language = Language.ENGLISH,
            target_refresh_rate: float = 60.0,
            jit_capable: bool = True,
            device_power: DevicePower | None = full_power,
            playlist_dir: Directory | None = None
    ):
        if core is None:
            raise ValueError("Core cannot be None")

        if isinstance(core, Core):
            self._core = core
        else:
            self._core = Core(core)

        self._audio = audio
        self._input = input_state
        self._video = video
        self._content = content
        self._system_av_info: retro_system_av_info | None = None
        self._system_info: retro_system_info | None = None

        self._overscan = overscan
        self._message: MessageInterface | None = message
        self._is_shutdown: bool = False
        self._keyboard_callback: retro_keyboard_callback | None = None
        self._performance_level: int | None = None
        self._system_dir = as_bytes(system_dir)
        self._support_no_game: bool | None = None
        self._libretro_path: bytes = as_bytes(self._core.path)
        self._frame_time_callback: retro_frame_time_callback | None = None
        self._log_callback: LogCallback | None = log_callback
        self._core_assets_dir = as_bytes(core_assets_dir)
        self._save_dir = as_bytes(save_dir)
        self._proc_address_callback: retro_get_proc_address_interface | None = None
        self._subsystem_info: Sequence[retro_subsystem_info] | None = None
        self._memory_maps: retro_memory_map | None = None
        self._username = as_bytes(username)
        self._language = language
        self._supports_achievements: bool | None = None
        self._serialization_quirks: SerializationQuirks | None = None
        self._target_refresh_rate = target_refresh_rate
        self._fastforwarding_override: retro_fastforwarding_override | None = None
        self._content_info_override: Sequence[retro_system_content_info_override] | None = None
        self._throttle_state: retro_throttle_state | None = None
        self._savestate_context: SavestateContext | None = SavestateContext.NORMAL
        self._jit_capable = jit_capable
        self._device_power = device_power
        self._playlist_dir = as_bytes(playlist_dir)
        self._pending_callback_exceptions: list[BaseException] = []

    def __enter__(self):
        api_version = self._core.api_version()
        if api_version != RETRO_API_VERSION:
            raise RuntimeError(f"libretro.py is only compatible with API version {RETRO_API_VERSION}, but the core uses {api_version}")

        self._core.set_video_refresh(self._video.refresh)
        self._core.set_audio_sample(self._audio.audio_sample)
        self._core.set_audio_sample_batch(self._audio.audio_sample_batch)
        self._core.set_input_poll(self._input.poll)
        self._core.set_input_state(self._input.state)
        self._core.set_environment(self.environment)
        self._system_info = self._core.get_system_info()

        if self._system_info.library_name is None:
            raise RuntimeError("Core did not provide a library name")

        if self._system_info.library_version is None:
            raise RuntimeError("Core did not provide a library version")

        if self._system_info.valid_extensions is None:
            raise RuntimeError("Core did not provide valid extensions")

        self._core.init()

        # TODO: Enforce the condition given in retro_system_content_info_override
        # TODO: Enforce the contents of retro_subsystem_info (if any)

        need_fullpath = self._system_info.need_fullpath # TODO: Look through the overrides and subsystems to determine when this is true
        persistent_data = False # TODO: Look through the overrides and subsystems to determine when this is true
        loaded: bool = False
        match self._content:
            case _DoNotLoad():
                # Do nothing, we're testing something that doesn't need to load a game
                return self
            case retro_game_info(info) if need_fullpath:
                # For test cases that create a retro_game_info manually
                info: retro_game_info

                if not info.path:
                    raise ValueError("Core requires a full path, but none was provided")

                loaded = self._core.load_game(info)
            case retro_game_info(info) if not need_fullpath:
                # For test cases that create a retro_game_info manually
                if not info.data:
                    raise ValueError("Core wants retro_game_info to include data, but none was provided")

                loaded = self._core.load_game(info)
            case str(path) | PathLike(path) if need_fullpath:
                # For test cases with content that needs a full path, so no data is provided
                # (RetroArch does this)
                loaded = self._core.load_game(retro_game_info(path.encode(), None, 0, None))
            case str(path) | PathLike(path) if not need_fullpath:
                with mmap_file(path) as content:
                    # noinspection PyTypeChecker
                    # You can't directly get an address from a memoryview,
                    # so you need to resort to C-like casting
                    array_type: Array = c_ubyte * len(content)
                    buffer_array = array_type.from_buffer(content)

                    info = retro_game_info(path.encode(), addressof(buffer_array), len(content), None)
                    loaded = self._core.load_game(info)
                    del info
                    del buffer_array
                    del array_type
                    # Need to clear all outstanding pointers, or else mmap will raise a BufferError

            case bytes(rom) | bytearray(rom) | memoryview(rom):
                # For test cases that provide ROM data directly
                if need_fullpath:
                    raise ValueError("Core requires a full path, but none was provided")

                loaded = self._core.load_game(retro_game_info(None, rom, len(rom), None))
            case SpecialContent(content_type, special_content):
                if not self._subsystem_info:
                    raise RuntimeError("Subsystem content was provided, but core did not register subsystems")

                # TODO
                #loaded = self._core.load_game_special(content_type, content)
            case None:
                if not self._support_no_game:
                    raise RuntimeError("No content provided and core did not indicate support for no game.")

                loaded = self._core.load_game(None)

        if not loaded:
            raise RuntimeError("Failed to load game")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._content is not DoNotLoad:
            self._core.unload_game()
        self._core.deinit()
        del self._core
        return False

    @property
    def core(self) -> Core:
        return self._core

    @property
    def audio(self) -> AudioCallbacks:
        return self._audio

    @property
    def input(self) -> InputCallbacks:
        return self._input

    @property
    def video(self) -> VideoCallbacks:
        return self._video

    @property
    def message(self) -> MessageInterface | None:
        return self._message

    @property
    def system_directory(self) -> bytes | None:
        return self._system_dir

    @property
    def system_dir(self) -> bytes | None:
        return self._system_dir

    @property
    def support_no_game(self) -> bool | None:
        return self._support_no_game

    @property
    def log(self) -> LogCallback | None:
        return self._log_callback

    @property
    def save_directory(self) -> bytes | None:
        return self._save_dir

    @property
    def save_dir(self) -> bytes | None:
        return self._save_dir

    @property
    def proc_address_callback(self) -> retro_get_proc_address_interface | None:
        return self._proc_address_callback

    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        if self._proc_address_callback is None or sym is None:
            return None

        return self._proc_address_callback.get_proc_address(sym)

    @property
    def subsystems(self) -> Sequence[retro_subsystem_info] | None:
        return self._subsystem_info

    @property
    def support_achievements(self) -> bool | None:
        return self._supports_achievements

    @property
    def content_info_overrides(self) -> Sequence[retro_system_content_info_override] | None:
        return self._content_info_override

    def environment(self, cmd: EnvironmentCall, data: c_void_p) -> bool:
        # TODO: Allow overriding certain calls by passing a function to the constructor
        match cmd:
            case EnvironmentCall.SET_ROTATION:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_ROTATION doesn't accept NULL")

                rotation_ptr = cast(data, POINTER(c_uint))
                return self._video.set_rotation(rotation_ptr.contents)

            case EnvironmentCall.GET_OVERSCAN:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_OVERSCAN doesn't accept NULL")

                overscan_ptr = cast(data, POINTER(c_bool))
                overscan_ptr.contents = self._overscan
                return True

            case EnvironmentCall.GET_CAN_DUPE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CAN_DUPE doesn't accept NULL")

                dupe_ptr = cast(data, POINTER(c_bool))
                dupe_ptr.contents = self._video.can_dupe()
                return True

            case EnvironmentCall.SET_MESSAGE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_MESSAGE doesn't accept NULL")

                message_ptr = cast(data, POINTER(retro_message))
                return self._message.set_message(message_ptr.contents)

            case EnvironmentCall.SHUTDOWN:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_PERFORMANCE_LEVEL:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL doesn't accept NULL")

                perflevel_ptr = cast(data, POINTER(c_uint))
                self._performance_level = perflevel_ptr.contents.value
                return True

            case EnvironmentCall.GET_SYSTEM_DIRECTORY:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY doesn't accept NULL")

                sysdir_ptr = cast(data, POINTER(c_char_p))
                sysdir_ptr.contents.value = self._system_dir
                return True

            case EnvironmentCall.SET_PIXEL_FORMAT:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_PIXEL_FORMAT doesn't accept NULL")

                pixfmt_ptr = cast(data, POINTER(retro_pixel_format))
                return self._video.set_pixel_format(PixelFormat(pixfmt_ptr.contents.value))

            case EnvironmentCall.SET_INPUT_DESCRIPTORS:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_KEYBOARD_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_DISK_CONTROL_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_VARIABLE:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_VARIABLES:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_VARIABLE_UPDATE:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_SUPPORT_NO_GAME:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME doesn't accept NULL")

                support_no_game_ptr = cast(data, POINTER(c_bool))
                self._support_no_game = support_no_game_ptr.contents.value
                return True

            case EnvironmentCall.GET_LIBRETRO_PATH:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LIBRETRO_PATH doesn't accept NULL")

                libretro_path_ptr = cast(data, POINTER(c_char_p))
                libretro_path_ptr.contents.value = self._libretro_path
                return True

            case EnvironmentCall.SET_FRAME_TIME_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_AUDIO_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_RUMBLE_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_INPUT_DEVICE_CAPABILITIES:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES doesn't accept NULL")

                inputcaps_ptr = cast(data, POINTER(c_uint64))
                inputcaps_ptr.contents = self._input.device_capabilities
                return True

            case EnvironmentCall.GET_SENSOR_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_CAMERA_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_LOG_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LOG_INTERFACE doesn't accept NULL")

                log_ptr = cast(data, POINTER(retro_log_callback))
                log_ptr.contents = self._log_callback._as_parameter_
                # TODO: Is there a cleaner way to do this than using _as_parameter_?
                return True

            case EnvironmentCall.GET_PERF_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_LOCATION_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_CORE_ASSETS_DIRECTORY:
                if self._core_assets_dir is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY doesn't accept NULL")

                core_assets_dir_ptr = cast(data, POINTER(c_char_p))
                core_assets_dir_ptr.contents.value = self._core_assets_dir
                return True

            case EnvironmentCall.GET_SAVE_DIRECTORY:
                if self._save_dir is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY doesn't accept NULL")

                save_dir_ptr = cast(data, POINTER(c_char_p))
                save_dir_ptr.contents.value = self._save_dir
                return True

            case EnvironmentCall.SET_SYSTEM_AV_INFO:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_PROC_ADDRESS_CALLBACK:
                if not data:
                    self._proc_address_callback = None
                else:
                    procaddress_ptr = cast(data, POINTER(retro_get_proc_address_interface))
                    interface: retro_get_proc_address_interface = procaddress_ptr.contents
                    self._proc_address_callback = retro_get_proc_address_interface(interface.get_proc_address)

                return True

            case EnvironmentCall.SET_SUBSYSTEM_INFO:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO doesn't accept NULL")

                subsystem_info_ptr = cast(data, POINTER(retro_subsystem_info))
                self._subsystem_info = from_zero_terminated(subsystem_info_ptr)
                return True

            case EnvironmentCall.SET_CONTROLLER_INFO:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_MEMORY_MAPS:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_GEOMETRY:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_USERNAME:
                if self._username is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_USERNAME doesn't accept NULL")

                username_ptr = cast(data, POINTER(c_char_p))
                username_ptr.contents.value = self._username
                return True

            case EnvironmentCall.GET_LANGUAGE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LANGUAGE doesn't accept NULL")

                language_ptr = cast(data, POINTER(retro_language))
                language_ptr.contents = self._language
                return True

            case EnvironmentCall.GET_CURRENT_SOFTWARE_FRAMEBUFFER:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_HW_RENDER_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_SUPPORT_ACHIEVEMENTS:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS doesn't accept NULL")

                supports_achievements_ptr = cast(data, POINTER(c_bool))
                self._supports_achievements = supports_achievements_ptr.contents.value
                return True

            case EnvironmentCall.SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_SERIALIZATION_QUIRKS:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_HW_SHARED_CONTEXT:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_VFS_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_LED_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_AUDIO_VIDEO_ENABLE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_MIDI_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_FASTFORWARDING:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_TARGET_REFRESH_RATE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE doesn't accept NULL")

                refresh_rate_ptr = cast(data, POINTER(c_float))
                refresh_rate_ptr.contents = self._target_refresh_rate
                return True

            case EnvironmentCall.GET_CORE_OPTIONS_VERSION:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_CORE_OPTIONS:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_CORE_OPTIONS_INTL:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_CORE_OPTIONS_DISPLAY:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_PREFERRED_HW_RENDER:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_DISK_CONTROL_INTERFACE_VERSION:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_DISK_CONTROL_EXT_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_MESSAGE_INTERFACE_VERSION:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_MESSAGE_EXT:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_AUDIO_BUFFER_STATUS_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_MINIMUM_AUDIO_LATENCY:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_FASTFORWARDING_OVERRIDE:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_CONTENT_INFO_OVERRIDE:
                if not data:
                    return True
                # The docs say that passing NULL here serves to query for support

                override_ptr = cast(data, POINTER(retro_system_content_info_override))
                self._content_info_override = from_zero_terminated(override_ptr)
                return True

            case EnvironmentCall.GET_GAME_INFO_EXT:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_CORE_OPTIONS_V2:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_CORE_OPTIONS_V2_INTL:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_VARIABLE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_THROTTLE_STATE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_SAVE_STATE_CONTEXT:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_JIT_CAPABLE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_JIT_CAPABLE doesn't accept NULL")

                jit_capable_ptr = cast(data, POINTER(c_bool))
                jit_capable_ptr.contents = self._jit_capable
                return True

            case EnvironmentCall.GET_MICROPHONE_INTERFACE:
                # TODO: Implement
                pass
            case EnvironmentCall.GET_DEVICE_POWER:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_NETPACKET_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_PLAYLIST_DIRECTORY:
                if self._playlist_dir is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY doesn't accept NULL")

                playlist_dir_ptr = cast(data, POINTER(c_char_p))
                playlist_dir_ptr.contents.value = self._playlist_dir
                return True

        # TODO: Define a way to override certain calls
        return False


def default_session(
        core: str,
        content: str | SpecialContent | _DoNotLoad | None = None,
        audio: AudioCallbacks | None = None,
        input_state: InputCallbacks | InputStateIterator | InputStateGenerator | None = None,
        video: VideoCallbacks | None = None,
        overscan: bool = False,
        message: MessageInterface | None = None,
        system_dir: Directory | None = None,
        log_callback: LogCallback | None = None,
        save_dir: Directory | None = None,
        ) -> Session:
    """
    Returns a Session with default state objects.
    """

    input_impl: InputState | None = None
    if isinstance(input_state, InputState):
        input_impl = input_state
    elif isinstance(input_state, Iterable):
        input_impl = GeneratorInputState(input_state)
    elif isinstance(input_state, Callable):
        input_impl = GeneratorInputState(input_state)

    logger = logging.getLogger('libretro')
    return Session(
        core=core,
        audio=audio or ArrayAudioState(),
        input_state=input_impl or GeneratorInputState(),
        video=video or SoftwareVideoState(),
        content=content,
        overscan=overscan,
        message=message or LoggerMessageInterface(1, logger),
        system_dir=system_dir,
        log_callback=log_callback or StandardLogger(logger),
        save_dir=save_dir
    )
