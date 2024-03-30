import ctypes
from collections.abc import Sequence
from copy import deepcopy
from ctypes import c_char_p, c_bool, c_uint, c_float, c_uint64
from os import PathLike
from typing import TypedDict, Required, override, Type, AnyStr

import _ctypes
from _ctypes import POINTER

from .. import LogCallback
from ..content import SubsystemContent, Content
from ..input import InputState
from ..led import LedInterface
from ..location import LocationInterface
from ..microphone import MicrophoneDriver
from ..midi import MidiInterface
from ..options import OptionDriver
from ..perf import PerfInterface
from ..rumble import RumbleInterface, retro_set_rumble_state_t
from ..savestate import SavestateContext, SerializationQuirks
from ..sensor import SensorInterface
from ..system import Language
from ..vfs import FileSystemInterface, retro_vfs_interface
from ..._utils import as_bytes, from_zero_terminated

from ...api.audio import *
from ...api.audio.callback import *
from ...api.av.defs import *
from ...api.camera import retro_camera_callback
from ...api.content import retro_game_info_ext, retro_system_content_info_override, retro_subsystem_info
from ...api.disk import retro_disk_control_ext_callback, retro_disk_control_callback
from ...api.environment.default import DefaultEnvironmentDriver
from ...api.input.info import retro_controller_info, retro_input_descriptor
from ...api.input.keyboard import retro_keyboard_callback
from ...api.led import retro_led_interface
from ...api.location import retro_location_callback
from ...api.log import retro_log_callback
from ...api.memory import retro_memory_map
from ...api.message import retro_message_ext, retro_message, MessageInterface
from ...api.microphone import retro_microphone_interface
from ...api.midi import retro_midi_interface
from ...api.netpacket import retro_netpacket_callback
from ...api.options import *
from ...api.perf import retro_perf_callback
from ...api.power import retro_device_power, DevicePower
from ...api.proc import retro_get_proc_address_interface
from ...api.rumble import retro_rumble_interface
from ...api.sensor import retro_sensor_interface
from ...api.throttle import retro_throttle_state, retro_fastforwarding_override, ThrottleMode
from ...api.vfs import retro_vfs_interface_info
from ...api.video import *
from ...h import retro_savestate_context, retro_hw_context_type, retro_av_enable_flags, retro_language, \
    retro_pixel_format


