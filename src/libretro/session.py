import logging

from collections.abc import Iterable
from logging import Logger
from types import TracebackType
from typing import Type

from .api.av import *
from .api.content import *
from .api.environment import EnvironmentCall
from .api.led import retro_led_interface, LedInterface, DictLedInterface
from .api.location import *
from .api.memory import retro_memory_map
from .api.microphone.default import MicrophoneInputIterator, MicrophoneInputGenerator, GeneratorMicrophoneInterface
from .api.microphone.defs import retro_microphone_interface
from .api.microphone.interface import MicrophoneInterface
from .api.midi import *
from .api.options import *
from .api.perf import *
from .api.power import retro_device_power, PowerState, DevicePower
from .api.rumble import *
from .api.savestate import *
from .api.sensor import *
from .api.system import *
from .api.throttle import *
from .api.log import retro_log_callback, LogCallback, UnformattedLogger
from .api.message import retro_message, MessageInterface, LoggerMessageInterface, retro_message_ext
from .api.proc import retro_get_proc_address_interface, retro_proc_address_t
from .api.vfs import retro_vfs_interface_info, FileSystemInterface, StandardFileSystemInterface, retro_vfs_interface
from .core import Core, CoreInterface
from .api.audio import AudioCallbacks, AudioState, ArrayAudioState
from .api.environment import EnvironmentCallback
from .api.input import *
from .api.input.info import retro_controller_info, retro_input_descriptor
from .api.input.keyboard import *
from .api.video import *

from ._utils import *

Directory = str | bytes

class _DoNotLoad: pass


DoNotLoad = _DoNotLoad()


class CoreShutDownException(Exception):
    def __init__(self, *args):
        super().__init__("Core has been shut down", *args)


def full_power() -> retro_device_power:
    return retro_device_power(PowerState.PLUGGED_IN, RETRO_POWERSTATE_NO_ESTIMATE, 100)


