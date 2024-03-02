import ctypes
from typing import *
from abc import abstractmethod

from .core import Core
from ._libretro import *
from .defs import Rotation, PixelFormat, Language, EnvironmentCall, SerializationQuirks, SavestateContext
from .input import InputState
from .audio import AudioState
from .video import VideoState
from .interface.getprocaddress import *


class EnvironmentProtocol(Protocol):
    @abstractmethod
    @property
    def core(self) -> Core: ...

    def set_rotation(self, rotation: Rotation) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_ROTATION``.

        Parameters:
          rotation: The rotation to set.

        Returns:
          ``True`` if the rotation was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_overscan(self) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_OVERSCAN``.

        Returns:
          ``True`` if overscan is enabled,
          ``False`` if it's disabled,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_can_dupe(self) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_CAN_DUPE``.

        Returns:
          ``True`` if the core supports frame duplication,
          ``False`` if it doesn't,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_message(self, message: retro_message) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_MESSAGE``.

        Parameters:
          message: The message to set.

        Returns:
          ``True`` if the message was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def shutdown(self) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SHUTDOWN``.

        Returns:
          ``True`` if the core is scheduled to be shut down,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_performance_level(self, level: int) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL``.

        Parameters:
          level: The performance level to set.

        Returns:
          ``True`` if the performance level was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_system_directory(self) -> str | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY``.

        Returns:
          The path to the system directory,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_pixel_format(self, pixel_format: PixelFormat) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_PIXEL_FORMAT``.

        Parameters:
          pixel_format: The pixel format to set.

        Returns:
          ``True`` if the pixel format was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_input_descriptors(self, descriptors: Sequence[retro_input_descriptor]) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS``.

        Parameters:
          descriptors: The input descriptors to set.
           Includes a sentinel with a ``None`` description.

        Returns:
          ``True`` if the input descriptors were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_keyboard_callback(self, callback: retro_keyboard_callback) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK``.

        Parameters:
          callback: The keyboard callback to set.

        Returns:
          ``True`` if the keyboard callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_disk_control_interface(self, interface: retro_disk_control_callback) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_DISK_CONTROL_INTERFACE``.

        Parameters:
          interface: The disk control interface to set.

        Returns:
          ``True`` if the disk control interface was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_hw_render(self, callback: retro_hw_render_callback) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_HW_RENDER``.

        Parameters:
          callback: The hardware render callback to set.
            Modifies it in-place.

        Returns:
          ``True`` if the hardware render callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_variable(self, variable: retro_variable) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_VARIABLE``.

        Parameters:
          variable: The variable to get.
            Modifies it in-place.

        Returns:
          ``True`` if the variable was retrieved,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_variables(self, variables: Sequence[retro_variable]) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_VARIABLES``.

        Parameters:
          variables: The variables to set.
            Includes a sentinel with a ``None`` key.

        Returns:
          ``True`` if the variables were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_variable_update(self) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE``.

        Returns:
          ``True`` if a variable was updated,
          ``False`` if not,
          ``None`` if the environment call is not supported.
        """
        return None

    def set_support_no_game(self, support: bool) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME``.

        Parameters:
          support: Whether to support no-content.

        Returns:
          ``True`` if the support was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_libretro_path(self) -> str | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_LIBRETRO_PATH``.

        Returns:
          The path to the libretro core,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_frame_time_callback(self, callback: retro_frame_time_callback) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK``.

        Parameters:
          callback: The frame time callback to set.

        Returns:
          ``True`` if the frame time callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_audio_callback(self, callback: retro_audio_callback) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_AUDIO_CALLBACK``.

        Parameters:
          callback: The audio callback to set.

        Returns:
          ``True`` if the audio callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_rumble_interface(self) -> retro_rumble_interface | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE``.

        Returns:
          The rumble interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_input_device_capabilities(self) -> int | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES``.

        Returns:
          The input device capabilities,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_sensor_interface(self) -> retro_sensor_interface | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE``.

        Returns:
          The sensor interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_camera_interface(self) -> retro_camera_callback | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_CAMERA_INTERFACE``.

        Returns:
          The camera interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_log_interface(self) -> retro_log_callback | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_LOG_INTERFACE``.

        Returns:
          The log interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_perf_interface(self) -> retro_perf_callback | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_PERF_INTERFACE``.

        Returns:
          The performance interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_location_interface(self) -> retro_location_callback | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE``.

        Returns:
          The location interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_core_assets_directory(self) -> str | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY``.

        Returns:
          The path to the core's assets directory,
          or ``None`` if the environment call is not supported.
        """
        return None

    @final
    def get_content_directory(self) -> str | None:
        return self.get_core_assets_directory()

    def get_save_directory(self) -> str | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY``.

        Returns:
          The path to the save directory,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_system_av_info(self, info: retro_system_av_info) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO``.

        Parameters:
          info: The system AV info to set.

        Returns:
          ``True`` if the system AV info was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_proc_address_callback(self, callback: retro_get_proc_address_interface) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_PROC_ADDRESS_CALLBACK``.

        Parameters:
          callback: The proc address callback to set.

        Returns:
          ``True`` if the proc address callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_subsystem_info(self, info: Sequence[retro_subsystem_info]) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO``.

        Parameters:
          info: The subsystem info to set.
            May include a sentinel with a ``None`` description.

        Returns:
          ``True`` if the subsystem info was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_controller_info(self, info: retro_controller_info) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CONTROLLER_INFO``.

        Parameters:
          info: The controller info to set.
            May include a sentinel with a ``None`` description.

        Returns:
          ``True`` if the controller info was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_memory_maps(self, maps: retro_memory_map) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_MEMORY_MAPS``.

        Parameters:
          maps: The memory maps to set.

        Returns:
          ``True`` if the memory maps were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_geometry(self, geometry: retro_game_geometry) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_GEOMETRY``.

        Parameters:
          geometry: The game geometry to set.

        Returns:
          ``True`` if the game geometry was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_username(self) -> str | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_USERNAME``.

        Returns:
          The username,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_language(self) -> enum_retro_language | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_LANGUAGE``.

        Returns:
          The language,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_current_software_framebuffer(self, framebuffer: retro_framebuffer) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER``.
        
        Parameters:
          framebuffer: The framebuffer to get.
            Modifies it in-place.

        Returns:
          ``True`` if the framebuffer was retrieved,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_hw_render_interface(self) -> retro_hw_render_interface | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE``.

        Returns:
          The hardware render interface,
          or ``None`` if the environment call is not supported.
        """
        return None
    
    def set_support_achievements(self, support: bool) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS``.

        Parameters:
          support: Whether to support achievements.

        Returns:
          ``True`` if the support was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_hw_render_context_negotiation_interface(self, interface: retro_hw_render_context_negotiation_interface) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE``.

        Parameters:
          interface: The hardware render context negotiation interface to set.

        Returns:
          ``True`` if the hardware render context negotiation interface was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_serialization_quirks(self, quirks: SerializationQuirks) -> SerializationQuirks | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS``.

        Parameters:
          quirks: The serialization quirks to set.

        Returns:
          The original serialization quirks with all unrecognized flags set to zero,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_hw_shared_context(self) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_HW_SHARED_CONTEXT``.

        Returns:
          ``True`` if the hardware shared context was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_vfs_interface(self) -> retro_vfs_interface | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_VFS_INTERFACE``.

        Returns:
          The VFS interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_led_interface(self) -> retro_led_interface | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_LED_INTERFACE``.

        Returns:
          The LED interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_audio_video_enable(self) -> int | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE``.

        Returns:
          The audio/video enable state,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_midi_interface(self) -> retro_midi_interface | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_MIDI_INTERFACE``.

        Returns:
          The MIDI interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_fastforwarding(self) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_FASTFORWARDING``.

        Returns:
          ``True`` if fastforwarding is enabled,
          ``False`` if it's disabled,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_target_refresh_rate(self) -> float | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE``.

        Returns:
          The target refresh rate,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_input_bitmasks(self) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_INPUT_BITMASKS``.

        Returns:
          ``True`` if input bitmasks are enabled,
          ``False`` if they're disabled,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_core_options_version(self) -> int | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION``.

        Returns:
          The core options version,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_core_options(self, options: Sequence[retro_core_option_definition]) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS``.

        Parameters:
          options: The core options to set.
            May include a sentinel with a ``None`` key.

        Returns:
          ``True`` if the core options were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_core_options_intl(self, options: retro_core_options_intl) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL``.

        Parameters:
          options: The international core options to set.

        Returns:
          ``True`` if the international core options were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_core_options_display(self, options: retro_core_option_display) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY``.

        Parameters:
          options: The display core options to set.

        Returns:
          ``True`` if the display core options were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_preferred_hw_render(self) -> retro_hw_render | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER``.

        Returns:
          The preferred hardware render,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_disk_control_interface_version(self) -> int | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_DISK_CONTROL_INTERFACE_VERSION``.

        Returns:
          The disk control interface version,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_disk_control_ext_interface(self, interface: retro_disk_control_ext_callback) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_DISK_CONTROL_EXT_INTERFACE``.

        Parameters:
          interface: The disk control extended interface to set.

        Returns:
          ``True`` if the disk control extended interface was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_message_interface_version(self) -> int | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_MESSAGE_INTERFACE_VERSION``.

        Returns:
          The message interface version,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_message_ext(self, message: retro_message_ext) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_MESSAGE_EXT``.

        Parameters:
          message: The extended message to set.

        Returns:
          ``True`` if the extended message was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_input_max_users(self) -> int | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS``.

        Returns:
          The maximum number of users,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_audio_buffer_status_callback(self, callback: retro_audio_buffer_status_callback) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK``.

        Parameters:
          callback: The audio buffer status callback to set.

        Returns:
          ``True`` if the audio buffer status callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_minimum_audio_latency(self, latency: int) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY``.

        Parameters:
          latency: The minimum audio latency to set.

        Returns:
          ``True`` if the minimum audio latency was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_fastforwarding_override(self, override: retro_fastforwarding_override) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_FASTFORWARDING_OVERRIDE``.

        Parameters:
          override: The fastforwarding override to set.

        Returns:
          ``True`` if the fastforwarding override was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_content_info_override(self, info: Sequence[retro_system_content_info_override]) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE``.

        Parameters:
          info: The content info override to set.
            May include a sentinel with a ``None`` path.

        Returns:
          ``True`` if the content info override was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_game_info_ext(self) -> Sequence[retro_game_info_ext] | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_GAME_INFO_EXT``.

        Returns:
          The extended game info,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_core_options_v2(self, options: retro_core_options_v2 | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2``.

        Parameters:
          options: The core options to set.

        Returns:
          ``True`` if the core options were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_core_options_v2_intl(self, options: retro_core_options_intl | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL``.

        Parameters:
          options: The international core options to set.

        Returns:
          ``True`` if the international core options were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_core_options_update_display_callback(self, callback: retro_core_options_update_display_callback | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK``.

        Parameters:
          callback: The core options update display callback to set.

        Returns:
          ``True`` if the core options update display callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_variable(self, variable: retro_variable) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_VARIABLE``.

        Parameters:
          variable: The variable to set.

        Returns:
          ``True`` if the variable was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_throttle_state(self) -> retro_throttle_state | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_THROTTLE_STATE``.

        Returns:
          The throttle state,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_savestate_context(self) -> SavestateContext | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_SAVESTATE_CONTEXT``.

        Returns:
          The savestate context flags,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_hw_render_context_negotiation_interface_support(self, interface: retro_hw_render_context_negotiation_interface) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT``.

        Returns:
          ``True`` if the hardware render context negotiation interface is supported,
          ``False`` if it isn't,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_jit_capable(self) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_JIT_CAPABLE``.

        Returns:
          ``True`` if the core is JIT capable,
          ``False`` if it isn't,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_microphone_interface(self) -> retro_microphone_interface | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_MICROPHONE_INTERFACE``.

        Returns:
          The microphone interface,
          or ``None`` if the environment call is not supported.
        """
        return None

    def get_device_power(self) -> retro_device_power | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_DEVICE_POWER``.

        Returns:
          The device power state,
          or ``None`` if the environment call is not supported.
        """
        return None

    def retro_set_netpacket_interface(self, interface: retro_netpacket_callback | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE``.

        Parameters:
          interface: The netpacket interface to set.

        Returns:
          ``True`` if the netpacket interface was set,
          ``False`` if the environment call is not supported.
        """
        return False



