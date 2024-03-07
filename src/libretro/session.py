import logging
from ctypes import *

from .retro import retro_game_info
from .callback.log import LogCallback, StandardLogger
from .core import Core
from .callback.audio import AudioCallbacks, AudioState, ArrayAudioState
from .callback.environment import EnvironmentCallback
from .callback.input import InputCallbacks, GeneratorInputState, InputState
from .callback.video import VideoCallbacks, SoftwareVideoState, VideoState
from .content import load_game, SpecialContent
from .defs import *


def _full_power() -> retro_device_power:
    return retro_device_power(PowerState.PluggedIn, RETRO_POWERSTATE_NO_ESTIMATE, 100)


def _to_bytes(value: str | bytes | None) -> bytes | None:
    if isinstance(value, str):
        return value.encode('utf-8')
    return value


class Session(EnvironmentCallback):
    def __init__(
            self,
            core: Core | str,
            audio: AudioState,
            input_state: InputState,
            video: VideoState,
            # TODO: Support for an env override function
            # TODO: Support for core options
            content: str | SpecialContent | None = None,
            overscan: bool = False,
            system_dir: Directory | None = None,
            log_callback: LogCallback | None = None,
            core_assets_dir: Directory | None = None,
            save_dir: Directory | None = None,
            username: str | None = "libretro.py",
            language: Language = Language.English,
            target_refresh_rate: float = 60.0,
            jit_capable: bool = True,
            device_power: DevicePower | None = _full_power,
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

        self._overscan = overscan
        self._is_shutdown: bool = False
        self._keyboard_callback: retro_keyboard_callback | None = None
        self._performance_level: int | None = None
        self._system_dir = _to_bytes(system_dir)
        self._support_no_game: bool | None = None
        self._libretro_path: bytes = _to_bytes(self._core.path)
        self._frame_time_callback: retro_frame_time_callback | None = None
        self._log_callback: LogCallback | None = log_callback
        self._core_assets_dir = _to_bytes(core_assets_dir)
        self._save_dir = _to_bytes(save_dir)
        self._proc_address_callback: retro_get_proc_address_interface | None = None
        self._subsystem_info: Sequence[retro_subsystem_info] | None = None
        self._memory_maps: retro_memory_map | None = None
        self._username = _to_bytes(username)
        self._language = language
        self._supports_achievements: bool | None = None
        self._serialization_quirks: SerializationQuirks | None = None
        self._target_refresh_rate = target_refresh_rate
        self._fastforwarding_override: retro_fastforwarding_override | None = None
        self._content_info_override: Sequence[retro_system_content_info_override] | None = None
        self._throttle_state: retro_throttle_state | None = None
        self._savestate_context: SavestateContext | None = SavestateContext.Normal
        self._jit_capable = jit_capable
        self._device_power = device_power
        self._playlist_dir = _to_bytes(playlist_dir)

    def __enter__(self):
        self._core.set_video_refresh(self._video.refresh)
        self._core.set_audio_sample(self._audio.audio_sample)
        self._core.set_audio_sample_batch(self._audio.audio_sample_batch)
        self._core.set_input_poll(self._input.poll)
        self._core.set_input_state(self._input.state)
        self._core.set_environment(self.environment)

        self._core.init()
        loaded: bool = False
        match self._content:
            case str(content):
                loaded = self._core.load_game(content)
            case SpecialContent(content_type, content):
                loaded = self._core.load_game_special(content_type, content)
            case None:
                if not self._support_no_game:
                    raise RuntimeError("No content provided and core did not indicate support for no game.")

                loaded = self._core.load_game(None)

        if not loaded:
            raise RuntimeError("Failed to load game")

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
    def audio(self) -> AudioCallbacks:
        return self._audio

    @property
    def input(self) -> InputCallbacks:
        return self._input

    @property
    def video(self) -> VideoCallbacks:
        return self._video

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

    @property
    def subsystems(self) -> Sequence[retro_subsystem_info] | None:
        return self._subsystem_info

    @property
    def support_achievements(self) -> bool | None:
        return self._supports_achievements

    def environment(self, cmd: EnvironmentCall, data: c_void_p) -> bool:
        # TODO: Allow overriding certain calls by passing a function to the constructor
        match cmd:
            case EnvironmentCall.SetRotation:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_ROTATION doesn't accept NULL")

                rotation_ptr = cast(data, POINTER(c_uint))
                return self._video.set_rotation(rotation_ptr.contents)

            case EnvironmentCall.GetOverscan:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_OVERSCAN doesn't accept NULL")

                overscan_ptr = cast(data, POINTER(c_bool))
                overscan_ptr.contents = self._overscan
                return True

            case EnvironmentCall.GetCanDupe:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CAN_DUPE doesn't accept NULL")

                dupe_ptr = cast(data, POINTER(c_bool))
                dupe_ptr.contents = self._video.can_dupe()
                return True

            case EnvironmentCall.SetMessage:
                # TODO: Implement
                pass
            case EnvironmentCall.Shutdown:
                # TODO: Implement
                pass

            case EnvironmentCall.SetPerformanceLevel:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL doesn't accept NULL")

                perflevel_ptr = cast(data, POINTER(c_uint))
                self._performance_level = perflevel_ptr.contents.value
                return True

            case EnvironmentCall.GetSystemDirectory:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY doesn't accept NULL")

                sysdir_ptr = cast(data, POINTER(c_char_p))
                sysdir_ptr.contents.value = self._system_dir
                return True

            case EnvironmentCall.SetPixelFormat:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_PIXEL_FORMAT doesn't accept NULL")

                pixfmt_ptr = cast(data, POINTER(enum_retro_pixel_format))
                return self._video.set_pixel_format(pixfmt_ptr.contents)

            case EnvironmentCall.SetInputDescriptors:
                # TODO: Implement
                pass
            case EnvironmentCall.SetKeyboardCallback:
                # TODO: Implement
                pass
            case EnvironmentCall.SetDiskControlInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetVariable:
                # TODO: Implement
                pass
            case EnvironmentCall.SetVariables:
                # TODO: Implement
                pass
            case EnvironmentCall.GetVariableUpdate:
                # TODO: Implement
                pass

            case EnvironmentCall.SetSupportNoGame:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME doesn't accept NULL")

                support_no_game_ptr = cast(data, POINTER(c_bool))
                self._support_no_game = support_no_game_ptr.contents.value
                return True

            case EnvironmentCall.GetLibretroPath:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LIBRETRO_PATH doesn't accept NULL")

                libretro_path_ptr = cast(data, POINTER(c_char_p))
                libretro_path_ptr.contents.value = self._libretro_path
                return True

            case EnvironmentCall.SetFrameTimeCallback:
                # TODO: Implement
                pass
            case EnvironmentCall.SetAudioCallback:
                # TODO: Implement
                pass
            case EnvironmentCall.GetRumbleInterface:
                # TODO: Implement
                pass

            case EnvironmentCall.GetInputDeviceCapabilities:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES doesn't accept NULL")

                inputcaps_ptr = cast(data, POINTER(c_uint64))
                inputcaps_ptr.contents = self._input.device_capabilities
                return True

            case EnvironmentCall.GetSensorInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetCameraInterface:
                # TODO: Implement
                pass

            case EnvironmentCall.GetLogInterface:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LOG_INTERFACE doesn't accept NULL")

                log_ptr = cast(data, POINTER(retro_log_callback))
                log_ptr.contents = self._log_callback._as_parameter_
                # TODO: Is there a cleaner way to do this than using _as_parameter_?
                return True

            case EnvironmentCall.GetPerfInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetLocationInterface:
                # TODO: Implement
                pass

            case EnvironmentCall.GetCoreAssetsDirectory:
                if self._core_assets_dir is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY doesn't accept NULL")

                core_assets_dir_ptr = cast(data, POINTER(c_char_p))
                core_assets_dir_ptr.contents.value = self._core_assets_dir
                return True

            case EnvironmentCall.GetSaveDirectory:
                if self._save_dir is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY doesn't accept NULL")

                save_dir_ptr = cast(data, POINTER(c_char_p))
                save_dir_ptr.contents.value = self._save_dir
                return True

            case EnvironmentCall.SetSystemAvInfo:
                # TODO: Implement
                pass

            case EnvironmentCall.SetProcAddressCallback:
                if not data:
                    self._proc_address_callback = None
                else:
                    procaddress_ptr = cast(data, POINTER(retro_get_proc_address_interface))
                    interface: retro_get_proc_address_interface = procaddress_ptr.contents
                    self._proc_address_callback = retro_get_proc_address_interface(interface.get_proc_address)

                return True

            case EnvironmentCall.SetSubsystemInfo:
                # TODO: Implement
                pass
            case EnvironmentCall.SetControllerInfo:
                # TODO: Implement
                pass
            case EnvironmentCall.SetMemoryMaps:
                # TODO: Implement
                pass
            case EnvironmentCall.SetGeometry:
                # TODO: Implement
                pass

            case EnvironmentCall.GetUsername:
                if self._username is None:
                    return False
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_USERNAME doesn't accept NULL")

                username_ptr = cast(data, POINTER(c_char_p))
                username_ptr.contents.value = self._username
                return True

            case EnvironmentCall.GetLanguage:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_LANGUAGE doesn't accept NULL")

                language_ptr = cast(data, POINTER(enum_retro_language))
                language_ptr.contents = self._language
                return True

            case EnvironmentCall.GetCurrentSoftwareFramebuffer:
                # TODO: Implement
                pass
            case EnvironmentCall.GetHwRenderInterface:
                # TODO: Implement
                pass

            case EnvironmentCall.SetSupportAchievements:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS doesn't accept NULL")

                supports_achievements_ptr = cast(data, POINTER(c_bool))
                self._supports_achievements = supports_achievements_ptr.contents.value
                return True

            case EnvironmentCall.SetHwRenderContextNegotiationInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.SetSerializationQuirks:
                # TODO: Implement
                pass
            case EnvironmentCall.SetHwSharedContext:
                # TODO: Implement
                pass
            case EnvironmentCall.GetVfsInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetLedInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetAudioVideoEnable:
                # TODO: Implement
                pass
            case EnvironmentCall.GetMidiInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetFastForwarding:
                # TODO: Implement
                pass

            case EnvironmentCall.GetTargetRefreshRate:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE doesn't accept NULL")

                refresh_rate_ptr = cast(data, POINTER(c_float))
                refresh_rate_ptr.contents = self._target_refresh_rate
                return True

            case EnvironmentCall.GetCoreOptionsVersion:
                # TODO: Implement
                pass
            case EnvironmentCall.SetCoreOptions:
                # TODO: Implement
                pass
            case EnvironmentCall.SetCoreOptionsIntl:
                # TODO: Implement
                pass
            case EnvironmentCall.SetCoreOptionsDisplay:
                # TODO: Implement
                pass
            case EnvironmentCall.GetPreferredHwRender:
                # TODO: Implement
                pass
            case EnvironmentCall.GetDiskControlInterfaceVersion:
                # TODO: Implement
                pass
            case EnvironmentCall.SetDiskControlExtInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetMessageInterfaceVersion:
                # TODO: Implement
                pass
            case EnvironmentCall.SetMessageExt:
                # TODO: Implement
                pass
            case EnvironmentCall.SetAudioBufferStatusCallback:
                # TODO: Implement
                pass
            case EnvironmentCall.SetMinimumAudioLatency:
                # TODO: Implement
                pass
            case EnvironmentCall.SetFastForwardingOverride:
                # TODO: Implement
                pass
            case EnvironmentCall.SetContentInfoOverride:
                # TODO: Implement
                pass
            case EnvironmentCall.GetGameInfoExt:
                # TODO: Implement
                pass
            case EnvironmentCall.SetCoreOptionsV2:
                # TODO: Implement
                pass
            case EnvironmentCall.SetCoreOptionsV2Intl:
                # TODO: Implement
                pass
            case EnvironmentCall.SetCoreOptionsUpdateDisplayCallback:
                # TODO: Implement
                pass
            case EnvironmentCall.SetVariable:
                # TODO: Implement
                pass
            case EnvironmentCall.GetThrottleState:
                # TODO: Implement
                pass
            case EnvironmentCall.GetSaveStateContext:
                # TODO: Implement
                pass
            case EnvironmentCall.GetHwRenderContextNegotiationInterfaceSupport:
                # TODO: Implement
                pass

            case EnvironmentCall.GetJitCapable:
                if not data:
                    raise ValueError("RETRO_ENVIRONMENT_GET_JIT_CAPABLE doesn't accept NULL")

                jit_capable_ptr = cast(data, POINTER(c_bool))
                jit_capable_ptr.contents = self._jit_capable
                return True

            case EnvironmentCall.GetMicrophoneInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetDevicePower:
                # TODO: Implement
                pass
            case EnvironmentCall.SetNetpacketInterface:
                # TODO: Implement
                pass

            case EnvironmentCall.GetPlaylistDirectory:
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
        content: str | SpecialContent | None = None,
        audio: AudioCallbacks | None = None,
        input_state: InputCallbacks | None = None,
        video: VideoCallbacks | None = None,
        overscan: bool = False,
        system_dir: Directory | None = None,
        log_callback: LogCallback | None = None,
        save_dir: Directory | None = None,
        ) -> Session:
    """
    Returns a Session with default state objects.
    """

    return Session(
        core=core,
        audio=audio or ArrayAudioState(),
        input_state=input_state or GeneratorInputState(),
        video=video or SoftwareVideoState(),
        content=content,
        overscan=overscan,
        system_dir=system_dir,
        log_callback=log_callback or StandardLogger(logging.getLogger('libretro')),
        save_dir=save_dir
    )