class Session(EnvironmentCallback):
    def __init__(
            self,
            core: Core | str,
            audio: AudioState,
            input_state: InputState,
            video: VideoDriver,
            # TODO: Support for an env override function

            content: Content | SubsystemContent | _DoNotLoad | None,
            overscan: bool,
            message: MessageInterface,
            options: OptionState,
            system_dir: Directory | None,
            rumble: RumbleInterface | None,
            sensor: SensorInterface | None,
            log_callback: LogCallback,
            perf: PerfInterface,
            location: LocationInterface,
            core_assets_dir: Directory | None,
            save_dir: Directory | None,
            username: str | bytes | None,
            language: Language,
            vfs: FileSystemInterface,
            led: LedInterface,
            av_enable: AvEnableFlags,
            midi: MidiInterface,
            target_refresh_rate: float,
            preferred_hw: HardwareContext | None,
            driver_switch_enable: bool,
            max_users: int,
            throttle_state: retro_throttle_state,
            savestate_context: SavestateContext,
            jit_capable: bool,
            mic_interface: MicrophoneInterface,
            device_power: DevicePower,
            playlist_dir: Directory | None
    ):
        if core is None:
            raise ValueError("Core cannot be None")

        if not isinstance(audio, AudioCallbacks):
            raise TypeError(f"Expected audio to match AudioCallbacks, not {type(audio).__name__}")

        if not isinstance(input_state, InputState):
            raise TypeError(f"Expected input_state to match InputState, not {type(input_state).__name__}")

        if not isinstance(video, VideoDriver):
            raise TypeError(f"Expected video to be a VideoDriver, got {type(video).__name__}")

        if not isinstance(message, MessageInterface):
            raise TypeError(f"Expected message to match MessageInterface, not {type(message).__name__}")

        if not isinstance(options, OptionState):
            raise TypeError(f"Expected options to match OptionState, not {type(options).__name__}")

        if not isinstance(system_dir, (str, bytes, type(None))):
            raise TypeError(f"Expected system_dir to be str, bytes, or None; got {type(system_dir).__name__}")

        if not isinstance(log_callback, LogCallback):
            raise TypeError(f"Expected log_callback to match LogCallback, not {type(log_callback).__name__}")

        if not isinstance(core_assets_dir, (str, bytes, type(None))):
            raise TypeError(f"Expected core_assets_dir to be str, bytes, or None; got {type(core_assets_dir).__name__}")

        if not isinstance(save_dir, (str, bytes, type(None))):
            raise TypeError(f"Expected save_dir to be str, bytes, or None; got {type(save_dir).__name__}")

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

        self._overscan = bool(overscan)
        self._message = message
        self._is_shutdown: bool = False
        self._keyboard_callback: retro_keyboard_callback | None = None
        self._performance_level: int | None = None
        self._system_dir = as_bytes(system_dir)
        self._input_descriptors: Sequence[retro_input_descriptor] | None = None
        self._options: OptionState = options
        self._hw_render: retro_hw_render_callback | None = None
        self._support_no_game: bool | None = None
        self._libretro_path: bytes = as_bytes(self._core.path)
        self._frame_time_callback: retro_frame_time_callback | None = None
        self._rumble = rumble
        self._sensor = sensor
        self._log_callback: LogCallback = log_callback
        self._perf = perf
        self._location = location
        self._core_assets_dir = as_bytes(core_assets_dir)
        self._save_dir = as_bytes(save_dir)
        self._proc_address_callback: retro_get_proc_address_interface | None = None
        self._subsystem_info: Sequence[retro_subsystem_info] | None = None
        self._controller_infos: Sequence[retro_controller_info] | None = None
        self._memory_maps: retro_memory_map | None = None
        self._username = as_bytes(username)
        self._language = language
        self._supports_achievements: bool | None = None
        self._vfs: FileSystemInterface = vfs
        self._led = led
        self._av_enable = av_enable
        self._midi = midi
        self._serialization_quirks: SerializationQuirks | None = None
        self._target_refresh_rate = target_refresh_rate
        self._preferred_hw = preferred_hw
        self._driver_switch_enable = bool(driver_switch_enable)
        self._max_users = max_users
        self._fastforwarding_override: retro_fastforwarding_override | None = None
        self._content_info_override: Sequence[retro_system_content_info_override] | None = None
        self._throttle_state: retro_throttle_state = throttle_state
        self._savestate_context: SavestateContext = savestate_context
        self._jit_capable = jit_capable
        self._mic_interface = mic_interface
        self._device_power = device_power
        self._playlist_dir = as_bytes(playlist_dir)
        self._pending_callback_exceptions: list[BaseException] = []
        self._is_exited = False

    def __enter__(self):
        api_version = self._core.api_version()
        if api_version != RETRO_API_VERSION:
            raise RuntimeError(f"libretro.py is only compatible with API version {RETRO_API_VERSION}, but the core uses {api_version}")

        self._core.set_video_refresh(self._video.refresh)
        self._core.set_audio_sample(self._audio.audio_sample)
        self._core.set_audio_sample_batch(self._audio.audio_sample_batch)
        self._core.set_input_poll(self._input.poll)
        self._core.set_input_state(self.__input_state)
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

            # TODO: case bytes(path) if path is a valid path
            case bytes(rom) | bytearray(rom) | memoryview(rom):
                # For test cases that provide ROM data directly
                if need_fullpath:
                    raise ValueError("Core requires a full path, but none was provided")

                loaded = self._core.load_game(retro_game_info(None, rom, len(rom), None))
            case SubsystemContent(game_type=game_type, info=infos):
                if not self._subsystem_info:
                    raise RuntimeError("Subsystem content was provided, but core did not register subsystems")

                # TODO: Verify conditions
                loaded = self._core.load_game_special(game_type, infos)
            case None:
                if not self._support_no_game:
                    raise RuntimeError("No content provided and core did not indicate support for no game.")

                loaded = self._core.load_game(None)

        if not loaded:
            raise RuntimeError("Failed to load game")

        self._system_av_info = self._core.get_system_av_info()
        self._video.set_system_av_info(self._system_av_info)

        return self

    def __exit__(self, exc_type: type[Exception], exc_val: Exception, exc_tb: TracebackType):
        if self._content is not DoNotLoad:
            self._core.unload_game()

        self._core.deinit()
        del self._core
        self._is_exited = True
        return isinstance(exc_val, CoreShutDownException)
        # Returning True from a context manage suppresses the exception;
        # if the core shut down then core methods should raise a CoreShutDownException,
        # which is not an error.
        # If exc_val is None, then there never was an exception.
        # If exc_val is any other error, then it should be propagated after cleaning up the core.

    @property
    def core(self) -> CoreInterface:
        if self._is_exited or self._is_shutdown:
            raise CoreShutDownException()

        return self._core

    @property
    def audio(self) -> AudioCallbacks:
        return self._audio

    @property
    def input(self) -> InputCallbacks:
        return self._input

    @property
    def video(self) -> VideoDriver:
        return self._video

    @property
    def message(self) -> MessageInterface | None:
        return self._message

    @property
    def is_shutdown(self) -> bool:
        return self._is_shutdown

    @property
    def is_exited(self) -> bool:
        return self._is_exited

    @property
    def system_directory(self) -> bytes | None:
        return self._system_dir

    @property
    def system_dir(self) -> bytes | None:
        return self._system_dir

    @property
    def input_descriptors(self) -> Sequence[retro_input_descriptor] | None:
        return self._input_descriptors

    @property
    def options(self) -> OptionState:
        return self._options

    @property
    def support_no_game(self) -> bool | None:
        return self._support_no_game

    @property
    def rumble(self) -> RumbleInterface | None:
        return self._rumble

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

    def get_proc_address(self, sym: AnyStr, funtype: Type[ctypes._CFuncPtr] | None) -> retro_proc_address_t | Callable | None:
        if not self._proc_address_callback or not sym:
            return None

        name = as_bytes(sym)

        proc = self._proc_address_callback.get_proc_address(name)

        if not proc:
            return None

        if funtype:
            return funtype(proc)

        return proc

    @property
    def subsystems(self) -> Sequence[retro_subsystem_info] | None:
        return self._subsystem_info

    @property
    def controller_info(self) -> Sequence[retro_controller_info] | None:
        return self._controller_infos

    @property
    def memory_maps(self) -> retro_memory_map | None:
        return self._memory_maps

    @property
    def support_achievements(self) -> bool | None:
        return self._supports_achievements

    @property
    def av_enable(self) -> AvEnableFlags:
        return self._av_enable

    @av_enable.setter
    def av_enable(self, value: AvEnableFlags):
        self._av_enable = value

    @property
    def midi(self) -> MidiInterface:
        return self._midi

    @property
    def serialization_quirks(self) -> SerializationQuirks | None:
        return self._serialization_quirks

    @property
    def vfs(self) -> FileSystemInterface:
        return self._vfs

    @property
    def led(self) -> LedInterface:
        return self._led

    @property
    def max_users(self) -> int:
        return self._max_users

    @max_users.setter
    def max_users(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Expected an integer number of users, got {type(value).__name__}")

        if value < 0:
            raise ValueError(f"Expected a non-negative number of users, got {value}")

        self._max_users = int(value)

    @property
    def fastforwarding_override(self) -> retro_fastforwarding_override | None:
        return self._fastforwarding_override

    @property
    def content_info_overrides(self) -> Sequence[retro_system_content_info_override] | None:
        return self._content_info_override

    @property
    def throttle_state(self) -> retro_throttle_state:
        return self._throttle_state

    def environment(self, cmd: int, data: c_void_p) -> bool:
        # TODO: Allow overriding certain calls by passing a function to the constructor
        # TODO: Match envcalls even if the experimental flag is unset (but still consider it for ABI differences)
        match EnvironmentCall(cmd):
            case EnvironmentCall.SET_ROTATION:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_ROTATION doesn't accept NULL")

                rotation = cast(data, POINTER(c_uint))[0]
                return self._video.set_rotation(Rotation(rotation))

            case EnvironmentCall.GET_OVERSCAN:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_OVERSCAN doesn't accept NULL")

                overscan_ptr = cast(data, POINTER(c_bool))
                overscan_ptr.contents.value = self._overscan
                return True

            case EnvironmentCall.GET_CAN_DUPE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CAN_DUPE doesn't accept NULL")

                dupe_ptr = cast(data, POINTER(c_bool))
                dupe_ptr.contents.value = self._video.can_dupe
                return True

            case EnvironmentCall.SET_MESSAGE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_MESSAGE doesn't accept NULL")

                message_ptr = cast(data, POINTER(retro_message))
                message: retro_message = message_ptr[0]
                return self._message.set_message(message)

            case EnvironmentCall.SHUTDOWN:
                self._is_shutdown = True
                return True

            case EnvironmentCall.SET_PERFORMANCE_LEVEL:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL doesn't accept NULL")

                self._performance_level = cast(data, POINTER(c_uint))[0]
                return True

            case EnvironmentCall.GET_SYSTEM_DIRECTORY:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY doesn't accept NULL")

                sysdir_ptr = cast(data, POINTER(c_char_p))
                sysdir_ptr[0] = self._system_dir
                return True

            case EnvironmentCall.SET_PIXEL_FORMAT:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_PIXEL_FORMAT doesn't accept NULL")

                pixfmt_ptr = cast(data, POINTER(retro_pixel_format))
                return self._video.set_pixel_format(PixelFormat(pixfmt_ptr[0]))

            case EnvironmentCall.SET_INPUT_DESCRIPTORS:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS doesn't accept NULL")

                inputdesc_ptr = cast(data, POINTER(retro_input_descriptor))
                self._input_descriptors = tuple(deepcopy(s) for s in from_zero_terminated(inputdesc_ptr))
                return True

            case EnvironmentCall.SET_KEYBOARD_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_DISK_CONTROL_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_HW_RENDER | EnvironmentCall.SET_HW_RENDER_EXPERIMENTAL:
                if not data:
                    return False  # Callback doesn't support NULL

                hwrender_ptr = cast(data, POINTER(retro_hw_render_callback))
                hwrender: retro_hw_render_callback = hwrender_ptr[0]

                ok = self._video.init_callback(hwrender_ptr[0])

                # TODO: Initialize a context based on the interface type
                # TODO: Account for the old ABI (see RETRO_ENVIRONMENT_EXPERIMENTAL)

                self._hw_render = retro_hw_render_callback()
                # TODO: Initialize the video driver
                pass  # TODO: Implement
                # Where should the video driver be initialized?

            case EnvironmentCall.GET_VARIABLE:
                if data:
                    var_ptr = cast(data, POINTER(retro_variable))
                    var: retro_variable = var_ptr.contents

                    result = self._options.get_variable(string_at(var.key) if var.key else None)
                    var.value = result
                    # Either a bytes for an option or None

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.SET_VARIABLES:
                if data:
                    variables_ptr = cast(data, POINTER(retro_variable))
                    self._options.set_variables(tuple(deepcopy(s) for s in from_zero_terminated(variables_ptr)))
                else:
                    self._options.set_variables(None)

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.GET_VARIABLE_UPDATE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE doesn't accept NULL")

                update_ptr = cast(data, POINTER(c_bool))
                update_ptr[0] = self._options.variable_updated
                return True

            case EnvironmentCall.SET_SUPPORT_NO_GAME:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME doesn't accept NULL")

                self._support_no_game = cast(data, POINTER(c_bool))[0]
                return True

            case EnvironmentCall.GET_LIBRETRO_PATH:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LIBRETRO_PATH doesn't accept NULL")

                libretro_path_ptr = cast(data, POINTER(c_char_p))
                libretro_path_ptr[0] = self._libretro_path
                return True

            case EnvironmentCall.SET_FRAME_TIME_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_AUDIO_CALLBACK:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_RUMBLE_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE doesn't accept NULL")

                rumble_ptr = cast(data, POINTER(retro_rumble_interface))
                rumble: retro_rumble_interface = rumble_ptr[0]
                rumble.set_rumble_state = retro_set_rumble_state_t(self.__set_rumble_state)
                return True

            case EnvironmentCall.GET_INPUT_DEVICE_CAPABILITIES:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES doesn't accept NULL")

                inputcaps_ptr = cast(data, POINTER(c_uint64))
                inputcaps_ptr[0] = self._input.device_capabilities
                return True

            case EnvironmentCall.GET_SENSOR_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE doesn't accept NULL")

                sensor_ptr = cast(data, POINTER(retro_sensor_interface))
                sensor: retro_sensor_interface = sensor_ptr[0]
                sensor.get_sensor_input = retro_sensor_get_input_t(self.__get_sensor_input)
                sensor.set_sensor_state = retro_set_sensor_state_t(self.__set_sensor_state)
                return True

            case EnvironmentCall.GET_CAMERA_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_LOG_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LOG_INTERFACE doesn't accept NULL")

                log_ptr = cast(data, POINTER(retro_log_callback))
                log_ptr[0] = retro_log_callback.from_param(self._log_callback)
                return True

            case EnvironmentCall.GET_PERF_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_PERF_INTERFACE doesn't accept NULL")

                perf_ptr = cast(data, POINTER(retro_perf_callback))
                perf_ptr[0] = retro_perf_callback.from_param(self._perf)
                return True

            case EnvironmentCall.GET_LOCATION_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE doesn't accept NULL")

                location_ptr = cast(data, POINTER(retro_location_callback))
                location: retro_location_callback = location_ptr[0]

                self._location.initialized = location.initialized
                self._location.deinitialized = location.deinitialized

                memmove(location_ptr, byref(retro_location_callback.from_param(self._location)), sizeof(retro_location_callback))
                return True

            case EnvironmentCall.GET_CORE_ASSETS_DIRECTORY:
                if self._core_assets_dir is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY doesn't accept NULL")

                core_assets_dir_ptr = cast(data, POINTER(c_char_p))
                core_assets_dir_ptr[0] = self._core_assets_dir
                return True

            case EnvironmentCall.GET_SAVE_DIRECTORY:
                if self._save_dir is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY doesn't accept NULL")

                save_dir_ptr = cast(data, POINTER(c_char_p))
                save_dir_ptr[0] = self._save_dir
                return True

            case EnvironmentCall.SET_SYSTEM_AV_INFO:
                if not data:
                    return False

                av_info_ptr = cast(data, POINTER(retro_system_av_info))
                av_info: retro_system_av_info = av_info_ptr[0]
                self._video.set_system_av_info(av_info)
                self._system_av_info = deepcopy(av_info)
                # TODO: Implement for audio drivers
                return True

            case EnvironmentCall.SET_PROC_ADDRESS_CALLBACK:
                if not data:
                    self._proc_address_callback = None
                else:
                    procaddress_ptr = cast(data, POINTER(retro_get_proc_address_interface))
                    self._proc_address_callback = deepcopy(procaddress_ptr[0])

                return True

            case EnvironmentCall.SET_SUBSYSTEM_INFO:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO doesn't accept NULL")

                subsystem_info_ptr = cast(data, POINTER(retro_subsystem_info))
                self._subsystem_info = tuple(deepcopy(s) for s in from_zero_terminated(subsystem_info_ptr))
                return True

            case EnvironmentCall.SET_CONTROLLER_INFO:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_CONTROLLER_INFO doesn't accept NULL")

                controller_info_ptr = cast(data, POINTER(retro_controller_info))
                controller_infos = tuple(deepcopy(s) for s in from_zero_terminated(controller_info_ptr))
                self._controller_infos = controller_infos

                return True

            case EnvironmentCall.SET_MEMORY_MAPS:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_MEMORY_MAPS doesn't accept NULL")

                memorymaps_ptr = cast(data, POINTER(retro_memory_map))
                memorymaps: retro_memory_map = memorymaps_ptr[0]

                self._memory_maps = deepcopy(memorymaps)
                return True

            case EnvironmentCall.SET_GEOMETRY:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_GEOMETRY doesn't accept NULL")

                geom: retro_game_geometry = cast(data, POINTER(retro_game_geometry))[0]
                self._video.set_geometry(geom)
                return True

            case EnvironmentCall.GET_USERNAME:
                if self._username is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_USERNAME doesn't accept NULL")

                username_ptr = cast(data, POINTER(c_char_p))
                username_ptr[0] = self._username
                return True

            case EnvironmentCall.GET_LANGUAGE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LANGUAGE doesn't accept NULL")

                language_ptr = cast(data, POINTER(retro_language))
                language_ptr[0] = self._language
                return True

            case EnvironmentCall.GET_CURRENT_SOFTWARE_FRAMEBUFFER:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER doesn't accept NULL")

                core_fb_ptr = cast(data, POINTER(retro_framebuffer))
                core_fb: retro_framebuffer = core_fb_ptr[0]

                width = core_fb.width
                height = core_fb.height
                access = core_fb.access_flags
                fb = self._video.get_software_framebuffer(int(width), int(height), MemoryAccess(access))
                if not fb:
                    return False

                core_fb.data = fb.data
                core_fb.pitch = fb.pitch
                core_fb.format = fb.format
                core_fb.memory_flags = fb.memory_flags
                return True

            case EnvironmentCall.GET_HW_RENDER_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE doesn't accept NULL")

                hwrender_interface = self._video.hw_render_interface
                if not hwrender_interface:
                    # This video driver doesn't provide (or need) a hardware render interface
                    return False

                hwrenderptr_ptr = cast(data, POINTER(POINTER(retro_hw_render_interface)))
                hwrenderptr_ptr[0] = pointer(hwrender_interface)
                return True

            case EnvironmentCall.SET_SUPPORT_ACHIEVEMENTS:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS doesn't accept NULL")

                self._supports_achievements = cast(data, POINTER(c_bool))[0]
                return True

            case EnvironmentCall.SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_SERIALIZATION_QUIRKS:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS doesn't accept NULL")

                quirks_ptr = cast(data, POINTER(c_uint64))
                self._serialization_quirks = SerializationQuirks(quirks_ptr[0])
                return True

            case EnvironmentCall.SET_HW_SHARED_CONTEXT:
                self._video.set_shared_context()
                return True

            case EnvironmentCall.GET_VFS_INTERFACE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_VFS_INTERFACE doesn't accept NULL")

                vfs_ptr = cast(data, POINTER(retro_vfs_interface_info))
                vfs_info: retro_vfs_interface_info = vfs_ptr[0]

                if vfs_info.required_interface_version > self._vfs.version:
                    # If the core wants a higher version than what we offer...
                    return False

                vfs_info.required_interface_version = self._vfs.version
                vfs_info.iface = pointer(retro_vfs_interface.from_param(self._vfs))
                return True

            case EnvironmentCall.GET_LED_INTERFACE:
                if data:
                    led_ptr = cast(data, POINTER(retro_led_interface))
                    memmove(led_ptr, byref(retro_led_interface.from_param(self._led)), sizeof(retro_led_interface))

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.GET_AUDIO_VIDEO_ENABLE:
                if data:
                    av_enable_ptr = cast(data, POINTER(c_uint))
                    av_enable_ptr[0] = self._av_enable

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.GET_MIDI_INTERFACE:
                if data:
                    midi_ptr = cast(data, POINTER(retro_midi_interface))
                    memmove(midi_ptr, byref(retro_midi_interface.from_param(self._midi)), sizeof(retro_midi_interface))

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.GET_FASTFORWARDING:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_FASTFORWARDING doesn't accept NULL")

                fastforwarding_ptr = cast(data, POINTER(c_bool))
                fastforwarding_ptr[0] = self._throttle_state.mode.value == ThrottleMode.FAST_FORWARD
                return True

            case EnvironmentCall.GET_TARGET_REFRESH_RATE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE doesn't accept NULL")

                refresh_rate_ptr = cast(data, POINTER(c_float))
                refresh_rate_ptr[0] = self._target_refresh_rate
                return True

            case EnvironmentCall.GET_INPUT_BITMASKS:
                return self._input.bitmasks_supported

            case EnvironmentCall.GET_CORE_OPTIONS_VERSION:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION doesn't accept NULL")

                optversion_ptr = cast(data, POINTER(c_uint))
                optversion_ptr[0] = self._options.version
                return True

            case EnvironmentCall.SET_CORE_OPTIONS:
                if data:
                    if self._options.get_version() < 1:
                        return False

                    options_ptr = cast(data, POINTER(retro_core_option_definition))
                    self._options.set_options(tuple(from_zero_terminated(options_ptr)))
                else:
                    self._options.set_options(None)

                # This envcall supports passing NULL to reset the options
                return True

            case EnvironmentCall.SET_CORE_OPTIONS_INTL:
                if data:
                    if self._options.get_version() < 1:
                        return False

                    options_intl_ptr = cast(data, POINTER(retro_core_options_intl))
                    self._options.set_options_intl(options_intl_ptr.contents)
                else:
                    self._options.set_options_intl(None)

                # This envcall supports passing NULL to reset the options
                return True

            case EnvironmentCall.SET_CORE_OPTIONS_DISPLAY:
                if data:
                    opt_display_ptr = cast(data, POINTER(retro_core_option_display))
                    opt_display: retro_core_option_display = opt_display_ptr.contents

                    if opt_display.key:
                        self._options.set_display(opt_display.key, opt_display.visible)

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.GET_PREFERRED_HW_RENDER:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER doesn't accept NULL")

                preferred_hw_ptr = cast(data, POINTER(retro_hw_context_type))
                preferred_hw_ptr[0] = self._preferred_hw

                # This envcall returns True if the core supports the call
                # *and* the frontend can switch video drivers
                return self._driver_switch_enable

            case EnvironmentCall.GET_DISK_CONTROL_INTERFACE_VERSION:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_DISK_CONTROL_EXT_INTERFACE:
                # TODO: Implement
                pass

            case EnvironmentCall.GET_MESSAGE_INTERFACE_VERSION:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_MESSAGE_INTERFACE_VERSION doesn't accept NULL")

                msgversion_ptr = cast(data, POINTER(c_uint))
                msgversion_ptr.contents.value = self._message.version
                return True

            case EnvironmentCall.SET_MESSAGE_EXT:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_MESSAGE_EXT doesn't accept NULL")

                message_ext_ptr = cast(data, POINTER(retro_message_ext))
                return self._message.set_message(message_ext_ptr.contents)

            case EnvironmentCall.GET_INPUT_MAX_USERS:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS doesn't accept NULL")

                max_users_ptr = cast(data, POINTER(c_uint))
                max_users_ptr[0] = self._max_users
                return True

            case EnvironmentCall.SET_AUDIO_BUFFER_STATUS_CALLBACK:
                # TODO: Implement
                pass
            case EnvironmentCall.SET_MINIMUM_AUDIO_LATENCY:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_FASTFORWARDING_OVERRIDE:
                if data:
                    fastforwarding_override_ptr = cast(data, POINTER(retro_fastforwarding_override))
                    fastforwarding: retro_fastforwarding_override = fastforwarding_override_ptr[0]
                    self._fastforwarding_override = retro_fastforwarding_override(
                        fastforwarding.ratio,
                        fastforwarding.fastforward,
                        fastforwarding.notification,
                        fastforwarding.inhibit_toggle
                    )

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.SET_CONTENT_INFO_OVERRIDE:
                if not data:
                    return True
                # The docs say that passing NULL here serves to query for support

                override_ptr = cast(data, POINTER(retro_system_content_info_override))
                self._content_info_override = tuple(from_zero_terminated(override_ptr))
                return True

            case EnvironmentCall.GET_GAME_INFO_EXT:
                # TODO: Implement
                pass

            case EnvironmentCall.SET_CORE_OPTIONS_V2:
                if self._options.get_version() < 2:
                    return False

                if data:
                    options_v2_ptr = cast(data, POINTER(retro_core_options_v2))
                    self._options.set_options_v2(options_v2_ptr.contents)
                else:
                    self._options.set_options_v2(None)

                return self._options.supports_categories

            case EnvironmentCall.SET_CORE_OPTIONS_V2_INTL:
                if self._options.get_version() < 2:
                    return False

                if data:
                    options_v2_intl_ptr = cast(data, POINTER(retro_core_options_v2_intl))
                    self._options.set_options_v2_intl(options_v2_intl_ptr.contents)
                else:
                    self._options.set_options_v2_intl(None)

                return self._options.supports_categories

            case EnvironmentCall.SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK:
                if data:
                    option_display_callback_ptr = cast(data, POINTER(retro_core_options_update_display_callback))
                    self._options.set_update_display_callback(option_display_callback_ptr.contents)

                return True

            case EnvironmentCall.SET_VARIABLE:
                if data:
                    var_ptr = cast(data, POINTER(retro_variable))
                    var: retro_variable = var_ptr.contents
                    return self._options.set_variable(var.key, var.value)

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.GET_THROTTLE_STATE:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_THROTTLE_STATE doesn't accept NULL")

                throttle_state_ptr = cast(data, POINTER(retro_throttle_state))
                throttle_state: retro_throttle_state = throttle_state_ptr[0]

                throttle_state.mode = self._throttle_state.mode
                throttle_state.rate = self._throttle_state.rate

                return True

            case EnvironmentCall.GET_SAVESTATE_CONTEXT:
                if data:
                    savestate_context_ptr = cast(data, POINTER(retro_savestate_context))
                    savestate_context_ptr[0] = self._savestate_context

                # This envcall supports passing NULL to query for support
                return True
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
                if data:
                    mic_interface_ptr = cast(data, POINTER(retro_microphone_interface))
                    mic_interface: retro_microphone_interface = mic_interface_ptr[0]

                    if mic_interface.interface_version != self._mic_interface.version:
                        return False

                    mic_interface_ptr[0] = retro_microphone_interface.from_param(self._mic_interface)

                # This envcall supports passing NULL to query for support
                return True

            case EnvironmentCall.GET_DEVICE_POWER:
                if data:
                    device_power_ptr = cast(data, POINTER(retro_device_power))
                    power = self._device_power()
                    memmove(device_power_ptr, byref(power), sizeof(retro_device_power))

                # This envcall supports passing NULL to query for support
                return True

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
            case _:
                print(f"Unhandled env call: {hex(cmd)}")

        # TODO: Define a way to override certain calls
        return False

    def __input_poll(self) -> None:
        self._input.poll()

        if isinstance(self._sensor, Pollable):
            self._sensor.poll()

        if isinstance(self._mic_interface, Pollable):
            self._mic_interface.poll()

    # Need a wrapper method in Session so that we can filter out unacceptable ports
    def __input_state(self, port: int, device: int, index: int, id: int) -> int:
        if not (0 <= port < self._max_users):
            # If querying the input state of a nonexistent player...
            return 0

        return self._input.state(port, device, index, id)

    # Need a wrapper method in Session so that we can filter out unacceptable ports
    def __set_rumble_state(self, port: int, effect: int, strength: int) -> bool:
        if effect not in RumbleEffect or not (0 <= port < self._max_users):
            # If setting the rumble state of a nonexistent player...
            return False

        return self._rumble.set_rumble_state(port, RumbleEffect(effect), strength)

    def __set_sensor_state(self, port: int, action: int, rate: int) -> bool:
        if action not in SensorAction or not (0 <= port < self._max_users):
            # If setting the sensor state of a nonexistent player or sensor...
            return False

        return self._sensor.set_sensor_state(port, SensorAction(action), rate)

    def __get_sensor_input(self, port: int, sensor: int) -> float:
        if sensor not in Sensor or not (0 <= port < self._max_users):
            # If querying the input of a nonexistent player or sensor...
            return 0.0

        return self._sensor.get_sensor_input(port, Sensor(sensor))


def default_session(
        core: str | Core | CDLL | PathLike,
        content: str | SubsystemContent | _DoNotLoad | None = None,
        audio: AudioCallbacks | None = None,
        input_state: InputCallbacks | InputStateIterator | InputStateGenerator | None = None,
        video: VideoDriver | None = None,
        options: OptionState | Mapping[AnyStr, AnyStr] | None = None,
        overscan: bool = False,
        message: MessageInterface | None = None,
        system_dir: Directory | None = None,
        rumble: RumbleInterface | None = None,
        sensor: SensorInterface | None = None,
        log_callback: LogCallback | str | Logger | None = None,
        perf: PerfInterface | None = None,
        location: LocationInterface | None = None,
        core_assets_dir: Directory | None = None,
        save_dir: Directory | None = None,
        username: str | bytes | None = "libretro.py",
        language: Language = Language.ENGLISH,
        vfs: FileSystemInterface | Literal[1, 2, 3] | None = None,
        led: LedInterface | None = None,
        av_enable: AvEnableFlags = AvEnableFlags.AUDIO | AvEnableFlags.VIDEO,
        midi: MidiInterface | None = None,
        target_refresh_rate: float = 60.0,
        preferred_hw: HardwareContext | None = HardwareContext.NONE,
        driver_switch_enable: bool = False,
        max_users: int = 8,
        throttle_state: retro_throttle_state | None = None,
        savestate_context: SavestateContext = SavestateContext.NORMAL,
        jit_capable: bool = True,
        mic_interface: MicrophoneInterface | MicrophoneInputIterator | MicrophoneInputGenerator | None = None,
        device_power: DevicePower | retro_device_power = full_power,
        playlist_dir: Directory | None = None,
        ) -> Session:
    """
    Returns a Session with default state objects.
    """

    core_impl: Core
    match core:
        case str(path) | PathLike(path) | CDLL(path):
            # Load a private copy of the core
            core_impl = Core(path)
        case Core() as c:
            # Use the provided core
            core_impl = c
        case _:
            raise TypeError(f"Expected core to be a string, path, Core, or CDLL; got {type(core).__name__}")

    logger = logging.getLogger('libretro')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    input_impl: InputState | None = None
    if isinstance(input_state, InputState):
        input_impl = input_state
    elif isinstance(input_state, Iterable):
        input_impl = GeneratorInputState(input_state)
    elif isinstance(input_state, Callable):
        input_impl = GeneratorInputState(input_state)

    options_impl: OptionState
    match options:
        case OptionState():
            options_impl = options
        case map if isinstance(map, Mapping):
            options_impl = StandardOptionState(2, True, map)
        case None:
            options_impl = StandardOptionState()
        case _:
            raise TypeError(f"Expected options to be an OptionState or a Mapping, not {type(options).__name__}")

    vfs_impl: FileSystemInterface
    match vfs:
        case FileSystemInterface() as v:
            vfs_impl = v
        case None:
            vfs_impl = StandardFileSystemInterface(logger=logger)
        case 1 | 2 | 3 as version:
            vfs_impl = StandardFileSystemInterface(version, logger=logger)
        case int() as i:
            raise ValueError(f"Expected a VFS version of 1, 2, or 3; got {i}")
        case _:
            raise TypeError(f"Expected vfs to be a FileSystemInterface or None, not {type(vfs).__name__}")

    mic_impl: MicrophoneInterface
    match mic_interface:
        case MicrophoneInterface() as m:
            mic_impl = m
        case m if callable(m):
            mic_impl = GeneratorMicrophoneInterface(m)
        case None:
            mic_impl = GeneratorMicrophoneInterface()
        case _:
            raise TypeError(f"Expected mic_interface to be a MicrophoneInterface or None, not {type(mic_interface).__name__}")

    power_impl: DevicePower
    match device_power:
        case retro_device_power() as p:
            power_impl = lambda: p
        case p if callable(p):
            power_impl = p
        case _:
            raise TypeError(f"Expected device_power to be a retro_device_power or a callable that returns one, not {type(device_power).__name__}")

    return Session(
        core=core_impl,
        audio=audio or ArrayAudioState(),
        input_state=input_impl or GeneratorInputState(),
        video=video or PillowVideoDriver(),
        content=content,
        overscan=overscan,
        message=message or LoggerMessageInterface(1, logger),
        options=options_impl,
        system_dir=system_dir,
        rumble=rumble or DefaultRumbleInterface(),
        sensor=sensor or GeneratorSensorInterface(),
        log_callback=log_callback or UnformattedLogger(),
        perf=perf or DefaultPerfInterface(),
        location=location or GeneratorLocationInterface(),
        core_assets_dir=core_assets_dir,
        save_dir=save_dir,
        username=username,
        language=language,
        vfs=vfs_impl,
        led=led or DictLedInterface(),
        av_enable=av_enable,
        midi=midi or GeneratorMidiInterface(),
        target_refresh_rate=target_refresh_rate,
        preferred_hw=preferred_hw,
        driver_switch_enable=driver_switch_enable,
        max_users=max_users,
        throttle_state=throttle_state or retro_throttle_state(ThrottleMode.NONE, 1.0),
        savestate_context=savestate_context,
        jit_capable=jit_capable,
        mic_interface=mic_impl,
        device_power=power_impl,
        playlist_dir=playlist_dir
    )


__all__ = [
    'Session',
    'default_session',
    'DoNotLoad',
    'CoreShutDownException',
]