class CompositeEnvironmentDriver(DefaultEnvironmentDriver):
    class Args(TypedDict, total=False):
        audio: Required[AudioState]
        input: Required[InputState]
        video: Required[VideoDriver]
        overscan: bool | None
        message: MessageInterface | None
        options: OptionDriver | None
        system_dir: str | bytes | PathLike | None
        rumble: RumbleInterface | None
        sensor: SensorInterface | None
        log_callback: LogCallback | None
        perf: PerfInterface | None
        location: LocationInterface | None
        core_assets_dir: str | bytes | PathLike | None
        save_dir: str | bytes | PathLike | None
        username: str | bytes | None
        language: Language | None
        vfs: FileSystemInterface | None
        led: LedInterface | None
        av_enable: AvEnableFlags | None
        midi: MidiInterface | None
        target_refresh_rate: float | None
        preferred_hw: HardwareContext | None
        driver_switch_enable: bool | None
        max_users: int | None
        throttle_state: retro_throttle_state | None
        savestate_context: SavestateContext | None
        jit_capable: bool | None
        mic_interface: MicrophoneDriver | None
        device_power: DevicePower | None
        playlist_dir: str | bytes | PathLike | None

    @override
    def __init__(self, kwargs: Args):
        super().__init__()
        self._audio = kwargs['audio']
        self._input = kwargs['input']
        self._video = kwargs['video']
        self._overscan = kwargs.get('overscan')
        self._message = kwargs.get('message')
        self._shutdown = False
        self._performance_level: int | None = None
        self._system_dir = as_bytes(kwargs.get('system_dir'))
        self._input_descriptors: Sequence[retro_input_descriptor] | None = None
        self._options = kwargs.get('options')
        self._support_no_game: bool | None = None
        self._rumble = kwargs.get('rumble')
        self._sensor = kwargs.get('sensor')
        self._log = kwargs.get('log_callback')
        self._perf = kwargs.get('perf')
        self._location = kwargs.get('location')
        self._core_assets_dir = as_bytes(kwargs.get('core_assets_dir'))
        self._save_dir = as_bytes(kwargs.get('save_dir'))
        self._proc_address_callback: retro_get_proc_address_interface | None = None
        self._subsystem_info: Sequence[retro_subsystem_info] | None = None
        self._controller_infos: Sequence[retro_controller_info] | None = None
        self._memory_maps: retro_memory_map | None = None
        self._username = kwargs.get('username')
        self._language = kwargs.get('language')
        self._supports_achievements: bool | None = None
        self._serialization_quirks: SerializationQuirks | None = None
        self._vfs = kwargs.get('vfs')
        self._led = kwargs.get('led')
        self._av_enable = kwargs.get('av_enable')
        self._midi = kwargs.get('midi')
        self._target_refresh_rate = kwargs.get('target_refresh_rate')
        self._preferred_hw = kwargs.get('preferred_hw')
        self._driver_switch_enable = kwargs.get('driver_switch_enable')
        self._max_users = kwargs.get('max_users')
        self._throttle_state = kwargs.get('throttle_state')
        self._savestate_context = kwargs.get('savestate_context')
        self._jit_capable = kwargs.get('jit_capable')
        self._mic_interface = kwargs.get('mic_interface')
        self._device_power = kwargs.get('device_power')
        self._playlist_dir = kwargs.get('playlist_dir')

    @property
    def audio(self) -> AudioState:
        return self._audio

    @property
    def input(self) -> InputState:
        return self._input

    @property
    def video(self) -> VideoDriver:
        return self._video

    @property
    def rotation(self) -> Rotation:
        return self._video.rotation

    @override
    def _set_rotation(self, rotation_ptr: POINTER(c_uint)) -> bool:
        if not rotation_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_ROTATION doesn't accept NULL")

        rot: Rotation = Rotation(rotation_ptr[0])
        return self._video.set_rotation(rot)


    @property
    def overscan(self) -> bool | None:
        return self._overscan

    @overscan.setter
    def overscan(self, value: bool) -> None:
        self._overscan = bool(value)

    @overscan.deleter
    def overscan(self) -> None:
        self._overscan = None

    @override
    def _get_overscan(self, overscan_ptr: POINTER(c_bool)) -> bool:
        if self.overscan is None:
            return False

        if not overscan_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_OVERSCAN doesn't accept NULL")

        overscan_ptr[0] = self.overscan
        return True

    @property
    def can_dupe(self) -> bool:
        return self._video.can_dupe

    @override
    def _get_can_dupe(self, can_dupe_ptr: POINTER(c_bool)) -> bool:
        if not can_dupe_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_CAN_DUPE doesn't accept NULL")

        can_dupe_ptr[0] = self._video.can_dupe
        return True

    @property
    def message(self) -> MessageInterface | None:
        return self._message

    @message.setter
    def message(self, value: MessageInterface) -> None:
        if not isinstance(value, MessageInterface):
            raise TypeError(f"Expected MessageInterface, got {type(value)}")

        self._message = value

    @message.deleter
    def message(self) -> None:
        self._message = None

    @override
    def _set_message(self, message_ptr: POINTER(retro_message)) -> bool:
        if not self._message:
            return False

        if not message_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_MESSAGE doesn't accept NULL")

        message: retro_message = message_ptr[0]
        return self._message.set_message(message)

    @property
    def is_shutdown(self) -> bool:
        return self._shutdown

    @override
    def _shutdown(self) -> bool:
        self._shutdown = True
        return True

    @property
    def performance_level(self) -> int | None:
        return self._performance_level

    @performance_level.setter
    def performance_level(self, value: int) -> None:
        self._performance_level = int(value)

    @performance_level.deleter
    def performance_level(self) -> None:
        self._performance_level = None

    @override
    def _set_performance_level(self, level_ptr: POINTER(c_uint)) -> bool:
        if not level_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL doesn't accept NULL")

        self._performance_level = level_ptr[0]
        return True

    @property
    def system_dir(self) -> bytes | None:
        return self._system_dir

    @system_dir.setter
    def system_dir(self, value: str | bytes | PathLike) -> None:
        self._system_dir = as_bytes(value)

    @system_dir.deleter
    def system_dir(self) -> None:
        self._system_dir = None

    @override
    def _get_system_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._system_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._system_dir
        return True

    @property
    def pixel_format(self) -> PixelFormat:
        return self._video.pixel_format

    @override
    def _set_pixel_format(self, format_ptr: POINTER(retro_pixel_format)) -> bool:
        if not format_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_PIXEL_FORMAT doesn't accept NULL")

        _format = PixelFormat(format_ptr[0])
        return self._video.set_pixel_format(_format)

    @property
    def input_descriptors(self) -> Sequence[retro_input_descriptor] | None:
        return self._input_descriptors

    @input_descriptors.deleter
    def input_descriptors(self) -> None:
        self._input_descriptors = None

    @override
    def _set_input_descriptors(self, descriptors_ptr: POINTER(retro_input_descriptor)) -> bool:
        # TODO: Move input descriptor state to a new InputDriver
        if not descriptors_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS doesn't accept NULL")

        self._input_descriptors = tuple(deepcopy(s) for s in from_zero_terminated(descriptors_ptr))
        return True

    @override
    def _set_keyboard_callback(self, callback: POINTER(retro_keyboard_callback)) -> bool:
        return False  # TODO: Implement

    @override
    def _set_disk_control_interface(self, callback: POINTER(retro_disk_control_callback)) -> bool:
        return False  # TODO: Implement

    @override
    def _set_hw_render(self, data: POINTER(retro_hw_render_callback)) -> bool:
        return False  # TODO: Implement

    @property
    def options(self) -> OptionDriver:
        return self._options

    @options.setter
    def options(self, value: OptionDriver) -> None:
        if not isinstance(value, OptionDriver):
            raise TypeError(f"Expected OptionDriver, got {type(value).__name__}")

        self._options = value

    @options.deleter
    def options(self) -> None:
        self._options = None

    @override
    def _get_variable(self, var_ptr: POINTER(retro_variable)) -> bool:
        if not self._options:
            return False

        if var_ptr:
            var: retro_variable = var_ptr[0]

            result = self._options.get_variable(string_at(var.key) if var.key else None)
            var.value = result
            # Either a bytes for an option or None

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _set_variables(self, vars_ptr: POINTER(retro_variable)) -> bool:
        if not self._options:
            return False

        if vars_ptr:
            self._options.set_variables(tuple(deepcopy(s) for s in from_zero_terminated(vars_ptr)))
        else:
            self._options.set_variables(None)

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _get_variable_update(self, updated_ptr: POINTER(c_bool)) -> bool:
        if not self._options:
            return False

        if not updated_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE doesn't accept NULL")

        update_ptr = cast(updated_ptr, POINTER(c_bool))
        update_ptr[0] = self._options.variable_updated
        return True

    @property
    def support_no_game(self) -> bool | None:
        return self._support_no_game

    @override
    def _set_support_no_game(self, support_ptr: POINTER(c_bool)) -> bool:
        if not support_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME doesn't accept NULL")

        self._support_no_game = cast(support_ptr, POINTER(c_bool))[0]
        return True

    @override
    def _get_libretro_path(self, path: POINTER(c_char_p)) -> bool:
        return False  # TODO: Implement

    @override
    def _set_frame_time_callback(self, callback: POINTER(retro_frame_time_callback)) -> bool:
        return False  # TODO: Implement

    @override
    def _set_audio_callback(self, callback: POINTER(retro_audio_callback)) -> bool:
        return False  # TODO: Implement

    @property
    def rumble(self) -> RumbleInterface | None:
        return self._rumble

    @rumble.setter
    def rumble(self, value: RumbleInterface) -> None:
        if not isinstance(value, RumbleInterface):
            raise TypeError(f"Expected RumbleInterface, got {type(value).__name__}")

        self._rumble = value

    @rumble.deleter
    def rumble(self) -> None:
        self._rumble = None

    @override
    def _get_rumble_interface(self, data: POINTER(retro_rumble_interface)) -> bool:
        if not self._rumble:
            return False

        if not data:
            raise ValueError("RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE doesn't accept NULL")

        # TODO: Reimplement after refactoring the input driver
        # TODO: Provide a private entry-point wrapper functions for this callback
        # so that drivers can be swapped out without the risk of crashes

    @override
    def _get_input_device_capabilites(self, caps_ptr: POINTER(c_uint64)) -> bool:
        if not caps_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES doesn't accept NULL")

        caps_ptr[0] = self._input.device_capabilities
        return True

    @override
    def _get_sensor_interface(self, sensor_ptr: POINTER(retro_sensor_interface)) -> bool:
        if not sensor_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE doesn't accept NULL")

        # TODO: Reimplement after refactoring the sensor driver
        # TODO: Provide a private entry-point wrapper functions for this callback
        # so that drivers can be swapped out without the risk of crashes
        return False

    @override
    def _get_camera_interface(self, interface: POINTER(retro_camera_callback)) -> bool:
        return False # TODO: Implement

    @property
    def log(self) -> LogCallback | None:
        return self._log

    @log.setter
    def log(self, value: LogCallback) -> None:
        if not isinstance(value, LogCallback):
            raise TypeError(f"Expected LogCallback, got {type(value).__name__}")

        self._log = value

    @log.deleter
    def log(self) -> None:
        self._log = None

    @override
    def _get_log_interface(self, log_ptr: POINTER(retro_log_callback)) -> bool:
        if not self._log:
            return False

        if not log_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_LOG_INTERFACE doesn't accept NULL")

        log_ptr[0] = retro_log_callback.from_param(self._log)
        # TODO: Provide private entry-point wrapper functions for this callback
        # so that drivers can be swapped out without the risk of crashes
        return True

    @property
    def perf(self) -> PerfInterface | None:
        return self._perf

    @perf.setter
    def perf(self, value: PerfInterface) -> None:
        if not isinstance(value, PerfInterface):
            raise TypeError(f"Expected PerfInterface, got {type(value).__name__}")

        self._perf = value

    @perf.deleter
    def perf(self) -> None:
        self._perf = None

    def _get_perf_interface(self, perf_ptr: POINTER(retro_perf_callback)) -> bool:
        if not self._perf:
            return False

        if not perf_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_PERF_INTERFACE doesn't accept NULL")

        # TODO: Provide private entry-point wrapper functions for this callback
        # so that drivers can be swapped out without the risk of crashes
        perf_ptr[0] = retro_perf_callback.from_param(self._perf)
        return True

    @property
    def location(self) -> LocationInterface | None:
        return self._location

    @location.setter
    def location(self, value: LocationInterface) -> None:
        if not isinstance(value, LocationInterface):
            raise TypeError(f"Expected LocationInterface, got {type(value).__name__}")

        self._location = value

    @location.deleter
    def location(self) -> None:
        self._location = None

    @override
    def _get_location_interface(self, location_ptr: POINTER(retro_location_callback)) -> bool:
        if not self._location:
            return False

        if not location_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE doesn't accept NULL")

        location: retro_location_callback = location_ptr[0]

        self._location.initialized = location.initialized
        self._location.deinitialized = location.deinitialized

        memmove(location_ptr, byref(retro_location_callback.from_param(self._location)), sizeof(retro_location_callback))
        return True
        # TODO: Provide a private entry-point wrapper functions for this callback
        # so that drivers can be swapped out without the risk of crashes

    @property
    def core_assets_dir(self) -> bytes:
        return self._core_assets_dir

    @core_assets_dir.setter
    def core_assets_dir(self, value: str | bytes | PathLike) -> None:
        self._core_assets_dir = as_bytes(value)

    @core_assets_dir.deleter
    def core_assets_dir(self) -> None:
        self._core_assets_dir = None

    @override
    def _get_core_assets_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._core_assets_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._core_assets_dir
        return True

    @property
    def save_dir(self) -> bytes:
        return self._save_dir

    @save_dir.setter
    def save_dir(self, value: str | bytes | PathLike) -> None:
        self._save_dir = as_bytes(value)

    @save_dir.deleter
    def save_dir(self) -> None:
        self._save_dir = None

    @override
    def _get_save_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._save_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._save_dir
        return True

    @override
    def _set_system_av_info(self, info_ptr: POINTER(retro_system_av_info)) -> bool:
        if not info_ptr:
            return False

        av_info: retro_system_av_info = info_ptr[0]
        self._video.set_system_av_info(av_info)
        self._system_av_info = deepcopy(av_info)
        # TODO: Implement for audio drivers
        return True

    @property
    def proc_address_callback(self) -> retro_get_proc_address_interface | None:
        return self._proc_address_callback

    @proc_address_callback.setter
    def proc_address_callback(self, value: retro_get_proc_address_interface) -> None:
        if not isinstance(value, retro_get_proc_address_interface):
            raise TypeError(f"Expected retro_get_proc_address_interface, got {type(value).__name__}")

        self._proc_address_callback = value

    @proc_address_callback.deleter
    def proc_address_callback(self) -> None:
        self._proc_address_callback = None

    def get_proc_address(self, sym: AnyStr, funtype: type[_ctypes.CFuncPtr] | None) -> retro_proc_address_t | Callable[[], None] | None:
        if not self._proc_address_callback or not sym:
            return None

        name = as_bytes(sym)

        proc = self._proc_address_callback.get_proc_address(name)

        if not proc:
            return None

        if funtype:
            return funtype(proc)

        return proc

    @override
    def _set_proc_address_callback(self, procaddress_ptr: POINTER(retro_get_proc_address_interface)) -> bool:
        if not procaddress_ptr:
            self._proc_address_callback = None
        else:
            self._proc_address_callback = deepcopy(procaddress_ptr[0])

        return True

    @property
    def subsystem_info(self) -> Sequence[retro_subsystem_info] | None:
        return self._subsystem_info

    @override
    def _set_subsystem_info(self, info_ptr: POINTER(retro_subsystem_info)) -> bool:
        if not info_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO doesn't accept NULL")

        self._subsystem_info = tuple(deepcopy(s) for s in from_zero_terminated(info_ptr))
        return True

    @property
    def controller_info(self) -> Sequence[retro_controller_info] | None:
        return self._controller_infos

    @override
    def _set_controller_info(self, info_ptr: POINTER(retro_controller_info)) -> bool:
        if not info_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_CONTROLLER_INFO doesn't accept NULL")

        controller_infos = tuple(deepcopy(s) for s in from_zero_terminated(info_ptr))
        self._controller_infos = controller_infos

        return True

    @property
    def memory_maps(self) -> retro_memory_map | None:
        return self._memory_maps

    @override
    def _set_memory_maps(self, map_ptr: POINTER(retro_memory_map)) -> bool:
        if not map_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_MEMORY_MAPS doesn't accept NULL")

        memorymaps: retro_memory_map = map_ptr[0]
        self._memory_maps = deepcopy(memorymaps)
        return True

    @property
    def geometry(self) -> retro_game_geometry:
        return self._video.geometry

    @override
    def _set_geometry(self, geometry_ptr: POINTER(retro_game_geometry)) -> bool:
        if not geometry_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_GEOMETRY doesn't accept NULL")

        geom: retro_game_geometry = geometry_ptr[0]
        self._video.set_geometry(geom)
        return True

    @property
    def username(self) -> bytes | None:
        return self._username

    @username.setter
    def username(self, value: str | bytes) -> None:
        self._username = as_bytes(value)

    @username.deleter
    def username(self) -> None:
        self._username = None

    def _get_username(self, username_ptr: POINTER(c_char_p)) -> bool:
        if self._username is None:
            return False

        if not username_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_USERNAME doesn't accept NULL")

        username_ptr[0] = self._username
        return True

    @property
    def language(self) -> Language | None:
        return self._language

    @language.setter
    def language(self, value: Language) -> None:
        if not isinstance(value, (int, Language)):
            raise TypeError(f"Expected Language, got {type(value).__name__}")

        self._language = Language(value)

    @language.deleter
    def language(self) -> None:
        self._language = None

    @override
    def _get_language(self, language_ptr: POINTER(retro_language)) -> bool:
        if self._language is None:
            return False

        if not language_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_LANGUAGE doesn't accept NULL")

        language_ptr[0] = self._language
        return True
        # TODO: Move to a UserDriver

    @override
    def _get_current_software_framebuffer(self, framebuffer_ptr: POINTER(retro_framebuffer)) -> bool:
        if not framebuffer_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER doesn't accept NULL")

        core_fb: retro_framebuffer = framebuffer_ptr[0]
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

    @override
    def _get_hw_render_interface(self, hwrender_ptr: POINTER(retro_hw_render_interface)) -> bool:
        if not hwrender_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE doesn't accept NULL")

        hwrender_interface = self._video.hw_render_interface
        if not hwrender_interface:
            # This video driver doesn't provide (or need) a hardware render interface
            return False

        hwrender_ptr[0] = pointer(hwrender_interface)
        return True

    @property
    def support_achievements(self) -> bool | None:
        return self._supports_achievements

    @override
    def _set_support_achievements(self, support_ptr: POINTER(c_bool)) -> bool:
        if not support_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS doesn't accept NULL")

        self._supports_achievements = support_ptr[0]
        return True

    @override
    def _set_hw_render_context_negotiation_interface(
        self,
        interface: POINTER(retro_hw_render_context_negotiation_interface)
    ) -> bool:
        return False  # TODO: Implement

    @property
    def serialization_quirks(self) -> SerializationQuirks:
        return self._serialization_quirks

    @override
    def _set_serialization_quirks(self, quirks_ptr: POINTER(c_uint64)) -> bool:
        if not quirks_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS doesn't accept NULL")

        self._serialization_quirks = SerializationQuirks(quirks_ptr[0])
        return True

    @property
    def hw_shared_context(self) -> bool:
        return self._video.shared_context

    def _set_hw_shared_context(self) -> bool:
        self._video.shared_context = True
        return True

    @property
    def vfs(self) -> FileSystemInterface | None:
        return self._vfs

    @vfs.setter
    def vfs(self, value: FileSystemInterface) -> None:
        if not isinstance(value, FileSystemInterface):
            raise TypeError(f"Expected FileSystemInterface, got {type(value).__name__}")

        self._vfs = value

    @vfs.deleter
    def vfs(self) -> None:
        self._vfs = None

    @override
    def _get_vfs_interface(self, vfs_ptr: POINTER(retro_vfs_interface_info)) -> bool:
        if not self._vfs:
            return False

        if not vfs_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_VFS_INTERFACE doesn't accept NULL")

        vfs_info: retro_vfs_interface_info = vfs_ptr[0]

        if vfs_info.required_interface_version > self._vfs.version:
            # If the core wants a higher version than what we offer...
            return False

        vfs_info.required_interface_version = self._vfs.version
        vfs_info.iface = pointer(retro_vfs_interface.from_param(self._vfs))
        return True

    @property
    def led(self) -> LedInterface | None:
        return self._led

    @led.setter
    def led(self, value: LedInterface) -> None:
        if not isinstance(value, LedInterface):
            raise TypeError(f"Expected LedInterface, got {type(value).__name__}")

        self._led = value

    @led.deleter
    def led(self) -> None:
        self._led = None

    def _get_led_interface(self, led_ptr: POINTER(retro_led_interface)) -> bool:
        if not self._led:
            return False

        if led_ptr:
            memmove(led_ptr, byref(retro_led_interface.from_param(self._led)), sizeof(retro_led_interface))

        # This envcall supports passing NULL to query for support
        return True

    @property
    def av_enable(self) -> AvEnableFlags | None:
        return self._av_enable

    @av_enable.setter
    def av_enable(self, value: AvEnableFlags) -> None:
        if not isinstance(value, (int, AvEnableFlags)):
            raise TypeError(f"Expected AvEnableFlags, got {type(value).__name__}")
        self._av_enable = AvEnableFlags(value)

    @av_enable.deleter
    def av_enable(self) -> None:
        self._av_enable = None

    @override
    def _get_audio_video_enable(self, enable_ptr: POINTER(retro_av_enable_flags)) -> bool:
        if enable_ptr:
            enable_ptr[0] = self._av_enable

        # This envcall supports passing NULL to query for support
        return True
        # TODO: Derive this from the audio, video, and state drivers

    @property
    def midi(self) -> MidiInterface | None:
        return self._midi

    @midi.setter
    def midi(self, value: MidiInterface) -> None:
        if not isinstance(value, MidiInterface):
            raise TypeError(f"Expected MidiInterface, got {type(value).__name__}")

        self._midi = value

    @midi.deleter
    def midi(self) -> None:
        self._midi = None

    @override
    def _get_midi_interface(self, midi_ptr: POINTER(retro_midi_interface)) -> bool:
        if not self._midi:
            return False

        if midi_ptr:
            memmove(midi_ptr, byref(retro_midi_interface.from_param(self._midi)), sizeof(retro_midi_interface))

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _get_fastforwarding(self, fastforwarding_ptr: POINTER(c_bool)) -> bool:
        if self._throttle_state is None:
            return False

        if not fastforwarding_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_FASTFORWARDING doesn't accept NULL")

        fastforwarding_ptr[0] = self._throttle_state.mode.value == ThrottleMode.FAST_FORWARD
        return True

    @property
    def target_refresh_rate(self) -> float | None:
        return self._target_refresh_rate

    @target_refresh_rate.setter
    def target_refresh_rate(self, value: float) -> None:
        self._target_refresh_rate = float(value)

    @target_refresh_rate.deleter
    def target_refresh_rate(self) -> None:
        self._target_refresh_rate = None

    @override
    def _get_target_refresh_rate(self, rate_ptr: POINTER(c_float)) -> bool:
        if self._target_refresh_rate is None:
            return False

        if not rate_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE doesn't accept NULL")

        refresh_rate_ptr = cast(rate_ptr, POINTER(c_float))
        refresh_rate_ptr[0] = self._target_refresh_rate
        return True
        # TODO: Move to a new AV driver

    @property
    def input_bitmasks(self) -> bool:
        return self._input.bitmasks_supported

    @override
    def _get_input_bitmasks(self) -> bool:
        return self._input.bitmasks_supported

    @property
    def core_options_version(self) -> int | None:
        return self._options.version if self._options else None

    @override
    def _get_core_options_version(self, version_ptr: POINTER(c_uint)) -> bool:
        if not self._options:
            return False

        if not version_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION doesn't accept NULL")

        version_ptr[0] = self._options.version
        return True

    @override
    def _set_core_options(self, options_ptr: POINTER(retro_core_option_definition)) -> bool:
        if not self._options:
            return False

        if options_ptr:
            if self._options.get_version() < 1:
                return False

            self._options.set_options(tuple(deepcopy(o) for o in from_zero_terminated(options_ptr)))
        else:
            self._options.set_options(None)

        # This envcall supports passing NULL to reset the options
        return True

    @override
    def _set_core_options_intl(self, options_ptr: POINTER(retro_core_options_intl)) -> bool:
        if not self._options:
            return False

        if options_ptr:
            if self._options.get_version() < 1:
                return False

            self._options.set_options_intl(options_ptr[0])
        else:
            self._options.set_options_intl(None)

        # This envcall supports passing NULL to reset the options
        return True

    @override
    def _set_core_options_display(self, options_display_ptr: POINTER(retro_core_option_display)) -> bool:
        if not self._options:
            return False

        if options_display_ptr:
            opt_display: retro_core_option_display = options_display_ptr[0]

            if opt_display.key:
                self._options.set_display(opt_display.key, opt_display.visible)

        # This envcall supports passing NULL to query for support
        return True

    @property
    def preferred_hw_render(self) -> HardwareContext | None:
        return self._preferred_hw

    @preferred_hw_render.setter
    def preferred_hw_render(self, value: HardwareContext) -> None:
        if not isinstance(value, (int, HardwareContext)):
            raise TypeError(f"Expected HardwareContext, got {type(value).__name__}")

        self._preferred_hw = HardwareContext(value)

    @preferred_hw_render.deleter
    def preferred_hw_render(self) -> None:
        self._preferred_hw = None

    @override
    def _get_preferred_hw_render(self, preferred_ptr: POINTER(retro_hw_context_type)) -> bool:
        if self._preferred_hw is None:
            return False

        if not preferred_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER doesn't accept NULL")

        preferred_ptr[0] = self._preferred_hw

        # This envcall returns True if the frontend supports the call
        # *and* the frontend can switch video drivers
        return self._driver_switch_enable
        # TODO: Move RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER to the VideoDriver and _driver_switch_enable to the VideoDriver

    @override
    def _get_disk_control_interface_version(self, version: POINTER(c_uint)) -> bool:
        return False  # TODO: Implement

    @override
    def _set_disk_control_ext_interface(self, interface: POINTER(retro_disk_control_ext_callback)) -> bool:
        return False  # TODO: Implement

    def _get_message_interface_version(self, version_ptr: POINTER(c_uint)) -> bool:
        if not self._message:
            return False

        if not version_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_MESSAGE_INTERFACE_VERSION doesn't accept NULL")

        version_ptr[0] = self._message.version
        return True

    @override
    def _set_message_ext(self, message_ext_ptr: POINTER(retro_message_ext)) -> bool:
        if not self._message:
            return False

        if not message_ext_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_MESSAGE_EXT doesn't accept NULL")

        return self._message.set_message(message_ext_ptr[0])

    @override
    def _get_input_max_users(self, max_users: POINTER(c_uint)) -> bool:
        return False  # TODO: Define in the refactored input drivers instead

    @override
    def _set_audio_buffer_status_callback(self, callback: POINTER(retro_audio_buffer_status_callback)) -> bool:
        return False  # TODO: Implement

    @override
    def _set_minimum_audio_latency(self, latency: POINTER(c_uint)) -> bool:
        return False # TODO: Implement

    @override
    def _set_fastforwarding_override(self, override_ptr: POINTER(retro_fastforwarding_override)) -> bool:
        if override_ptr:
            fastforwarding: retro_fastforwarding_override = override_ptr[0]
            self._fastforwarding_override = deepcopy(retro_fastforwarding_override(fastforwarding))

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _set_content_info_override(self, override: POINTER(retro_system_content_info_override)) -> bool:
        return False # TODO: Implement in refactoed ContentDriver

    @override
    def _get_game_info_ext(self, info: POINTER(retro_game_info_ext)) -> bool:
        # TODO: Implement in refactored ContentDriver
        return False

    @override
    def _set_core_options_v2(self, options_ptr: POINTER(retro_core_options_v2)) -> bool:
        if not self._options:
            return False

        if self._options.get_version() < 2:
            return False

        if options_ptr:
            self._options.set_options_v2(options_ptr[0])
        else:
            self._options.set_options_v2(None)

        return self._options.supports_categories

    def _set_core_options_v2_intl(self, options_ptr: POINTER(retro_core_options_v2_intl)) -> bool:
        if not self._options:
            return False

        if self._options.get_version() < 2:
            return False

        if options_ptr:
            self._options.set_options_v2_intl(options_ptr[0])
        else:
            self._options.set_options_v2_intl(None)

        return self._options.supports_categories

    def _set_core_options_update_display_callback(
        self,
        callback_ptr: POINTER(retro_core_options_update_display_callback)
    ) -> bool:
        if not self._options:
            return False

        if callback_ptr:
            self._options.set_update_display_callback(callback_ptr[0])

        return True

    @override
    def _set_variable(self, variable_ptr: POINTER(retro_variable)) -> bool:
        if not self._options:
            return False

        if variable_ptr:
            var: retro_variable = variable_ptr[0]
            return self._options.set_variable(var.key, var.value)

        # This envcall supports passing NULL to query for support
        return True

    @property
    def throttle_state(self) -> retro_throttle_state | None:
        return self._throttle_state

    @throttle_state.setter
    def throttle_state(self, value: retro_throttle_state) -> None:
        if not isinstance(value, retro_throttle_state):
            raise TypeError(f"Expected retro_throttle_state, got {type(value).__name__}")

        self._throttle_state = value

    @throttle_state.deleter
    def throttle_state(self) -> None:
        self._throttle_state = None

    @override
    def _get_throttle_state(self, throttle_ptr: POINTER(retro_throttle_state)) -> bool:
        if not self._throttle_state:
            return False

        if not throttle_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_THROTTLE_STATE doesn't accept NULL")

        throttle_state: retro_throttle_state = throttle_ptr[0]

        throttle_state.mode = self._throttle_state.mode
        throttle_state.rate = self._throttle_state.rate

        return True

    @property
    def savestate_context(self) -> SavestateContext | None:
        return self._savestate_context

    @savestate_context.setter
    def savestate_context(self, value: SavestateContext) -> None:
        if not isinstance(value, (int, SavestateContext)):
            raise TypeError(f"Expected SavestateContext, got {type(value).__name__}")

        self._savestate_context = SavestateContext(value)

    @savestate_context.deleter
    def savestate_context(self) -> None:
        self._savestate_context = None

    @override
    def _get_savestate_context(self, context_ptr: POINTER(retro_savestate_context)) -> bool:
        if context_ptr:
            context_ptr[0] = self._savestate_context

        # This envcall supports passing NULL to query for support
        return True

    def _get_hw_render_context_negotiation_interface_support(
        self,
        support: POINTER(retro_hw_render_context_negotiation_interface)
    ) -> bool:
        return False  # TODO: Implement

    @property
    def jit_capable(self) -> bool | None:
        return self._jit_capable

    @jit_capable.setter
    def jit_capable(self, value: bool) -> None:
        self._jit_capable = bool(value)

    @jit_capable.deleter
    def jit_capable(self) -> None:
        self._jit_capable = None

    def _get_jit_capable(self, capable_ptr: POINTER(c_bool)) -> bool:
        if self._jit_capable is None:
            return False

        if not capable_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_JIT_CAPABLE doesn't accept NULL")

        capable_ptr[0] = self._jit_capable
        return True

    @property
    def microphones(self) -> MicrophoneDriver | None:
        return self._mic_interface

    @microphones.setter
    def microphones(self, value: MicrophoneDriver) -> None:
        if not isinstance(value, MicrophoneDriver):
            raise TypeError(f"Expected MicrophoneDriver, got {type(value).__name__}")

        self._mic_interface = value

    @microphones.deleter
    def microphones(self) -> None:
        self._mic_interface = None

    @override
    def _get_microphone_interface(self, mic_ptr: POINTER(retro_microphone_interface)) -> bool:
        if not self._mic_interface:
            return False

        if mic_ptr:
            mic_interface: retro_microphone_interface = mic_ptr[0]

            if mic_interface.interface_version != self._mic_interface.version:
                return False

            mic_ptr[0] = retro_microphone_interface.from_param(self._mic_interface)

        # This envcall supports passing NULL to query for support
        return True

    @property
    def power(self) -> retro_device_power | None:
        return self._device_power

    @power.setter
    def power(self, value: retro_device_power) -> None:
        if not isinstance(value, retro_device_power):
            raise TypeError(f"Expected retro_device_power, got {type(value).__name__}")

        self._device_power = value

    @power.deleter
    def power(self) -> None:
        self._device_power = None

    @override
    def _get_device_power(self, power_ptr: POINTER(retro_device_power)) -> bool:
        if not self._device_power:
            return False

        if power_ptr:
            memmove(power_ptr, byref(self._device_power), sizeof(retro_device_power))

        # This envcall supports passing NULL to query for support
        return True
        # TODO: Add a PowerDriver

    @override
    def _set_netpacket_interface(self, interface: POINTER(retro_netpacket_callback)) -> bool:
        return False  # TODO: Implement

    @property
    def playlist_directory(self) -> bytes | None:
        return self._playlist_dir

    @playlist_directory.setter
    def playlist_directory(self, value: str | bytes | PathLike) -> None:
        self._playlist_dir = as_bytes(value)

    @playlist_directory.deleter
    def playlist_directory(self) -> None:
        self._playlist_dir = None

    @override
    def _get_playlist_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._playlist_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._playlist_dir
        return True
