from abc import abstractmethod
from ctypes import c_float, c_int16, c_uint, c_uint64, c_void_p
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from libretro.api import (
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

if TYPE_CHECKING:
    from libretro.typing import (
        BoolPointer,
        FloatPointer,
        IntPointer,
        StringPointer,
        StructurePointer,
    )


@runtime_checkable
class EnvironmentDriver(Protocol):
    @abstractmethod
    def environment(self, cmd: int, data: c_void_p) -> bool: ...

    @abstractmethod
    def video_refresh(self, data: c_void_p, width: int, height: int, pitch: int) -> None: ...

    @abstractmethod
    def audio_sample(self, left: int, right: int) -> None: ...

    @abstractmethod
    def audio_sample_batch(self, data: IntPointer[c_int16], frames: int) -> int: ...

    @abstractmethod
    def input_poll(self) -> None: ...

    @abstractmethod
    def input_state(self, port: int, device: int, index: int, id: int) -> int: ...

    def _set_rotation(self, rotation: IntPointer[c_uint]) -> bool:
        return False

    def _get_overscan(self, overscan: BoolPointer) -> bool:
        return False

    def _get_can_dupe(self, can_dupe: BoolPointer) -> bool:
        return False

    def _set_message(self, message: StructurePointer[retro_message]) -> bool:
        return False

    def _shutdown(self) -> bool:
        return False

    def _set_performance_level(self, level: IntPointer[c_uint]) -> bool:
        return False

    def _get_system_directory(self, dir: StringPointer) -> bool:
        return False

    def _set_pixel_format(self, fmt: IntPointer[retro_pixel_format]) -> bool:
        return False

    def _set_input_descriptors(
        self, descriptors: StructurePointer[retro_input_descriptor]
    ) -> bool:
        return False

    def _set_keyboard_callback(self, callback: StructurePointer[retro_keyboard_callback]) -> bool:
        return False

    def _set_disk_control_interface(
        self, callback: StructurePointer[retro_disk_control_callback]
    ) -> bool:
        return False

    def _set_hw_render(self, callback: StructurePointer[retro_hw_render_callback]) -> bool:
        return False

    def _get_variable(self, variable: StructurePointer[retro_variable]) -> bool:
        return False

    def _set_variables(self, variables: StructurePointer[retro_variable]) -> bool:
        return False

    def _get_variable_update(self, updated: BoolPointer) -> bool:
        return False

    def _set_support_no_game(self, support: BoolPointer) -> bool:
        return False

    def _get_libretro_path(self, path: StringPointer) -> bool:
        return False

    def _set_frame_time_callback(
        self, callback: StructurePointer[retro_frame_time_callback]
    ) -> bool:
        return False

    def _set_audio_callback(self, callback: StructurePointer[retro_audio_callback]) -> bool:
        return False

    def _get_rumble_interface(self, rumble: StructurePointer[retro_rumble_interface]) -> bool:
        return False

    def _get_input_device_capabilities(self, capabilities: IntPointer[c_uint64]) -> bool:
        return False

    def _get_sensor_interface(self, interface: StructurePointer[retro_sensor_interface]) -> bool:
        return False

    def _get_camera_interface(self, interface: StructurePointer[retro_camera_callback]) -> bool:
        return False

    def _get_log_interface(self, interface: StructurePointer[retro_log_callback]) -> bool:
        return False

    def _get_perf_interface(self, interface: StructurePointer[retro_perf_callback]) -> bool:
        return False

    def _get_location_interface(
        self, interface: StructurePointer[retro_location_callback]
    ) -> bool:
        return False

    def _get_core_assets_directory(self, dir: StringPointer) -> bool:
        return False

    def _get_save_directory(self, dir: StringPointer) -> bool:
        return False

    def _set_system_av_info(self, info: StructurePointer[retro_system_av_info]) -> bool:
        return False

    def _set_proc_address_callback(
        self, callback: StructurePointer[retro_get_proc_address_interface]
    ) -> bool:
        return False

    def _set_subsystem_info(self, info: StructurePointer[retro_subsystem_info]) -> bool:
        return False

    def _set_controller_info(self, info: StructurePointer[retro_controller_info]) -> bool:
        return False

    def _set_memory_maps(self, maps: StructurePointer[retro_memory_map]) -> bool:
        return False

    def _set_geometry(self, geometry: StructurePointer[retro_game_geometry]) -> bool:
        return False

    def _get_username(self, username: StringPointer) -> bool:
        return False

    def _get_language(self, language: IntPointer[retro_language]) -> bool:
        return False

    def _get_current_software_framebuffer(
        self, framebuffer: StructurePointer[retro_framebuffer]
    ) -> bool:
        return False

    def _get_hw_render_interface(
        self, interface: StructurePointer[retro_hw_render_interface]
    ) -> bool:
        return False

    def _set_support_achievements(self, support: BoolPointer) -> bool:
        return False

    def _set_hw_render_context_negotiation_interface(
        self, interface: StructurePointer[retro_hw_render_context_negotiation_interface]
    ) -> bool:
        return False

    def _set_serialization_quirks(self, quirks: IntPointer[c_uint64]) -> bool:
        return False

    def _set_hw_shared_context(self) -> bool:
        return False

    def _get_vfs_interface(self, vfs: StructurePointer[retro_vfs_interface_info]) -> bool:
        return False

    def _get_led_interface(self, led: StructurePointer[retro_led_interface]) -> bool:
        return False

    def _get_audio_video_enable(self, enable: IntPointer[retro_av_enable_flags]) -> bool:
        return False

    def _get_midi_interface(self, midi: StructurePointer[retro_midi_interface]) -> bool:
        return False

    def _get_fastforwarding(self, is_fastforwarding: BoolPointer) -> bool:
        return False

    def _get_target_refresh_rate(self, rate: FloatPointer[c_float]) -> bool:
        return False

    def _get_input_bitmasks(self) -> bool:
        return False

    def _get_core_options_version(self, version: IntPointer[c_uint]) -> bool:
        return False

    def _set_core_options(self, options: StructurePointer[retro_core_option_definition]) -> bool:
        return False

    def _set_core_options_intl(self, options: StructurePointer[retro_core_options_intl]) -> bool:
        return False

    def _set_core_options_display(
        self, options: StructurePointer[retro_core_option_display]
    ) -> bool:
        return False

    def _get_preferred_hw_render(self, preferred: IntPointer[retro_hw_context_type]) -> bool:
        return False

    def _get_disk_control_interface_version(self, version: IntPointer[c_uint]) -> bool:
        return False

    def _set_disk_control_ext_interface(
        self, interface: StructurePointer[retro_disk_control_ext_callback]
    ) -> bool:
        return False

    def _get_message_interface_version(self, version: IntPointer[c_uint]) -> bool:
        return False

    def _set_message_ext(self, interface: StructurePointer[retro_message_ext]) -> bool:
        return False

    def _get_input_max_users(self, max_users: IntPointer[c_uint]) -> bool:
        return False

    def _set_audio_buffer_status_callback(
        self, callback: StructurePointer[retro_audio_buffer_status_callback]
    ) -> bool:
        return False

    def _set_minimum_audio_latency(self, latency: IntPointer[c_uint]) -> bool:
        return False

    def _set_fastforwarding_override(
        self, override: StructurePointer[retro_fastforwarding_override]
    ) -> bool:
        return False

    def _set_content_info_override(
        self, override: StructurePointer[retro_system_content_info_override]
    ) -> bool:
        return False

    def _get_game_info_ext(self, info: StructurePointer[retro_game_info_ext]) -> bool:
        return False

    def _set_core_options_v2(self, options: StructurePointer[retro_core_options_v2]) -> bool:
        return False

    def _set_core_options_v2_intl(
        self, options: StructurePointer[retro_core_options_v2_intl]
    ) -> bool:
        return False

    def _set_core_options_update_display_callback(
        self, callback: StructurePointer[retro_core_options_update_display_callback]
    ) -> bool:
        return False

    def _set_variable(self, variable: StructurePointer[retro_variable]) -> bool:
        return False

    def _get_throttle_state(self, state: StructurePointer[retro_throttle_state]) -> bool:
        return False

    def _get_savestate_context(self, context: IntPointer[retro_savestate_context]) -> bool:
        return False

    def _get_hw_render_context_negotiation_interface_support(
        self, support: StructurePointer[retro_hw_render_context_negotiation_interface]
    ) -> bool:
        return False

    def _get_jit_capable(self, capable: BoolPointer) -> bool:
        return False

    def _get_microphone_interface(
        self, interface: StructurePointer[retro_microphone_interface]
    ) -> bool:
        return False

    def _get_device_power(self, power: StructurePointer[retro_device_power]) -> bool:
        return False

    def _set_netpacket_interface(
        self, interface: StructurePointer[retro_netpacket_callback]
    ) -> bool:
        return False

    def _get_playlist_directory(self, dir: StringPointer) -> bool:
        return False


__all__ = [
    "EnvironmentDriver",
]
