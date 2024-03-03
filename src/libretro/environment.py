import ctypes
from typing import *
from abc import abstractmethod

from .core import Core
from ._libretro import *
from .defs import Rotation, PixelFormat, Language, EnvironmentCall, SerializationQuirks, SavestateContext
from .input import InputState
from .audio import AudioState
from .video import VideoState


class EnvironmentProtocol(Protocol):
    @abstractmethod
    @property
    def core(self) -> Core: ...

    def set_rotation(self, rotation: Rotation | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_ROTATION``.

        Parameters:
          rotation: The rotation to set.

        Returns:
          ``True`` if the rotation was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_overscan(self, overscan: POINTER(c_bool)) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_OVERSCAN``.

        Returns:
          ``True`` if overscan is enabled,
          ``False`` if it's disabled,
          or ``None`` if the environment call is not supported.
        """
        return False

    def get_can_dupe(self, can_dupe: c_bool | None) -> bool | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_CAN_DUPE``.

        Returns:
          ``True`` if the core supports frame duplication,
          ``False`` if it doesn't,
          or ``None`` if the environment call is not supported.
        """
        return None

    def set_message(self, message: retro_message | None) -> bool:
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

    def set_performance_level(self, level: int | None) -> bool:
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

    def set_pixel_format(self, pixel_format: PixelFormat | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_PIXEL_FORMAT``.

        Parameters:
          pixel_format: The pixel format to set.

        Returns:
          ``True`` if the pixel format was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_input_descriptors(self, descriptors: Sequence[retro_input_descriptor] | None) -> bool:
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

    def set_keyboard_callback(self, callback: retro_keyboard_callback | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK``.

        Parameters:
          callback: The keyboard callback to set.

        Returns:
          ``True`` if the keyboard callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_disk_control_interface(self, interface: retro_disk_control_callback | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_DISK_CONTROL_INTERFACE``.

        Parameters:
          interface: The disk control interface to set.

        Returns:
          ``True`` if the disk control interface was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_hw_render(self, callback: retro_hw_render_callback | None) -> bool:
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

    def get_variable(self, variable: retro_variable | None) -> bool:
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

    def set_variables(self, variables: Sequence[retro_variable] | None) -> bool:
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

    def set_support_no_game(self, support: bool | None) -> bool:
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

    def set_frame_time_callback(self, callback: retro_frame_time_callback | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK``.

        Parameters:
          callback: The frame time callback to set.

        Returns:
          ``True`` if the frame time callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_audio_callback(self, callback: retro_audio_callback | None) -> bool:
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

    def set_system_av_info(self, info: retro_system_av_info | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO``.

        Parameters:
          info: The system AV info to set.

        Returns:
          ``True`` if the system AV info was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_proc_address_callback(self, callback: retro_get_proc_address_interface | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_PROC_ADDRESS_CALLBACK``.

        Parameters:
          callback: The proc address callback to set.

        Returns:
          ``True`` if the proc address callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_subsystem_info(self, info: Sequence[retro_subsystem_info] | None) -> bool:
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

    def set_controller_info(self, info: retro_controller_info | None) -> bool:
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

    def set_memory_maps(self, maps: retro_memory_map | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_MEMORY_MAPS``.

        Parameters:
          maps: The memory maps to set.

        Returns:
          ``True`` if the memory maps were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_geometry(self, geometry: retro_game_geometry | None) -> bool:
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

    def get_current_software_framebuffer(self, framebuffer: retro_framebuffer | None) -> bool:
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
    
    def set_support_achievements(self, support: bool | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS``.

        Parameters:
          support: Whether to support achievements.

        Returns:
          ``True`` if the support was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_hw_render_context_negotiation_interface(self, interface: retro_hw_render_context_negotiation_interface | None) -> bool:
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

    def set_core_options(self, options: Sequence[retro_core_option_definition] | None) -> bool:
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

    def set_core_options_intl(self, options: retro_core_options_intl | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL``.

        Parameters:
          options: The international core options to set.

        Returns:
          ``True`` if the international core options were set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_core_options_display(self, options: retro_core_option_display | None) -> bool:
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

    def set_disk_control_ext_interface(self, interface: retro_disk_control_ext_callback | None) -> bool:
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

    def set_message_ext(self, message: retro_message_ext | None) -> bool:
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

    def set_audio_buffer_status_callback(self, callback: retro_audio_buffer_status_callback | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK``.

        Parameters:
          callback: The audio buffer status callback to set.

        Returns:
          ``True`` if the audio buffer status callback was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_minimum_audio_latency(self, latency: int | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY``.

        Parameters:
          latency: The minimum audio latency to set.

        Returns:
          ``True`` if the minimum audio latency was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_fastforwarding_override(self, override: retro_fastforwarding_override | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_FASTFORWARDING_OVERRIDE``.

        Parameters:
          override: The fastforwarding override to set.

        Returns:
          ``True`` if the fastforwarding override was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def set_content_info_override(self, info: Sequence[retro_system_content_info_override] | None) -> bool:
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

    def set_core_options_v2_intl(self, options: retro_core_options_v2_intl | None) -> bool:
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

    def set_variable(self, variable: retro_variable | None) -> bool:
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

    def set_netpacket_interface(self, interface: retro_netpacket_callback | None) -> bool:
        """
        Equivalent to ``RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE``.

        Parameters:
          interface: The netpacket interface to set.

        Returns:
          ``True`` if the netpacket interface was set,
          ``False`` if the environment call is not supported.
        """
        return False

    def get_playlist_directory(self) -> str | None:
        """
        Equivalent to ``RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY``.

        Returns:
          The path to the playlist directory,
          or ``None`` if the environment call is not supported.
        """
        return None

def environment_callback(env: EnvironmentProtocol) -> retro_environment_t:
    def callback(cmd: int, data: c_void_p) -> bool:
        match cmd:
            case EnvironmentCall.SetRotation:
                ptr = cast(data, POINTER(c_uint))
                value: Rotation | None = Rotation(ptr.contents) if ptr else None
                return env.set_rotation(value)

            case EnvironmentCall.GetOverscan:
                # TODO: Implement
                return False

            case EnvironmentCall.GetCanDupe:
                # TODO: Implement
                return False

            case EnvironmentCall.SetMessage:
                ptr = cast(data, POINTER(retro_message))
                value: retro_message | None = ptr.contents if ptr else None
                return env.set_message(value)

            case EnvironmentCall.Shutdown:
                return env.shutdown()

            case EnvironmentCall.SetPerformanceLevel:
                ptr = cast(data, POINTER(c_uint))
                value: int | None = int(ptr.contents) if ptr else None
                return env.set_performance_level(value)

            case EnvironmentCall.GetSystemDirectory:
                # TODO: Implement
                return False

            case EnvironmentCall.SetPixelFormat:
                ptr = cast(data, POINTER(c_uint))
                value: PixelFormat | None = PixelFormat(ptr.contents) if ptr else None
                return env.set_pixel_format(value)

            case EnvironmentCall.SetInputDescriptors:
                # TODO: Implement
                return False

            case EnvironmentCall.SetKeyboardCallback:
                ptr = cast(data, POINTER(retro_keyboard_callback))
                value: retro_keyboard_callback | None = ptr.contents if ptr else None
                return env.set_keyboard_callback(retro_keyboard_callback(data))

            case EnvironmentCall.SetDiskControlInterface:
                ptr = cast(data, POINTER(retro_disk_control_callback))
                value: retro_disk_control_callback | None = ptr.contents if ptr else None
                return env.set_disk_control_interface(value)

            case EnvironmentCall.SetHwRender:
                ptr = cast(data, POINTER(retro_hw_render_callback))
                value: retro_hw_render_callback | None = ptr.contents if ptr else None
                return env.set_hw_render(value)

            case EnvironmentCall.GetVariable:
                ptr = cast(data, POINTER(retro_variable))
                value: retro_variable | None = ptr.contents if ptr else None
                return env.get_variable(value)

            case EnvironmentCall.SetVariables:
                # TODO: Implement
                return False

            case EnvironmentCall.GetVariableUpdate:
                # TODO: Implement
                return False

            case EnvironmentCall.SetSupportNoGame:
                ptr = cast(data, POINTER(c_bool))
                value: bool | None = bool(ptr.contents) if ptr else None
                return env.set_support_no_game(value)

            case EnvironmentCall.GetLibretroPath:
                # TODO: Implement
                return False

            case EnvironmentCall.SetFrameTimeCallback:
                ptr = cast(data, POINTER(retro_frame_time_callback))
                value: retro_frame_time_callback | None = ptr.contents if ptr else None
                return env.set_frame_time_callback(value)

            case EnvironmentCall.SetAudioCallback:
                ptr = cast(data, POINTER(retro_audio_callback))
                value: retro_audio_callback | None = ptr.contents if ptr else None
                return env.set_audio_callback(value)

            case EnvironmentCall.GetRumbleInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetInputDeviceCapabilities:
                # TODO: Implement
                return False

            case EnvironmentCall.GetSensorInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetCameraInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetLogInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetPerfInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetLocationInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetCoreAssetsDirectory:
                # TODO: Implement
                return False

            case EnvironmentCall.GetSaveDirectory:
                # TODO: Implement
                return False

            case EnvironmentCall.SetSystemAvInfo:
                ptr = cast(data, POINTER(retro_system_av_info))
                value: retro_system_av_info | None = ptr.contents if ptr else None
                return env.set_system_av_info(value)

            case EnvironmentCall.SetProcAddressCallback:
                ptr = cast(data, POINTER(retro_get_proc_address_interface))
                value: retro_get_proc_address_interface | None = ptr.contents if ptr else None
                return env.set_proc_address_callback(value)

            case EnvironmentCall.SetSubsystemInfo:
                # TODO: Implement
                return False

            case EnvironmentCall.SetControllerInfo:
                # TODO: Implement
                return False

            case EnvironmentCall.SetMemoryMaps:
                ptr = cast(data, POINTER(retro_memory_map))
                value: retro_memory_map | None = ptr.contents if ptr else None
                return env.set_memory_maps(value)

            case EnvironmentCall.SetGeometry:
                ptr = cast(data, POINTER(retro_game_geometry))
                value: retro_game_geometry | None = ptr.contents if ptr else None
                return env.set_geometry(value)

            case EnvironmentCall.GetUsername:
                # TODO: Implement
                return False

            case EnvironmentCall.GetLanguage:
                # TODO: Implement
                return False

            case EnvironmentCall.GetCurrentSoftwareFramebuffer:
                # TODO: Implement
                return False

            case EnvironmentCall.GetHwRenderInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.SetSupportAchievements:
                ptr = cast(data, POINTER(c_bool))
                value: bool | None = bool(ptr.contents) if ptr else None
                return env.set_support_achievements(value)

            case EnvironmentCall.SetHwRenderContextNegotiationInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.SetSerializationQuirks:
                # TODO: Implement
                return False

            case EnvironmentCall.SetHwSharedContext:
                return env.set_hw_shared_context()

            case EnvironmentCall.GetVfsInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetLedInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetAudioVideoEnable:
                # TODO: Implement
                return False

            case EnvironmentCall.GetMidiInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetFastForwarding:
                # TODO: Implement
                return False

            case EnvironmentCall.GetTargetRefreshRate:
                # TODO: Implement
                return False

            case EnvironmentCall.GetInputBitmasks:
                # TODO: Implement
                return False

            case EnvironmentCall.GetCoreOptionsVersion:
                # TODO: Implement
                return False

            case EnvironmentCall.SetCoreOptions:
                # TODO: Implement
                return False

            case EnvironmentCall.SetCoreOptionsIntl:
                ptr = cast(data, POINTER(retro_core_options_intl))
                value: retro_core_options_intl | None = ptr.contents if ptr else None
                return env.set_core_options_intl(value)

            case EnvironmentCall.SetCoreOptionsDisplay:
                ptr = cast(data, POINTER(retro_core_option_display))
                value: retro_core_option_display | None = ptr.contents if ptr else None
                return env.set_core_options_display(value)

            case EnvironmentCall.GetPreferredHwRender:
                # TODO: Implement
                return False

            case EnvironmentCall.GetDiskControlInterfaceVersion:
                # TODO: Implement
                return False

            case EnvironmentCall.SetDiskControlExtInterface:
                ptr = cast(data, POINTER(retro_disk_control_ext_callback))
                value: retro_disk_control_ext_callback | None = ptr.contents if ptr else None
                return env.set_disk_control_ext_interface(value)

            case EnvironmentCall.GetMessageInterfaceVersion:
                # TODO: Implement
                return False

            case EnvironmentCall.SetMessageExt:
                ptr = cast(data, POINTER(retro_message_ext))
                value: retro_message_ext | None = ptr.contents if ptr else None
                return env.set_message_ext(value)

            case EnvironmentCall.GetInputMaxUsers:
                # TODO: Implement
                return False

            case EnvironmentCall.SetAudioBufferStatusCallback:
                ptr = cast(data, POINTER(retro_audio_buffer_status_callback))
                value: retro_audio_buffer_status_callback | None = ptr.contents if ptr else None
                return env.set_audio_buffer_status_callback(value)

            case EnvironmentCall.SetMinimumAudioLatency:
                ptr = cast(data, POINTER(c_uint))
                value: int | None = int(ptr.contents) if ptr else None
                return env.set_minimum_audio_latency(value)

            case EnvironmentCall.SetFastForwardingOverride:
                ptr = cast(data, POINTER(retro_fastforwarding_override))
                value: retro_fastforwarding_override | None = ptr.contents if ptr else None
                return env.set_fastforwarding_override(value)

            case EnvironmentCall.SetContentInfoOverride:
                # TODO: Implement
                return False

            case EnvironmentCall.GetGameInfoExt:
                # TODO: Implement
                return False

            case EnvironmentCall.SetCoreOptionsV2:
                # TODO: Implement
                return False

            case EnvironmentCall.SetCoreOptionsV2Intl:
                ptr = cast(data, POINTER(retro_core_options_v2_intl))
                value: retro_core_options_v2_intl | None = ptr.contents if ptr else None
                return env.set_core_options_v2_intl(value)

            case EnvironmentCall.SetCoreOptionsUpdateDisplayCallback:
                ptr = cast(data, POINTER(retro_core_options_update_display_callback))
                value: retro_core_options_update_display_callback | None = ptr.contents if ptr else None
                return env.set_core_options_update_display_callback(value)

            case EnvironmentCall.SetVariable:
                ptr = cast(data, POINTER(retro_variable))
                value: retro_variable | None = ptr.contents if ptr else None
                return env.set_variable(value)

            case EnvironmentCall.GetThrottleState:
                # TODO: Implement
                return False

            case EnvironmentCall.GetSaveStateContext:
                # TODO: Implement
                return False

            case EnvironmentCall.GetHwRenderContextNegotiationInterfaceSupport:
                # TODO: Implement
                return False

            case EnvironmentCall.GetJitCapable:
                # TODO: Implement
                return False

            case EnvironmentCall.GetMicrophoneInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetDevicePower:
                # TODO: Implement
                return False

            case EnvironmentCall.SetNetpacketInterface:
                ptr = cast(data, POINTER(retro_netpacket_callback))
                value: retro_netpacket_callback | None = ptr.contents if ptr else None
                return env.set_netpacket_interface(value)

            case EnvironmentCall.GetPlaylistDirectory:
                # TODO: Implement
                return False

            case _:
                return False


    return callback


class Environment:
    def __init__(
            self,
            core: Core | str | CDLL,
            audio: AudioState,
            input_state: InputState,
            video: VideoState,
            rotation: Rotation | NotImplemented = None,
            performance_level: int | None = None,
            system_directory: str | None = None,
            username: str | None = None,
            pixel_format: PixelFormat = PixelFormat.RGB1555,
            input_descriptors: Sequence[retro_input_descriptor] | None = None,
            support_no_game: bool | None = None,
            save_directory: str | None = None,
            proc_address_callback: GetProcAddressProtocol | None = None,
            language: Language | None = None,
            support_achievements: bool | None = None,
            fastforwarding: bool | None = None,
            target_refresh_rate: float | None = None,
            core_options_version: int | None = None,
            device_power: retro_device_power | None = None
    ):
        """
        Load a libretro core from a file and sets all the required retro_ callbacks.
        Does not call retro_init or retro_load_game.

        Parameters:
            core: The shared library that contains the core.
              Can be a path to a file or a CDLL instance.

        Returns:
            An environment object that can be used to manage the core's life and execution.

        Raises:
            ValueError: If `core` is missing a required symbol.
        """
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

        self.rotation = rotation
        self.overscan = overscan
        self.performance_level = performance_level
        self.username = username
        self.system_directory = system_directory
        self.pixel_format = pixel_format
        self.input_descriptors = input_descriptors
        self.support_no_game = support_no_game
        self.save_directory = save_directory
        self.proc_address_callback = proc_address_callback
        self.language = language
        self.support_achievements = support_achievements
        self.fastforwarding = fastforwarding
        self.target_refresh_rate = target_refresh_rate
        self.core_options_version = core_options_version
        self.device_power = device_power


    def __enter__(self):
        self._core.set_video_refresh(self._video.refresh)
        self._core.set_audio_sample(self._audio.audio_sample)
        self._core.set_audio_sample_batch(self._audio.audio_sample_batch)
        self._core.set_input_poll(self._input.poll)
        self._core.set_input_state(self._input.state)
        self._core.set_environment(self.environment)

        self._core.init()
        # TODO: Call retro_load_game or retro_load_game_special here (even if there's no content)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._core.unload_game()
        self._core.deinit()
        del self._core
        return False

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