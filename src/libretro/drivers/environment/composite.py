from collections.abc import Callable, Sequence
from copy import deepcopy
from ctypes import (
    POINTER,
    Array,
    byref,
    c_bool,
    c_char_p,
    c_float,
    c_int16,
    c_uint,
    c_uint64,
    c_void_p,
    memmove,
    pointer,
    sizeof,
    string_at,
)
from typing import AnyStr, Required, TypedDict

from _ctypes import CFuncPtr

from libretro._typing import override
from libretro.api import (
    AvEnableFlags,
    HardwareContext,
    InputDevice,
    LogLevel,
    MemoryAccess,
    PixelFormat,
    Port,
    Rotation,
    RumbleEffect,
    SavestateContext,
    Sensor,
    SensorAction,
    SerializationQuirks,
    ThrottleMode,
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
    retro_log_printf_t,
    retro_memory_map,
    retro_message,
    retro_message_ext,
    retro_microphone_interface,
    retro_midi_interface,
    retro_netpacket_callback,
    retro_perf_callback,
    retro_pixel_format,
    retro_proc_address_t,
    retro_rumble_interface,
    retro_savestate_context,
    retro_sensor_get_input_t,
    retro_sensor_interface,
    retro_set_rumble_state_t,
    retro_set_sensor_state_t,
    retro_subsystem_info,
    retro_system_av_info,
    retro_system_content_info_override,
    retro_throttle_state,
    retro_variable,
    retro_vfs_interface,
    retro_vfs_interface_info,
)
from libretro.api._utils import as_bytes, from_zero_terminated, memoryview_at
from libretro.drivers.audio import AudioDriver
from libretro.drivers.camera import CameraDriver
from libretro.drivers.content import ContentDriver
from libretro.drivers.input import InputDriver
from libretro.drivers.led import LedDriver
from libretro.drivers.location import LocationDriver
from libretro.drivers.log import LogDriver
from libretro.drivers.message import MessageInterface
from libretro.drivers.microphone import MicrophoneDriver
from libretro.drivers.midi import MidiDriver
from libretro.drivers.options import OptionDriver
from libretro.drivers.path import PathDriver
from libretro.drivers.perf import PerfDriver
from libretro.drivers.power import PowerDriver
from libretro.drivers.timing import TimingDriver
from libretro.drivers.user import UserDriver
from libretro.drivers.vfs import FileSystemInterface
from libretro.drivers.video import FrameBufferSpecial, VideoDriver

from .default import DefaultEnvironmentDriver

# TODO: Match envcalls even if the experimental flag is unset (but still consider it for ABI differences)


