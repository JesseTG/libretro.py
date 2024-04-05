from abc import abstractmethod
from ctypes import POINTER, c_bool, c_char_p, c_float
from typing import Protocol, runtime_checkable

from ..audio.defs import *
from ..camera import *
from ..content import *
from ..disk import *
from ..input.rumble.defs import *
from ..input.sensor.defs import *
from ..input.defs import *
from ..led import *
from ..location import *
from ..log import *
from ..memory import *
from ..message import *
from ..microphone import retro_microphone_interface
from ..midi import *
from ..netpacket import retro_netpacket_callback
from ..options.defs import *
from ..perf import *
from ..power import retro_device_power
from ..proc import *
from ..timing import *
from ..vfs import *
from ..video import *
from ...h import *


# noinspection PyMethodMayBeStatic,PyUnusedLocal,PyShadowingNames
@runtime_checkable
class EnvironmentDriver(Protocol):
    @abstractmethod
    def environment(self, cmd: int, data: c_void_p) -> bool: ...

    def _set_rotation(self, rotation: POINTER(c_uint)) -> bool: return False

    def _get_overscan(self, overscan: POINTER(c_bool)) -> bool: return False

    def _get_can_dupe(self, can_dupe: POINTER(c_bool)) -> bool: return False

    def _set_message(self, message: POINTER(retro_message)) -> bool: return False

    def _shutdown(self) -> bool: return False

    def _set_performance_level(self, level: POINTER(c_uint)) -> bool: return False

    def _get_system_directory(self, dir: POINTER(c_char_p)) -> bool: return False

    def _set_pixel_format(self, fmt: POINTER(retro_pixel_format)) -> bool: return False

    def _set_input_descriptors(self, descriptors: POINTER(retro_input_descriptor)) -> bool: return False

    def _set_keyboard_callback(self, callback: POINTER(retro_keyboard_callback)) -> bool: return False

    def _set_disk_control_interface(self, callback: POINTER(retro_disk_control_callback)) -> bool: return False

    def _set_hw_render(self, data: POINTER(retro_hw_render_callback)) -> bool: return False

    def _get_variable(self, variable: POINTER(retro_variable)) -> bool: return False

    def _set_variables(self, variables: POINTER(retro_variable)) -> bool: return False

    def _get_variable_update(self, update: POINTER(c_bool)) -> bool: return False

    def _set_support_no_game(self, support: POINTER(c_bool)) -> bool: return False

    def _get_libretro_path(self, path: POINTER(c_char_p)) -> bool: return False

    def _set_frame_time_callback(self, callback: POINTER(retro_frame_time_callback)) -> bool: return False

    def _set_audio_callback(self, callback: POINTER(retro_audio_callback)) -> bool: return False

    def _get_rumble_interface(self, data: POINTER(retro_rumble_interface)) -> bool: return False

    def _get_input_device_capabilities(self, capabilities: POINTER(c_uint64)) -> bool: return False

    def _get_sensor_interface(self, interface: POINTER(retro_sensor_interface)) -> bool: return False

    def _get_camera_interface(self, interface: POINTER(retro_camera_callback)) -> bool: return False

    def _get_log_interface(self, interface: POINTER(retro_log_callback)) -> bool: return False

    def _get_perf_interface(self, interface: POINTER(retro_perf_callback)) -> bool: return False

    def _get_location_interface(self, interface: POINTER(retro_location_callback)) -> bool: return False

    def _get_core_assets_directory(self, dir: POINTER(c_char_p)) -> bool: return False

    def _get_save_directory(self, dir: POINTER(c_char_p)) -> bool: return False

    def _set_system_av_info(self, info: POINTER(retro_system_av_info)) -> bool: return False

    def _set_proc_address_callback(self, callback: POINTER(retro_get_proc_address_interface)) -> bool: return False

    def _set_subsystem_info(self, info: POINTER(retro_subsystem_info)) -> bool: return False

    def _set_controller_info(self, info: POINTER(retro_controller_info)) -> bool: return False

    def _set_memory_maps(self, maps: POINTER(retro_memory_map)) -> bool: return False

    def _set_geometry(self, geometry: POINTER(retro_game_geometry)) -> bool: return False

    def _get_username(self, username: POINTER(c_char_p)) -> bool: return False

    def _get_language(self, language: POINTER(retro_language)) -> bool: return False

    def _get_current_software_framebuffer(self, framebuffer: POINTER(retro_framebuffer)) -> bool: return False

    def _get_hw_render_interface(self, interface: POINTER(retro_hw_render_interface)) -> bool: return False

    def _set_support_achievements(self, support: POINTER(c_bool)) -> bool: return False

    def _set_hw_render_context_negotiation_interface(self, interface: POINTER(retro_hw_render_context_negotiation_interface)) -> bool: return False

    def _set_serialization_quirks(self, quirks: POINTER(c_uint64)) -> bool: return False

    def _set_hw_shared_context(self) -> bool: return False

    def _get_vfs_interface(self, vfs: POINTER(retro_vfs_interface_info)) -> bool: return False

    def _get_led_interface(self, led: POINTER(retro_led_interface)) -> bool: return False

    def _get_audio_video_enable(self, enable: POINTER(retro_av_enable_flags)) -> bool: return False

    def _get_midi_interface(self, midi: POINTER(retro_midi_interface)) -> bool: return False

    def _get_fastforwarding(self, is_fastforwarding: POINTER(c_bool)) -> bool: return False

    def _get_target_refresh_rate(self, rate: POINTER(c_float)) -> bool: return False

    def _get_input_bitmasks(self) -> bool: return False

    def _get_core_options_version(self, version: POINTER(c_uint)) -> bool: return False

    def _set_core_options(self, options: POINTER(retro_core_option_definition)) -> bool: return False

    def _set_core_options_intl(self, options: POINTER(retro_core_options_intl)) -> bool: return False

    def _set_core_options_display(self, options: POINTER(retro_core_option_display)) -> bool: return False

    def _get_preferred_hw_render(self, preferred: POINTER(retro_hw_context_type)) -> bool: return False

    def _get_disk_control_interface_version(self, version: POINTER(c_uint)) -> bool: return False

    def _set_disk_control_ext_interface(self, interface: POINTER(retro_disk_control_ext_callback)) -> bool: return False

    def _get_message_interface_version(self, version: POINTER(c_uint)) -> bool: return False

    def _set_message_ext(self, interface: POINTER(retro_message_ext)) -> bool: return False

    def _get_input_max_users(self, max_users: POINTER(c_uint)) -> bool: return False

    def _set_audio_buffer_status_callback(self, callback: POINTER(retro_audio_buffer_status_callback)) -> bool: return False

    def _set_minimum_audio_latency(self, latency: POINTER(c_uint)) -> bool: return False

    def _set_fastforwarding_override(self, override: POINTER(retro_fastforwarding_override)) -> bool: return False

    def _set_content_info_override(self, override: POINTER(retro_system_content_info_override)) -> bool: return False

    def _get_game_info_ext(self, info: POINTER(POINTER(retro_game_info_ext))) -> bool: return False

    def _set_core_options_v2(self, options: POINTER(retro_core_options_v2)) -> bool: return False

    def _set_core_options_v2_intl(self, options: POINTER(retro_core_options_v2_intl)) -> bool: return False

    def _set_core_options_update_display_callback(self, callback: POINTER(retro_core_options_update_display_callback)) -> bool: return False

    def _set_variable(self, variable: POINTER(retro_variable)) -> bool: return False

    def _get_throttle_state(self, state: POINTER(retro_throttle_state)) -> bool: return False

    def _get_savestate_context(self, context: POINTER(retro_savestate_context)) -> bool: return False

    def _get_hw_render_context_negotiation_interface_support(self, support: POINTER(retro_hw_render_context_negotiation_interface)) -> bool: return False

    def _get_jit_capable(self, capable: POINTER(c_bool)) -> bool: return False

    def _get_microphone_interface(self, interface: POINTER(retro_microphone_interface)) -> bool: return False

    def _get_device_power(self, power: POINTER(retro_device_power)) -> bool: return False

    def _set_netpacket_interface(self, interface: POINTER(retro_netpacket_callback)) -> bool: return False

    def _get_playlist_directory(self, dir: POINTER(c_char_p)) -> bool: return False


__all__ = [
    'EnvironmentDriver',
]
