from collections.abc import Mapping
from ctypes import POINTER, c_bool, c_char_p, c_float, c_uint, c_uint64, cast

from libretro._typing import override
from libretro.api import (
    EnvironmentCall,
    retro_audio_buffer_status_callback,
    retro_audio_callback,
    retro_av_enable_flags,
    retro_camera_callback,
    retro_controller_info,
    retro_core_option_definition,
    retro_core_option_display,
    retro_core_options_intl,
    retro_core_options_update_display_callback,
    retro_core_options_v2,
    retro_core_options_v2_intl,
    retro_device_power,
    retro_disk_control_callback,
    retro_disk_control_ext_callback,
    retro_fastforwarding_override,
    retro_frame_time_callback,
    retro_framebuffer,
    retro_game_geometry,
    retro_game_info_ext,
    retro_get_proc_address_interface,
    retro_hw_context_type,
    retro_hw_render_callback,
    retro_hw_render_context_negotiation_interface,
    retro_hw_render_interface,
    retro_input_descriptor,
    retro_keyboard_callback,
    retro_language,
    retro_led_interface,
    retro_location_callback,
    retro_log_callback,
    retro_memory_map,
    retro_message,
    retro_message_ext,
    retro_microphone_interface,
    retro_midi_interface,
    retro_netpacket_callback,
    retro_perf_callback,
    retro_pixel_format,
    retro_rumble_interface,
    retro_savestate_context,
    retro_sensor_interface,
    retro_subsystem_info,
    retro_system_av_info,
    retro_system_content_info_override,
    retro_throttle_state,
    retro_variable,
    retro_vfs_interface_info,
)

from .dict import DictEnvironmentDriver, EnvironmentCallbackFunction