class CompositeEnvironmentDriver(DefaultEnvironmentDriver):
    class Args(TypedDict, total=False):
        audio: Required[AudioDriver]
        input: Required[InputDriver]
        video: Required[VideoDriver]
        content: ContentDriver | None
        overscan: bool | None
        message: MessageInterface | None
        options: OptionDriver | None
        path: PathDriver | None
        camera: CameraDriver | None
        log: LogDriver | None
        perf: PerfDriver | None
        location: LocationDriver | None
        user: UserDriver | None
        vfs: FileSystemInterface | None
        led: LedDriver | None
        av_enable: AvEnableFlags | None
        midi: MidiDriver | None
        timing: TimingDriver | None
        preferred_hw: HardwareContext | None
        driver_switch_enable: bool | None
        savestate_context: SavestateContext | None
        jit_capable: bool | None
        mic_interface: MicrophoneDriver | None
        device_power: PowerDriver | None

    @override
    def __init__(self, kwargs: Args):
        super().__init__()
        self._audio = kwargs["audio"]
        if not isinstance(self._audio, AudioDriver):
            raise TypeError(f"Expected AudioDriver, got {type(self._audio).__qualname__}")

        self._input = kwargs["input"]
        if not isinstance(self._input, InputDriver):
            raise TypeError(f"Expected InputDriver, got {type(self._input).__qualname__}")

        self._video = kwargs["video"]
        if not isinstance(self._video, VideoDriver):
            raise TypeError(f"Expected VideoDriver, got {type(self._video).__qualname__}")

        self._content = kwargs.get("content")
        if self._content is not None and not isinstance(self._content, ContentDriver):
            raise TypeError(
                f"Expected ContentDriver or None, got {type(self._content).__qualname__}"
            )

        self._overscan = kwargs.get("overscan")
        if self._overscan is not None and not isinstance(self._overscan, bool):
            raise TypeError(f"Expected bool or None, got {type(self._overscan).__qualname__}")

        self._message = kwargs.get("message")
        if self._message is not None and not isinstance(self._message, MessageInterface):
            raise TypeError(
                f"Expected MessageInterface or None, got {type(self._message).__qualname__}"
            )

        self.__shutdown = False
        self._performance_level: int | None = None
        self._path = kwargs.get("path")
        if self._path is not None and not isinstance(self._path, PathDriver):
            raise TypeError(f"Expected PathDriver or None, got {type(self._path).__qualname__}")

        self._options = kwargs.get("options")
        if self._options is not None and not isinstance(self._options, OptionDriver):
            raise TypeError(
                f"Expected OptionDriver or None, got {type(self._options).__qualname__}"
            )

        self._camera = kwargs.get("camera")
        if self._camera is not None and not isinstance(self._camera, CameraDriver):
            raise TypeError(
                f"Expected CameraDriver or None, got {type(self._camera).__qualname__}"
            )

        self._log = kwargs.get("log")
        if self._log is not None and not isinstance(self._log, LogDriver):
            raise TypeError(f"Expected LogDriver or None, got {type(self._log).__qualname__}")

        self._perf = kwargs.get("perf")
        if self._perf is not None and not isinstance(self._perf, PerfDriver):
            raise TypeError(f"Expected PerfDriver or None, got {type(self._perf).__qualname__}")

        self._location = kwargs.get("location")
        if self._location is not None and not isinstance(self._location, LocationDriver):
            raise TypeError(
                f"Expected LocationDriver or None, got {type(self._location).__qualname__}"
            )

        self._proc_address_callback: retro_get_proc_address_interface | None = None
        self._memory_maps: retro_memory_map | None = None
        self._user = kwargs.get("user")
        if self._user is not None and not isinstance(self._user, UserDriver):
            raise TypeError(f"Expected UserDriver or None, got {type(self._user).__qualname__}")

        self._supports_achievements: bool | None = None
        self._serialization_quirks: SerializationQuirks | None = None
        self._vfs = kwargs.get("vfs")
        if self._vfs is not None and not isinstance(self._vfs, FileSystemInterface):
            raise TypeError(
                f"Expected FileSystemInterface or None, got {type(self._vfs).__qualname__}"
            )

        self._led = kwargs.get("led")
        if self._led is not None and not isinstance(self._led, LedDriver):
            raise TypeError(f"Expected LedDriver or None, got {type(self._led).__qualname__}")

        self._av_enable = kwargs.get("av_enable")
        if self._av_enable is not None and not isinstance(self._av_enable, AvEnableFlags):
            raise TypeError(
                f"Expected AvEnableFlags or None, got {type(self._av_enable).__qualname__}"
            )

        self._midi = kwargs.get("midi")
        if self._midi is not None and not isinstance(self._midi, MidiDriver):
            raise TypeError(f"Expected MidiDriver or None, got {type(self._midi).__qualname__}")

        self._timing = kwargs.get("timing")
        if self._timing is not None and not isinstance(self._timing, TimingDriver):
            raise TypeError(
                f"Expected TimingDriver or None, got {type(self._timing).__qualname__}"
            )

        self._preferred_hw = kwargs.get("preferred_hw")
        if self._preferred_hw is not None and not isinstance(self._preferred_hw, HardwareContext):
            raise TypeError(
                f"Expected HardwareContext or None, got {type(self._preferred_hw).__qualname__}"
            )

        self._driver_switch_enable = kwargs.get("driver_switch_enable")
        if self._driver_switch_enable is not None and not isinstance(
            self._driver_switch_enable, bool
        ):
            raise TypeError(
                f"Expected bool or None, got {type(self._driver_switch_enable).__qualname__}"
            )

        self._savestate_context = kwargs.get("savestate_context")
        if self._savestate_context is not None and not isinstance(
            self._savestate_context, SavestateContext
        ):
            raise TypeError(
                f"Expected SavestateContext or None, got {type(self._savestate_context).__qualname__}"
            )

        self._jit_capable = kwargs.get("jit_capable")
        if self._jit_capable is not None and not isinstance(self._jit_capable, bool):
            raise TypeError(f"Expected bool or None, got {type(self._jit_capable).__qualname__}")

        self._mic_interface = kwargs.get("mic_interface")
        if self._mic_interface is not None and not isinstance(
            self._mic_interface, MicrophoneDriver
        ):
            raise TypeError(
                f"Expected MicrophoneDriver or None, got {type(self._mic_interface).__qualname__}"
            )

        self._device_power = kwargs.get("device_power")
        if self._device_power is not None and not isinstance(self._device_power, PowerDriver):
            raise TypeError(
                f"Expected PowerDriver or None, got {type(self._device_power).__qualname__}"
            )

        self._rumble: retro_rumble_interface | None = None
        self._sensor: retro_sensor_interface | None = None
        self._log_cb: retro_log_callback | None = None
        self._led_cb: retro_led_interface | None = None

    @property
    def audio(self) -> AudioDriver:
        return self._audio

    @property
    def input(self) -> InputDriver:
        return self._input

    @property
    def video(self) -> VideoDriver:
        return self._video

    @property
    def content(self) -> ContentDriver | None:
        return self._content

    @property
    def camera(self) -> CameraDriver | None:
        return self._camera

    @property
    def user(self) -> UserDriver | None:
        return self._user

    @property
    def path(self) -> PathDriver | None:
        return self._path

    @property
    def timing(self) -> TimingDriver | None:
        return self._timing

    @override
    def video_refresh(self, data: c_void_p, width: int, height: int, pitch: int) -> None:
        # Handle the constants and their equivalent ints, just to be safe
        match data:
            case FrameBufferSpecial.DUPE | 0 | None:
                self._video.refresh(FrameBufferSpecial.DUPE, width, height, pitch)
            case FrameBufferSpecial.HARDWARE | -1 | 18446744073709551615:
                self._video.refresh(FrameBufferSpecial.HARDWARE, width, height, pitch)
            case int() | c_void_p():
                view = memoryview_at(data, pitch * height, readonly=True)
                assert (
                    len(view) == pitch * height
                ), f"Expected view to have {pitch * height} bytes, got {len(view)} bytes"
                self._video.refresh(view, width, height, pitch)
            case _:
                raise TypeError(
                    f"Expected FrameBufferSpecial, int, or c_void_p, got {type(data).__name__}"
                )

    @override
    def audio_sample(self, left: int, right: int) -> None:
        self._audio.sample(left, right)

    @override
    def audio_sample_batch(self, data: POINTER(c_int16), frames: int) -> int:
        sample_view = memoryview_at(data, frames * 2 * sizeof(c_int16)).cast("h")
        assert (
            len(sample_view) == frames * 2
        ), f"Expected view to have {frames * 2} samples, got {len(sample_view)} samples"
        return self._audio.sample_batch(sample_view)

    @override
    def input_poll(self) -> None:
        self._input.poll()

    @override
    def input_state(self, port: int, device: int, index: int, id: int) -> int:
        return self._input.state(Port(port), InputDevice(device), index, id)

    @property
    def rotation(self) -> Rotation:
        return self._video.rotation

    @override
    def _set_rotation(self, rotation_ptr: POINTER(c_uint)) -> bool:
        if not rotation_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_ROTATION doesn't accept NULL")

        self._video.rotation = Rotation(rotation_ptr[0])
        return True

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
        return self.__shutdown

    @override
    def _shutdown(self) -> bool:
        self.__shutdown = True  # TODO: Add a shutdown driver?
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

    @override
    def _get_system_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._path is None or self._path.system_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._path.system_dir
        return True

    @property
    def pixel_format(self) -> PixelFormat:
        return self._video.pixel_format

    @override
    def _set_pixel_format(self, format_ptr: POINTER(retro_pixel_format)) -> bool:
        if not format_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_PIXEL_FORMAT doesn't accept NULL")

        self._video.pixel_format = PixelFormat(format_ptr[0])
        return True

    @property
    def input_descriptors(self) -> Sequence[retro_input_descriptor] | None:
        return self._input.descriptors

    @override
    def _set_input_descriptors(self, descriptors_ptr: POINTER(retro_input_descriptor)) -> bool:
        if not descriptors_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS doesn't accept NULL")

        self._input.descriptors = tuple(deepcopy(d) for d in from_zero_terminated(descriptors_ptr))
        return True

    @property
    def keyboard_callback(self) -> retro_keyboard_callback | None:
        return self._input.keyboard_callback

    @override
    def _set_keyboard_callback(self, callback_ptr: POINTER(retro_keyboard_callback)) -> bool:
        if not callback_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK doesn't accept NULL")

        self._input.keyboard_callback = deepcopy(callback_ptr[0])
        return True

    @override
    def _set_disk_control_interface(self, callback: POINTER(retro_disk_control_callback)) -> bool:
        return False  # TODO: Implement

    @override
    def _set_hw_render(self, hw_render_ptr: POINTER(retro_hw_render_callback)) -> bool:
        if not hw_render_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_HW_RENDER doesn't accept NULL")

        context = self._video.set_context(hw_render_ptr[0])
        if context is None:
            return False

        hw_render_ptr[0] = context
        # Give the core the callbacks that the video driver defines

        return True

    @property
    def options(self) -> OptionDriver | None:
        return self._options

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

        updated_ptr[0] = self._options.variable_updated
        return True

    @property
    def support_no_game(self) -> bool | None:
        if not self._content:
            return None

        return self._content.support_no_game

    @override
    def _set_support_no_game(self, support_ptr: POINTER(c_bool)) -> bool:
        if not self._content:
            return False

        if not support_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME doesn't accept NULL")

        self._content.support_no_game = support_ptr[0]
        return True

    @override
    def _get_libretro_path(self, path_ptr: POINTER(c_char_p)) -> bool:
        if not self._path or not self._path.libretro_path:
            return False

        if not path_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_LIBRETRO_PATH doesn't accept NULL")

        path_ptr[0] = self._path.libretro_path
        return True

    @override
    def _set_frame_time_callback(self, callback_ptr: POINTER(retro_frame_time_callback)) -> bool:
        if not self._timing:
            return False

        if not callback_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK doesn't accept NULL")

        self._timing.frame_time_callback = deepcopy(callback_ptr[0])
        return True

    @override
    def _set_audio_callback(self, callback_ptr: POINTER(retro_audio_callback)) -> bool:
        if callback_ptr:
            self._audio.callbacks = deepcopy(callback_ptr[0])

        return True

    @override
    def _get_rumble_interface(self, rumble_ptr: POINTER(retro_rumble_interface)) -> bool:
        if not rumble_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE doesn't accept NULL")

        if not self._input.rumble:
            return False

        if not self._rumble:
            self._rumble = retro_rumble_interface(self.__set_rumble_state)
            # So that even if the rumble/input drivers are swapped out,
            # the core still has valid function pointers tied to non-GC'd callable objects

        rumble_ptr[0] = self._rumble
        return True

    @retro_set_rumble_state_t
    def __set_rumble_state(self, port: int, effect: int, strength: int) -> bool:
        if not self._input.rumble:
            return False

        return self._input.rumble.set_rumble_state(port, RumbleEffect(effect), strength)

    @override
    def _get_input_device_capabilities(self, caps_ptr: POINTER(c_uint64)) -> bool:
        if not caps_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES doesn't accept NULL")

        caps = self._input.device_capabilities
        if caps is None:
            return False

        caps_ptr[0] = caps
        return True

    @override
    def _get_sensor_interface(self, sensor_ptr: POINTER(retro_sensor_interface)) -> bool:
        if not sensor_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE doesn't accept NULL")

        if not self._input.sensor:
            return False

        if not self._sensor:
            self._sensor = retro_sensor_interface(
                set_sensor_state=self.__set_sensor_state,
                get_sensor_input=self.__get_sensor_input,
            )
            # So that even if the sensor/input drivers are swapped out,
            # the core still has valid function pointers tied to non-GC'd callable objects

        sensor_ptr[0] = self._sensor
        return True

    @retro_set_sensor_state_t
    def __set_sensor_state(self, port: int, action: int, rate: int) -> bool:
        if not self._input.sensor:
            return False

        return self._input.sensor.set_sensor_state(port, SensorAction(action), rate)

    @retro_sensor_get_input_t
    def __get_sensor_input(self, port: int, id: int) -> float:
        if not self._input.sensor:
            return 0.0

        return self._input.sensor.get_sensor_input(port, Sensor(id))

    @override
    def _get_camera_interface(self, callback_ptr: POINTER(retro_camera_callback)) -> bool:
        if not self._camera:
            return False

        if not callback_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_CAMERA_INTERFACE doesn't accept NULL")

        callback: retro_camera_callback = callback_ptr[0]
        self._camera.width = callback.width
        self._camera.height = callback.height

        callback_ptr[0] = retro_camera_callback.from_param(self._camera)

        return True  # TODO: Implement

    @property
    def log(self) -> LogDriver | None:
        return self._log

    @override
    def _get_log_interface(self, log_ptr: POINTER(retro_log_callback)) -> bool:
        if not self._log:
            return False

        if not log_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_LOG_INTERFACE doesn't accept NULL")

        if not self._log_cb:
            self._log_cb = retro_log_callback(log=retro_log_printf_t(self.__log))

        log_ptr[0] = self._log_cb
        return True

    def __log(self, level: int, message: bytes):
        if self._log:
            self._log.log(LogLevel(level), message)

    @property
    def perf(self) -> PerfDriver | None:
        return self._perf

    def _get_perf_interface(self, perf_ptr: POINTER(retro_perf_callback)) -> bool:
        if not self._perf:
            return False

        if not perf_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_PERF_INTERFACE doesn't accept NULL")

        perf_ptr[0] = retro_perf_callback.from_param(self._perf)
        return True

    @property
    def location(self) -> LocationDriver | None:
        return self._location

    @override
    def _get_location_interface(self, location_ptr: POINTER(retro_location_callback)) -> bool:
        if not self._location:
            return False

        if not location_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE doesn't accept NULL")

        location: retro_location_callback = location_ptr[0]

        self._location.initialized = location.initialized
        self._location.deinitialized = location.deinitialized

        memmove(
            location_ptr,
            byref(retro_location_callback.from_param(self._location)),
            sizeof(retro_location_callback),
        )
        return True

    @override
    def _get_core_assets_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._path is None or self._path.core_assets_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._path.core_assets_dir
        return True

    @override
    def _get_save_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._path is None or self._path.save_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._path.save_dir
        return True

    @override
    def _set_system_av_info(self, info_ptr: POINTER(retro_system_av_info)) -> bool:
        if not info_ptr:
            return False

        # TODO: Provide a way to disable this envcall
        av_info: retro_system_av_info = info_ptr[0]
        self._video.system_av_info = av_info
        self._audio.system_av_info = av_info
        self._system_av_info = deepcopy(av_info)
        return True

    @property
    def proc_address_callback(self) -> retro_get_proc_address_interface | None:
        return self._proc_address_callback

    def get_proc_address(
        self, sym: AnyStr, funtype: type[CFuncPtr] | None
    ) -> retro_proc_address_t | Callable[[], None] | None:
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
    def _set_proc_address_callback(
        self, procaddress_ptr: POINTER(retro_get_proc_address_interface)
    ) -> bool:
        if not procaddress_ptr:
            self._proc_address_callback = None
        else:
            self._proc_address_callback = deepcopy(procaddress_ptr[0])

        return True

    @property
    def subsystems(self) -> Sequence[retro_subsystem_info] | None:
        if not self._content:
            return None

        return self._content.subsystem_info

    @override
    def _set_subsystem_info(self, info_ptr: POINTER(retro_subsystem_info)) -> bool:
        if not self._content:
            return False

        if not info_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO doesn't accept NULL")

        self._content.subsystem_info = tuple(deepcopy(s) for s in from_zero_terminated(info_ptr))
        return True

    @property
    def controller_info(self) -> Sequence[retro_controller_info] | None:
        return self._input.controller_info

    @override
    def _set_controller_info(self, info_ptr: POINTER(retro_controller_info)) -> bool:
        if not info_ptr:
            raise ValueError("RETRO_ENVIRONMENT_SET_CONTROLLER_INFO doesn't accept NULL")

        controller_infos = tuple(deepcopy(s) for s in from_zero_terminated(info_ptr))
        self._input.controller_info = controller_infos

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

        self._video.geometry = geometry_ptr[0]
        return True

    @override
    def _get_username(self, username_ptr: POINTER(c_char_p)) -> bool:
        if self._user is None or self._user.username is None:
            return False

        if not username_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_USERNAME doesn't accept NULL")

        username_ptr[0] = self._user.username
        return True

    @override
    def _get_language(self, language_ptr: POINTER(retro_language)) -> bool:
        if self._user is None or self._user.language is None:
            return False

        if not language_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_LANGUAGE doesn't accept NULL")

        language_ptr[0] = self._user.language
        return True

    @override
    def _get_current_software_framebuffer(
        self, framebuffer_ptr: POINTER(retro_framebuffer)
    ) -> bool:
        if not framebuffer_ptr:
            raise ValueError(
                "RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER doesn't accept NULL"
            )

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
        self, interface: POINTER(retro_hw_render_context_negotiation_interface)
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
    def led(self) -> LedDriver | None:
        return self._led

    def _get_led_interface(self, led_ptr: POINTER(retro_led_interface)) -> bool:
        if not self._led:
            return False

        if not led_ptr:
            # This envcall supports passing NULL to query for support
            return True

        if not self._led_cb:
            self._led_cb = retro_led_interface(self.__set_led_state)

        led_ptr[0] = self._led_cb
        return True

    def __set_led_state(self, led: int, state: int) -> None:
        if self._led:
            self._led.set_led_state(led, state)

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
    def midi(self) -> MidiDriver | None:
        return self._midi

    @override
    def _get_midi_interface(self, midi_ptr: POINTER(retro_midi_interface)) -> bool:
        if not self._midi:
            return False

        if midi_ptr:
            memmove(
                midi_ptr,
                byref(retro_midi_interface.from_param(self._midi)),
                sizeof(retro_midi_interface),
            )

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _get_fastforwarding(self, fastforwarding_ptr: POINTER(c_bool)) -> bool:
        if self._timing is None or self._timing.throttle_state is None:
            return False

        if not fastforwarding_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_FASTFORWARDING doesn't accept NULL")

        fastforwarding_ptr[0] = (
            ThrottleMode(self.timing.throttle_state.mode) == ThrottleMode.FAST_FORWARD
        )
        return True

    @override
    def _get_target_refresh_rate(self, rate_ptr: POINTER(c_float)) -> bool:
        if self._timing is None or self._timing.target_refresh_rate is None:
            return False

        if not rate_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE doesn't accept NULL")

        rate_ptr[0] = self._timing.target_refresh_rate
        return True

    @property
    def input_bitmasks(self) -> bool | None:
        return self._input.bitmasks_supported

    @override
    def _get_input_bitmasks(self) -> bool:
        return bool(self._input.bitmasks_supported)

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
            if self._options.version < 1:
                return False

            self._options.set_options(
                tuple(deepcopy(o) for o in from_zero_terminated(options_ptr))
            )
        else:
            self._options.set_options(None)

        # This envcall supports passing NULL to reset the options
        return True

    @override
    def _set_core_options_intl(self, options_ptr: POINTER(retro_core_options_intl)) -> bool:
        if not self._options:
            return False

        if options_ptr:
            if self._options.version < 1:
                return False

            self._options.set_options_intl(options_ptr[0])
        else:
            self._options.set_options_intl(None)

        # This envcall supports passing NULL to reset the options
        return True

    @override
    def _set_core_options_display(
        self, options_display_ptr: POINTER(retro_core_option_display)
    ) -> bool:
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
    def _set_disk_control_ext_interface(
        self, interface: POINTER(retro_disk_control_ext_callback)
    ) -> bool:
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
    def _get_input_max_users(self, max_users_ptr: POINTER(c_uint)) -> bool:
        if not max_users_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS doesn't accept NULL")

        max_users = self._input.max_users
        if max_users is None:
            return False

        max_users_ptr[0] = max_users
        return True

    @override
    def _set_audio_buffer_status_callback(
        self, callback_ptr: POINTER(retro_audio_buffer_status_callback)
    ) -> bool:
        if callback_ptr:
            self._audio.buffer_status = deepcopy(callback_ptr[0])
        else:
            self._audio.buffer_status = None

        return True

    @override
    def _set_minimum_audio_latency(self, latency_ptr: POINTER(c_uint)) -> bool:
        if latency_ptr:
            self._audio.minimum_latency = latency_ptr[0]

        return True

    @override
    def _set_fastforwarding_override(
        self, override_ptr: POINTER(retro_fastforwarding_override)
    ) -> bool:
        if not self._timing:
            return False

        if override_ptr:
            self._timing.fastforwarding_override = deepcopy(override_ptr[0])

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _set_content_info_override(
        self, overrides_ptr: POINTER(retro_system_content_info_override)
    ) -> bool:
        if not self._content:
            return False

        if not overrides_ptr:
            # This envcall supports passing NULL to query for support
            return True

        self._content.overrides = tuple(deepcopy(o) for o in from_zero_terminated(overrides_ptr))
        return True

    @override
    def _get_game_info_ext(self, info_ptr: POINTER(retro_game_info_ext)) -> bool:
        if not self._content:
            return False

        if not info_ptr:
            return False

        info_ext: Array[retro_game_info_ext] | None = self._content.game_info_ext
        if info_ext is None:
            return False

        info_ptr[0] = pointer(info_ext)
        return True

    @override
    def _set_core_options_v2(self, options_ptr: POINTER(retro_core_options_v2)) -> bool:
        if not self._options:
            return False

        if self._options.version < 2:
            return False

        if options_ptr:
            self._options.set_options_v2(options_ptr[0])
        else:
            self._options.set_options_v2(None)

        return self._options.supports_categories

    def _set_core_options_v2_intl(self, options_ptr: POINTER(retro_core_options_v2_intl)) -> bool:
        if not self._options:
            return False

        if self._options.version < 2:
            return False

        if options_ptr:
            self._options.set_options_v2_intl(options_ptr[0])
        else:
            self._options.set_options_v2_intl(None)

        return self._options.supports_categories

    def _set_core_options_update_display_callback(
        self, callback_ptr: POINTER(retro_core_options_update_display_callback)
    ) -> bool:
        if not self._options:
            return False

        if callback_ptr:
            self._options.update_display_callback = callback_ptr[0]

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

    @override
    def _get_throttle_state(self, throttle_ptr: POINTER(retro_throttle_state)) -> bool:
        if not self._timing or not self._timing.throttle_state:
            return False

        if not throttle_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_THROTTLE_STATE doesn't accept NULL")

        throttle_ptr[0] = deepcopy(self._timing.throttle_state)

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
        self, support: POINTER(retro_hw_render_context_negotiation_interface)
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
    def power(self) -> PowerDriver | None:
        return self._device_power

    @override
    def _get_device_power(self, power_ptr: POINTER(retro_device_power)) -> bool:
        if not self._device_power:
            return False

        if power_ptr:
            power_ptr[0] = self._device_power.device_power

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _set_netpacket_interface(self, interface: POINTER(retro_netpacket_callback)) -> bool:
        return False  # TODO: Implement

    @override
    def _get_playlist_directory(self, dir_ptr: POINTER(c_char_p)) -> bool:
        if self._path is None or self._path.playlist_dir is None:
            return False

        if not dir_ptr:
            raise ValueError("RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY doesn't accept NULL")

        dir_ptr[0] = self._path.playlist_dir
        return True


__all__ = ["CompositeEnvironmentDriver"]
