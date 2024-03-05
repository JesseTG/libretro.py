from ctypes import *
from typing import *

from ._libretro import retro_game_info
from .core import Core
from .callback.audio import AudioCallbacks, AudioState
from .callback.environment import EnvironmentCallback
from .callback.input import InputCallbacks, GeneratorInputState
from .callback.video import VideoCallbacks, SoftwareVideoState
from .defs import *


def _full_power() -> retro_device_power:
    return retro_device_power(PowerState.PluggedIn, RETRO_POWERSTATE_NO_ESTIMATE, 100)


class Session(EnvironmentCallback):
    def __init__(
            self,
            core: Core | str,
            audio: AudioCallbacks,
            input_state: InputCallbacks,
            video: VideoCallbacks,
            # TODO: Support for an env override function
            # TODO: Support for core options
            content: str | SpecialContent | None = None,
            system_dir: Directory | None = None,
            core_assets_dir: Directory | None = None,
            save_dir: Directory | None = None,
            username: str | None = "libretro.py",
            language: Language | None = Language.English,
            target_refresh_rate: float | None = 60.0,
            jit_capable: bool | None = True,
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

        self._is_shutdown: bool = False
        self._keyboard_callback: retro_keyboard_callback | None = None
        self._performance_level: int | None = None
        self._system_dir = system_dir
        self._support_no_game: bool | None = None
        self._frame_time_callback: retro_frame_time_callback | None = None
        self._core_assets_dir = core_assets_dir
        self._save_dir = save_dir
        self._proc_address_callback: retro_get_proc_address_interface | None = None
        self._subsystem_info: Sequence[retro_subsystem_info] | None = None
        self._memory_maps: retro_memory_map | None = None
        self._username = username
        self._language = language
        self._supports_achievements: bool | None = None
        self._serialization_quirks: SerializationQuirks | None = None
        self._target_refresh_rate = target_refresh_rate
        self._fastforwarding_override: retro_fastforwarding_override | None = None
        self._content_info_override: Sequence[retro_system_content_info_override] | None = None
        self._throttle_state: retro_throttle_state | None = None
        self._savestate_context: SavestateContext | None = SavestateContext.Normal
        self._jit_capable = jit_capable
        self._playlist_dir = playlist_dir

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
                if not self._environment.support_no_game:
                    raise RuntimeError("No content provided")

                loaded = self._core.load_game(retro_game_info())

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

    def environment(self, cmd: EnvironmentCall, data: c_void_p) -> bool:
        match cmd:
            case EnvironmentCall.SetRotation:
                # TODO: Implement
                pass
            case EnvironmentCall.GetOverscan:
                # TODO: Implement
                pass
            case EnvironmentCall.GetCanDupe:
                # TODO: Implement
                pass
            case EnvironmentCall.SetMessage:
                # TODO: Implement
                pass
            case EnvironmentCall.Shutdown:
                # TODO: Implement
                pass
            case EnvironmentCall.SetPerformanceLevel:
                # TODO: Implement
                pass
            case EnvironmentCall.GetSystemDirectory:
                # TODO: Implement
                pass
            case EnvironmentCall.SetPixelFormat:
                ptr = cast(data, POINTER(PixelFormat))
                if not ptr:
                    raise ValueError("RETRO_ENVIRONMENT_SET_PIXEL_FORMAT doesn't accept NULL")
                # TODO: Implement
                pass
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
                # TODO: Implement
                pass
            case EnvironmentCall.GetLibretroPath:
                # TODO: Implement
                pass
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
                # TODO: Implement
                pass
            case EnvironmentCall.GetSensorInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetCameraInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetLogInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetPerfInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetLocationInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.GetCoreAssetsDirectory:
                # TODO: Implement
                pass
            case EnvironmentCall.GetSaveDirectory:
                # TODO: Implement
                pass
            case EnvironmentCall.SetSystemAvInfo:
                # TODO: Implement
                pass
            case EnvironmentCall.SetProcAddressCallback:
                # TODO: Implement
                pass
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
                # TODO: Implement
                pass
            case EnvironmentCall.GetLanguage:
                # TODO: Implement
                pass
            case EnvironmentCall.GetCurrentSoftwareFramebuffer:
                # TODO: Implement
                pass
            case EnvironmentCall.GetHwRenderInterface:
                # TODO: Implement
                pass
            case EnvironmentCall.SetSupportAchievements:
                # TODO: Implement
                pass
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
                # TODO: Implement
                pass
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
                # TODO: Implement
                pass
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
                # TODO: Implement
                pass
            case _:
                return False
        # TODO: Define a way to override certain calls
        return False


def default_session(
        core: str,
        content: str | SpecialContent | None = None,
        audio: AudioCallbacks | None = None,
        input_state: InputCallbacks | None = None,
        video: VideoCallbacks | None = None,
        ) -> Session:
    """
    Returns a Session with default state objects.
    """

    return Session(
        core=core,
        audio=audio or AudioState(),
        input_state=input_state or GeneratorInputState(),
        video=video or SoftwareVideoState(),
        content=content
    )