class Environment:
    def __init__(
            self,
            core: Core | str | CDLL,
            audio: Optional[AudioState] = None,
            input_state: Optional[InputState] = None,
            video: Optional[VideoState] = None,
            system_directory: Optional[str] = None,
            save_directory: Optional[str] = None,
    ):
        if core is None:
            raise ValueError("Core cannot be None")

        if isinstance(core, Core):
            self._core = core
        else:
            self._core = Core(core)

        self._audio = audio or AudioState()
        self._input = input_state or InputState()
        self._video = video or VideoState()
        self._overrides: Dict[int, Any] = {}

        self._rotation: Optional[Rotation] = Rotation.NONE
        self._overscan: Optional[bool] = False
        self._performance_level: Optional[int] = None
        self._username: Optional[str] = "libretro.py"
        self._system_directory = system_directory
        self._pixel_format: PixelFormat = PixelFormat.RGB1555
        self._input_descriptors: Sequence[retro_input_descriptor] = []
        self._support_no_game = False
        self._save_directory = save_directory
        self._language: Optional[Language] = None
        self._support_achievements = False
        self._fastforwarding: Optional[bool] = False
        self._target_refresh_rate: Optional[float] = 60.0
        self._core_options_version: Optional[int] = 2

    @property
    def core(self) -> Core:
        return self._core

    @property
    def audio(self) -> AudioState:
        return self._audio

    @property
    def input(self) -> InputState:
        return self._input

    @property
    def video(self) -> VideoState:
        return self._video

    @property
    def rotation(self) -> Optional[Rotation]:
        return self._rotation

    @rotation.setter
    def rotation(self, value: Rotation):
        self._rotation = value

    @rotation.deleter
    def rotation(self):
        self._rotation = None

    @property
    def overscan(self) -> Optional[bool]:
        return self._overscan

    @overscan.setter
    def overscan(self, value: bool):
        self._overscan = value

    @overscan.deleter
    def overscan(self):
        self._overscan = None

    @property
    def performance_level(self) -> Optional[int]:
        return self._performance_level

    @performance_level.setter
    def performance_level(self, value: int):
        self._performance_level = value

    @performance_level.deleter
    def performance_level(self):
        self._performance_level = None

    @property
    def system_directory(self) -> Optional[str]:
        return self._system_directory

    @system_directory.setter
    def system_directory(self, value: str):
        self._system_directory = value

    @system_directory.deleter
    def system_directory(self):
        self._system_directory = None

    @property
    def pixel_format(self) -> PixelFormat:
        return self._pixel_format

    @pixel_format.setter
    def pixel_format(self, value: PixelFormat):
        self._pixel_format = value

    @pixel_format.deleter
    def pixel_format(self):
        self._pixel_format = PixelFormat.RGB1555

    @property
    def input_descriptors(self) -> Sequence[retro_input_descriptor]:
        return self._input_descriptors

    @input_descriptors.setter
    def input_descriptors(self, value: Sequence[retro_input_descriptor]):
        self._input_descriptors = list(value)

    @input_descriptors.deleter
    def input_descriptors(self):
        self._input_descriptors = None

    @property
    def support_no_game(self) -> bool:
        return self._support_no_game

    @support_no_game.setter
    def support_no_game(self, value: bool):
        self._support_no_game = value

    @support_no_game.deleter
    def support_no_game(self):
        self._support_no_game = False

    @property
    def save_directory(self) -> Optional[str]:
        return self._save_directory

    @save_directory.setter
    def save_directory(self, value: str):
        self._save_directory = value

    @save_directory.deleter
    def save_directory(self):
        self._save_directory = None

    @property
    def username(self) -> Optional[str]:
        return self._username

    @username.setter
    def username(self, value: str):
        self._username = value

    @username.deleter
    def username(self):
        self._username = None

    @property
    def language(self) -> Optional[Language]:
        return self._language

    @language.setter
    def language(self, value: Language):
        self._language = value

    @language.deleter
    def language(self):
        self._language = None

    @property
    def support_achievements(self) -> Optional[bool]:
        return self._support_achievements

    @support_achievements.setter
    def support_achievements(self, value: bool):
        self._support_achievements = value

    @support_achievements.deleter
    def support_achievements(self):
        self._support_achievements = None

    @property
    def fastforwarding(self) -> Optional[bool]:
        return self._fastforwarding

    @fastforwarding.setter
    def fastforwarding(self, value: bool):
        self._fastforwarding = value

    @fastforwarding.deleter
    def fastforwarding(self):
        self._fastforwarding = None

    @property
    def target_refresh_rate(self) -> Optional[float]:
        return self._target_refresh_rate

    @target_refresh_rate.setter
    def target_refresh_rate(self, value: float):
        self._target_refresh_rate = value

    @target_refresh_rate.deleter
    def target_refresh_rate(self):
        self._target_refresh_rate = None

    def environment(self, cmd: int, data: c_void_p) -> bool:
        if cmd in self._overrides:
            return self._overrides[cmd](data)

        match cmd:
            case EnvironmentCall.SetRotation:
                if self._rotation is not None:
                    # If the rotation envcall isn't disabled...
                    ptr = cast(data, POINTER(c_uint))
                    self._rotation = Rotation(ptr.contents)
                    return True

            case EnvironmentCall.GetOverscan:
                if self._overscan is not None:
                    # If the overscan envcall isn't disabled...
                    ptr = cast(data, POINTER(c_bool))
                    ptr.contents = self._overscan
                    return True

            case EnvironmentCall.SetPerformanceLevel:
                if self._performance_level is not None:
                    # If the performance level envcall isn't disabled...
                    ptr = cast(data, POINTER(c_uint))
                    self._performance_level = ptr.contents
                    return True

            case EnvironmentCall.GetSystemDirectory:
                if self._system_directory is not None:
                    # If the system directory envcall isn't disabled...
                    ptr = cast(data, POINTER(c_char_p))
                    ptr.contents = self._system_directory.encode()
                    return True

            case EnvironmentCall.SetPixelFormat:
                ptr = cast(data, POINTER(enum_retro_pixel_format))
                self._pixel_format = PixelFormat(ptr.contents)
                return True

            case EnvironmentCall.SetInputDescriptors:
                if self._input_descriptors is not None:
                    # If the input descriptors envcall isn't disabled...
                    ptr = cast(data, POINTER(retro_input_descriptor))
                    self._input_descriptors = []
                    i = 0
                    while ptr[i].contents.description is not None:
                        self._input_descriptors.append(ptr[i].contents)
                        i += 1

                    return True

            case EnvironmentCall.SetSupportNoGame:
                if self._support_no_game is not None:
                    # If the no-content envcall isn't disabled...
                    ptr = cast(data, POINTER(c_bool))
                    self._support_no_game = ptr.contents
                    return True

            case EnvironmentCall.SetSupportAchievements:
                if self._support_achievements is not None:
                    # If the achievements envcall isn't disabled...
                    ptr = cast(data, POINTER(c_bool))
                    self._support_achievements = ptr.contents
                    return True

            case EnvironmentCall.GetFastForwarding:
                if self._fastforwarding is not None:
                    # If the fastforwarding envcall isn't disabled...
                    ptr = cast(data, POINTER(c_bool))
                    ptr.contents = self._fastforwarding
                    return True

            case EnvironmentCall.GetTargetRefreshRate:
                if self._target_refresh_rate is not None:
                    # If the target refresh rate envcall isn't disabled...
                    ptr = cast(data, POINTER(c_float))
                    ptr.contents = self._target_refresh_rate
                    return True

        print(f"Unsupported environment call {cmd}")
        return False