class DefaultEnvironmentDriver(DictEnvironmentDriver):
    @override
    def __init__(self):
        # We apply "type: ignore" to all the lambda functions in this dictionary because
        # the "Pointer" protocols I use for type safety aren't convertible to the standard _Pointer types,
        # even though they're replaced with said pointer types at runtime.
        envcalls: Mapping[EnvironmentCall, EnvironmentCallbackFunction] = {
            EnvironmentCall.SET_ROTATION: lambda data: self._set_rotation(
                cast(data, POINTER(c_uint))  # type: ignore
            ),
            EnvironmentCall.GET_OVERSCAN: lambda data: self._get_overscan(
                cast(data, POINTER(c_bool))  # type: ignore
            ),
            EnvironmentCall.GET_CAN_DUPE: lambda data: self._get_can_dupe(
                cast(data, POINTER(c_bool))  # type: ignore
            ),
            EnvironmentCall.SET_MESSAGE: lambda data: self._set_message(
                cast(data, POINTER(retro_message))  # type: ignore
            ),
            EnvironmentCall.SHUTDOWN: lambda _: self._shutdown(),
            EnvironmentCall.SET_PERFORMANCE_LEVEL: lambda data: self._set_performance_level(
                cast(data, POINTER(c_uint))  # type: ignore
            ),
            EnvironmentCall.GET_SYSTEM_DIRECTORY: lambda data: self._get_system_directory(
                cast(data, POINTER(c_char_p))  # type: ignore
            ),
            EnvironmentCall.SET_PIXEL_FORMAT: lambda data: self._set_pixel_format(
                cast(data, POINTER(retro_pixel_format))  # type: ignore
            ),
            EnvironmentCall.SET_INPUT_DESCRIPTORS: lambda data: self._set_input_descriptors(
                cast(data, POINTER(retro_input_descriptor))  # type: ignore
            ),
            EnvironmentCall.SET_KEYBOARD_CALLBACK: lambda data: self._set_keyboard_callback(
                cast(data, POINTER(retro_keyboard_callback))  # type: ignore
            ),
            EnvironmentCall.SET_DISK_CONTROL_INTERFACE: lambda data: self._set_disk_control_interface(
                cast(data, POINTER(retro_disk_control_callback))  # type: ignore
            ),
            EnvironmentCall.SET_HW_RENDER: lambda data: self._set_hw_render(
                cast(data, POINTER(retro_hw_render_callback))  # type: ignore
            ),
            EnvironmentCall.GET_VARIABLE: lambda data: self._get_variable(
                cast(data, POINTER(retro_variable))  # type: ignore
            ),
            EnvironmentCall.SET_VARIABLES: lambda data: self._set_variables(
                cast(data, POINTER(retro_variable))  # type: ignore
            ),
            EnvironmentCall.GET_VARIABLE_UPDATE: lambda data: self._get_variable_update(
                cast(data, POINTER(c_bool))  # type: ignore
            ),
            EnvironmentCall.SET_SUPPORT_NO_GAME: lambda data: self._set_support_no_game(
                cast(data, POINTER(c_bool))  # type: ignore
            ),
            EnvironmentCall.GET_LIBRETRO_PATH: lambda data: self._get_libretro_path(
                cast(data, POINTER(c_char_p))  # type: ignore
            ),
            EnvironmentCall.SET_FRAME_TIME_CALLBACK: lambda data: self._set_frame_time_callback(
                cast(data, POINTER(retro_frame_time_callback))  # type: ignore
            ),
            EnvironmentCall.SET_AUDIO_CALLBACK: lambda data: self._set_audio_callback(
                cast(data, POINTER(retro_audio_callback))  # type: ignore
            ),
            EnvironmentCall.GET_RUMBLE_INTERFACE: lambda data: self._get_rumble_interface(
                cast(data, POINTER(retro_rumble_interface))  # type: ignore
            ),
            EnvironmentCall.GET_INPUT_DEVICE_CAPABILITIES: lambda data: self._get_input_device_capabilities(
                cast(data, POINTER(c_uint64))  # type: ignore
            ),
            EnvironmentCall.GET_SENSOR_INTERFACE: lambda data: self._get_sensor_interface(
                cast(data, POINTER(retro_sensor_interface))  # type: ignore
            ),
            EnvironmentCall.GET_CAMERA_INTERFACE: lambda data: self._get_camera_interface(
                cast(data, POINTER(retro_camera_callback))  # type: ignore
            ),
            EnvironmentCall.GET_LOG_INTERFACE: lambda data: self._get_log_interface(
                cast(data, POINTER(retro_log_callback))  # type: ignore
            ),
            EnvironmentCall.GET_PERF_INTERFACE: lambda data: self._get_perf_interface(
                cast(data, POINTER(retro_perf_callback))  # type: ignore
            ),
            EnvironmentCall.GET_LOCATION_INTERFACE: lambda data: self._get_location_interface(
                cast(data, POINTER(retro_location_callback))  # type: ignore
            ),
            EnvironmentCall.GET_CORE_ASSETS_DIRECTORY: lambda data: self._get_core_assets_directory(
                cast(data, POINTER(c_char_p))  # type: ignore
            ),
            EnvironmentCall.GET_SAVE_DIRECTORY: lambda data: self._get_save_directory(
                cast(data, POINTER(c_char_p))  # type: ignore
            ),
            EnvironmentCall.SET_SYSTEM_AV_INFO: lambda data: self._set_system_av_info(
                cast(data, POINTER(retro_system_av_info))  # type: ignore
            ),
            EnvironmentCall.SET_PROC_ADDRESS_CALLBACK: lambda data: self._set_proc_address_callback(
                cast(data, POINTER(retro_get_proc_address_interface))  # type: ignore
            ),
            EnvironmentCall.SET_SUBSYSTEM_INFO: lambda data: self._set_subsystem_info(
                cast(data, POINTER(retro_subsystem_info))  # type: ignore
            ),
            EnvironmentCall.SET_CONTROLLER_INFO: lambda data: self._set_controller_info(
                cast(data, POINTER(retro_controller_info))  # type: ignore
            ),
            EnvironmentCall.SET_MEMORY_MAPS: lambda data: self._set_memory_maps(
                cast(data, POINTER(retro_memory_map))  # type: ignore
            ),
            EnvironmentCall.SET_GEOMETRY: lambda data: self._set_geometry(
                cast(data, POINTER(retro_game_geometry))  # type: ignore
            ),
            EnvironmentCall.GET_USERNAME: lambda data: self._get_username(
                cast(data, POINTER(c_char_p))  # type: ignore
            ),
            EnvironmentCall.GET_LANGUAGE: lambda data: self._get_language(
                cast(data, POINTER(retro_language))  # type: ignore
            ),
            EnvironmentCall.GET_CURRENT_SOFTWARE_FRAMEBUFFER: lambda data: self._get_current_software_framebuffer(
                cast(data, POINTER(retro_framebuffer))  # type: ignore
            ),
            EnvironmentCall.GET_HW_RENDER_INTERFACE: lambda data: self._get_hw_render_interface(
                cast(data, POINTER(retro_hw_render_interface))  # type: ignore
            ),
            EnvironmentCall.SET_SUPPORT_ACHIEVEMENTS: lambda data: self._set_support_achievements(
                cast(data, POINTER(c_bool))  # type: ignore
            ),
            EnvironmentCall.SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE: lambda data: self._set_hw_render_context_negotiation_interface(
                cast(data, POINTER(retro_hw_render_context_negotiation_interface))  # type: ignore
            ),
            EnvironmentCall.SET_SERIALIZATION_QUIRKS: lambda data: self._set_serialization_quirks(
                cast(data, POINTER(c_uint64))  # type: ignore
            ),
            EnvironmentCall.SET_HW_SHARED_CONTEXT: lambda _: self._set_hw_shared_context(),
            EnvironmentCall.GET_VFS_INTERFACE: lambda data: self._get_vfs_interface(
                cast(data, POINTER(retro_vfs_interface_info))  # type: ignore
            ),
            EnvironmentCall.GET_LED_INTERFACE: lambda data: self._get_led_interface(
                cast(data, POINTER(retro_led_interface))  # type: ignore
            ),
            EnvironmentCall.GET_AUDIO_VIDEO_ENABLE: lambda data: self._get_audio_video_enable(
                cast(data, POINTER(retro_av_enable_flags))  # type: ignore
            ),
            EnvironmentCall.GET_MIDI_INTERFACE: lambda data: self._get_midi_interface(
                cast(data, POINTER(retro_midi_interface))  # type: ignore
            ),
            EnvironmentCall.GET_FASTFORWARDING: lambda data: self._get_fastforwarding(
                cast(data, POINTER(c_bool))  # type: ignore
            ),
            EnvironmentCall.GET_TARGET_REFRESH_RATE: lambda data: self._get_target_refresh_rate(
                cast(data, POINTER(c_float))  # type: ignore
            ),
            EnvironmentCall.GET_INPUT_BITMASKS: lambda _: self._get_input_bitmasks(),
            EnvironmentCall.GET_CORE_OPTIONS_VERSION: lambda data: self._get_core_options_version(
                cast(data, POINTER(c_uint))  # type: ignore
            ),
            EnvironmentCall.SET_CORE_OPTIONS: lambda data: self._set_core_options(
                cast(data, POINTER(retro_core_option_definition))  # type: ignore
            ),
            EnvironmentCall.SET_CORE_OPTIONS_INTL: lambda data: self._set_core_options_intl(
                cast(data, POINTER(retro_core_options_intl))  # type: ignore
            ),
            EnvironmentCall.SET_CORE_OPTIONS_DISPLAY: lambda data: self._set_core_options_display(
                cast(data, POINTER(retro_core_option_display))  # type: ignore
            ),
            EnvironmentCall.GET_PREFERRED_HW_RENDER: lambda data: self._get_preferred_hw_render(
                cast(data, POINTER(retro_hw_context_type))  # type: ignore
            ),
            EnvironmentCall.GET_DISK_CONTROL_INTERFACE_VERSION: lambda data: self._get_disk_control_interface_version(
                cast(data, POINTER(c_uint))  # type: ignore
            ),
            EnvironmentCall.SET_DISK_CONTROL_EXT_INTERFACE: lambda data: self._set_disk_control_ext_interface(
                cast(data, POINTER(retro_disk_control_ext_callback))  # type: ignore
            ),
            EnvironmentCall.GET_MESSAGE_INTERFACE_VERSION: lambda data: self._get_message_interface_version(
                cast(data, POINTER(c_uint))  # type: ignore
            ),
            EnvironmentCall.SET_MESSAGE_EXT: lambda data: self._set_message_ext(
                cast(data, POINTER(retro_message_ext))  # type: ignore
            ),
            EnvironmentCall.GET_INPUT_MAX_USERS: lambda data: self._get_input_max_users(
                cast(data, POINTER(c_uint))  # type: ignore
            ),
            EnvironmentCall.SET_AUDIO_BUFFER_STATUS_CALLBACK: lambda data: self._set_audio_buffer_status_callback(
                cast(data, POINTER(retro_audio_buffer_status_callback))  # type: ignore
            ),
            EnvironmentCall.SET_MINIMUM_AUDIO_LATENCY: lambda data: self._set_minimum_audio_latency(
                cast(data, POINTER(c_uint))  # type: ignore
            ),
            EnvironmentCall.SET_FASTFORWARDING_OVERRIDE: lambda data: self._set_fastforwarding_override(
                cast(data, POINTER(retro_fastforwarding_override))  # type: ignore
            ),
            EnvironmentCall.SET_CONTENT_INFO_OVERRIDE: lambda data: self._set_content_info_override(
                cast(data, POINTER(retro_system_content_info_override))  # type: ignore
            ),
            EnvironmentCall.GET_GAME_INFO_EXT: lambda data: self._get_game_info_ext(
                cast(data, POINTER(POINTER(retro_game_info_ext)))  # type: ignore
            ),
            EnvironmentCall.SET_CORE_OPTIONS_V2: lambda data: self._set_core_options_v2(
                cast(data, POINTER(retro_core_options_v2))  # type: ignore
            ),
            EnvironmentCall.SET_CORE_OPTIONS_V2_INTL: lambda data: self._set_core_options_v2_intl(
                cast(data, POINTER(retro_core_options_v2_intl))  # type: ignore
            ),
            EnvironmentCall.SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK: lambda data: self._set_core_options_update_display_callback(
                cast(data, POINTER(retro_core_options_update_display_callback))  # type: ignore
            ),
            EnvironmentCall.SET_VARIABLE: lambda data: self._set_variable(
                cast(data, POINTER(retro_variable))  # type: ignore
            ),
            EnvironmentCall.GET_THROTTLE_STATE: lambda data: self._get_throttle_state(
                cast(data, POINTER(retro_throttle_state))  # type: ignore
            ),
            EnvironmentCall.GET_SAVESTATE_CONTEXT: lambda data: self._get_savestate_context(
                cast(data, POINTER(retro_savestate_context))  # type: ignore
            ),
            EnvironmentCall.GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT: lambda data: self._get_hw_render_context_negotiation_interface_support(
                cast(data, POINTER(retro_hw_render_context_negotiation_interface))  # type: ignore
            ),
            EnvironmentCall.GET_JIT_CAPABLE: lambda data: self._get_jit_capable(
                cast(data, POINTER(c_bool))  # type: ignore
            ),
            EnvironmentCall.GET_MICROPHONE_INTERFACE: lambda data: self._get_microphone_interface(
                cast(data, POINTER(retro_microphone_interface))  # type: ignore
            ),
            EnvironmentCall.GET_DEVICE_POWER: lambda data: self._get_device_power(
                cast(data, POINTER(retro_device_power))  # type: ignore
            ),
            EnvironmentCall.SET_NETPACKET_INTERFACE: lambda data: self._set_netpacket_interface(
                cast(data, POINTER(retro_netpacket_callback))  # type: ignore
            ),
            EnvironmentCall.GET_PLAYLIST_DIRECTORY: lambda data: self._get_playlist_directory(
                cast(data, POINTER(c_char_p))  # type: ignore
            ),
        }

        super().__init__(envcalls)


__all__ = [
    "DefaultEnvironmentDriver",
]
