from abc import abstractmethod
from typing import *

from .._libretro import *
from ..defs import Rotation, PixelFormat, EnvironmentCall


class EnvironmentCallback(Protocol):
    @abstractmethod
    def environment(self, cmd: EnvironmentCall, data: c_void_p) -> bool: ...

def environment_callback(env: EnvironmentCallback) -> retro_environment_t:
    def callback(cmd: int, data: c_void_p) -> bool:
        match cmd:
            case EnvironmentCall.SetRotation:
                ptr = cast(data, POINTER(c_uint))
                value: Rotation | None = Rotation(ptr.contents) if ptr else None
                return env.set_rotation(value)

            case EnvironmentCall.GetOverscan:
                ptr = cast(data, POINTER(c_bool))
                value: c_bool | None = ptr.contents if ptr else None
                return env.get_overscan(value)

            case EnvironmentCall.GetCanDupe:
                ptr = cast(data, POINTER(c_bool))
                value: c_bool | None = ptr.contents if ptr else None
                return env.get_can_dupe(value)

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
                ptr = cast(data, POINTER(c_char_p))
                value: c_char_p | None = ptr.contents if ptr else None
                return env.get_system_directory(value)

            case EnvironmentCall.SetPixelFormat:
                ptr = cast(data, POINTER(c_uint))
                value: PixelFormat | None = PixelFormat(ptr.contents) if ptr else None
                return env.set_pixel_format(value)

            case EnvironmentCall.SetInputDescriptors:
                ptr = cast(data, POINTER(retro_input_descriptor))
                if ptr:
                    descriptors = []
                    i = 0
                    d = ptr[0]
                    while ptr[i].description:
                        descriptors.append(ptr[i])
                        i += 1
                    return env.set_input_descriptors(descriptors)
                else:
                    return env.set_input_descriptors(None)

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
                ptr = cast(data, POINTER(c_char_p))
                value: c_char_p | None = ptr.contents if ptr else None
                return env.get_libretro_path(value)

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
                ptr = cast(data, POINTER(retro_log_callback))
                return env.get_log_interface(ptr.contents if ptr else None)

            case EnvironmentCall.GetPerfInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetLocationInterface:
                # TODO: Implement
                return False

            case EnvironmentCall.GetCoreAssetsDirectory:
                ptr = cast(data, POINTER(c_char_p))
                value: c_char_p | None = ptr.contents if ptr else None
                return env.get_core_assets_directory(value)

            case EnvironmentCall.GetSaveDirectory:
                ptr = cast(data, POINTER(c_char_p))
                value: c_char_p | None = ptr.contents if ptr else None
                return env.get_save_directory(value)

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
                ptr = cast(data, POINTER(c_char_p))
                value: c_char_p | None = ptr.contents if ptr else None
                return env.get_username(value)

            case EnvironmentCall.GetLanguage:
                ptr = cast(data, POINTER(c_uint))
                value: c_uint | None = ptr.contents if ptr else None
                return env.get_language(value)

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
                ptr = cast(data, POINTER(c_uint))
                value: c_uint | None = ptr.contents if ptr else None
                return env.get_input_max_users(value)

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
                ptr = cast(data, POINTER(retro_throttle_state))
                value: retro_throttle_state | None = ptr.contents if ptr else None
                return env.get_throttle_state(value)

            case EnvironmentCall.GetSaveStateContext:
                ptr = cast(data, POINTER(enum_retro_savestate_context))
                value: enum_retro_savestate_context | None = ptr.contents if ptr else None
                return env.get_savestate_context(value)

            case EnvironmentCall.GetHwRenderContextNegotiationInterfaceSupport:
                # TODO: Implement
                return False

            case EnvironmentCall.GetJitCapable:
                ptr = cast(data, POINTER(c_bool))
                value: c_bool | None = ptr.contents if ptr else None
                return env.get_jit_capable(value)

            case EnvironmentCall.GetMicrophoneInterface:
                ptr = cast(data, POINTER(retro_microphone_interface))
                value: retro_microphone_interface | None = ptr.contents if ptr else None
                return env.get_microphone_interface(retro_microphone_interface)

            case EnvironmentCall.GetDevicePower:
                ptr = cast(data, POINTER(retro_device_power))
                value: retro_device_power | None = ptr.contents if ptr else None
                return env.get_device_power(value)

            case EnvironmentCall.SetNetpacketInterface:
                ptr = cast(data, POINTER(retro_netpacket_callback))
                value: retro_netpacket_callback | None = ptr.contents if ptr else None
                return env.set_netpacket_interface(value)

            case EnvironmentCall.GetPlaylistDirectory:
                ptr = cast(data, POINTER(c_char_p))
                value: c_char_p | None = ptr.contents if ptr else None
                return env.get_playlist_directory(value)

            case _:
                return False

    return callback
