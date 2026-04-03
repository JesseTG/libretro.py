from collections.abc import Sequence
from copy import deepcopy
from ctypes import (
    c_bool,
    c_char_p,
    c_double,
    c_float,
    c_int16,
    c_int32,
    c_uint,
    c_uint8,
    c_uint64,
    c_void_p,
    cast,
    memmove,
    pointer,
    sizeof,
)
from typing import TYPE_CHECKING, Literal, Required, TypedDict, overload

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
)
from libretro.api import Sensor as SensorAxis
from libretro.api import (
    SensorAction,
    SerializationQuirks,
    ThrottleMode,
    VfsFileAccess,
    VfsFileAccessHint,
    VfsSeekPosition,
    retro_audio_buffer_status_callback,
    retro_audio_callback,
    retro_av_enable_flags,
    retro_camera_callback,
    retro_controller_description,
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
    retro_hw_get_current_framebuffer_t,
    retro_hw_get_proc_address_t,
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
    retro_perf_counter,
    retro_pixel_format,
    retro_proc_address_t,
    retro_rumble_interface,
    retro_savestate_context,
    retro_sensor_get_input_t,
    retro_sensor_interface,
    retro_set_led_state_t,
    retro_set_rumble_state_t,
    retro_set_sensor_state_t,
    retro_subsystem_info,
    retro_system_av_info,
    retro_system_content_info_override,
    retro_throttle_state,
    retro_variable,
    retro_vfs_dir_handle,
    retro_vfs_get_path_t,
    retro_vfs_interface,
    retro_vfs_interface_info,
    retro_vfs_open_t,
)
from libretro.api._utils import (
    as_bytes,
    deepcopy_array,
    from_zero_terminated,
    is_zeroed,
    memoryview_at,
)
from libretro.api.location import *
from libretro.api.microphone import *
from libretro.api.midi import *
from libretro.api.vfs import *
from libretro.api.vfs import retro_vfs_close_t, retro_vfs_file_handle
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
from libretro.drivers.rumble import RumbleDriver
from libretro.drivers.sensor import SensorDriver
from libretro.drivers.timing import TimingDriver
from libretro.drivers.user import UserDriver
from libretro.drivers.vfs import FileSystemInterface
from libretro.drivers.video import FrameBufferSpecial, VideoDriver
from libretro.typing import TypedPointer, c_void_ptr

from .default import DefaultEnvironmentDriver

# TODO: Match envcalls even if the experimental flag is unset (but still consider it for ABI differences)
if TYPE_CHECKING:
    from ctypes import _CFunctionType  # type: ignore


class CompositeEnvironmentDriver[
    Audio: AudioDriver,
    Input: InputDriver,
    Video: VideoDriver,
    Content: ContentDriver | None,
    Message: MessageInterface | None,
    Option: OptionDriver | None,
    Path: PathDriver | None,
    Rumble: RumbleDriver | None,
    Sensor: SensorDriver | None,
    Camera: CameraDriver | None,
    Log: LogDriver | None,
    Perf: PerfDriver | None,
    Location: LocationDriver | None,
    User: UserDriver | None,
    Vfs: FileSystemInterface | None,
    Led: LedDriver | None,
    Midi: MidiDriver | None,
    Timing: TimingDriver | None,
    Mic: MicrophoneDriver | None,
    Power: PowerDriver | None,
](DefaultEnvironmentDriver):
    class Args(TypedDict, total=False):
        audio: Required[AudioDriver]
        input: Required[InputDriver]
        video: Required[VideoDriver]
        content: ContentDriver | None
        overscan: bool | None
        message: MessageInterface | None
        options: OptionDriver | None
        path: PathDriver | None
        rumble: RumbleDriver | None
        sensor: SensorDriver | None
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
    def __init__(
        self,
        /,
        audio: Audio,
        input: Input,
        video: Video,
        content: Content = None,
        overscan: bool | None = None,
        message: Message = None,
        options: Option = None,
        path: Path = None,
        rumble: Rumble = None,
        sensor: Sensor = None,
        camera: Camera = None,
        log: Log = None,
        perf: Perf = None,
        location: Location = None,
        user: User = None,
        vfs: Vfs = None,
        led: Led = None,
        av_enable: AvEnableFlags | None = None,
        midi: Midi = None,
        timing: Timing = None,
        preferred_hw: HardwareContext | None = None,
        driver_switch_enable: bool | None = None,
        savestate_context: SavestateContext | None = None,
        jit_capable: bool | None = None,
        mic: Mic = None,
        device_power: Power = None,
    ):
        super().__init__()
        self._audio = audio
        if not isinstance(self._audio, AudioDriver):
            raise TypeError(f"Expected AudioDriver, got {type(self._audio).__qualname__}")

        self._input = input
        if not isinstance(self._input, InputDriver):
            raise TypeError(f"Expected InputDriver, got {type(self._input).__qualname__}")

        self._video = video
        if not isinstance(self._video, VideoDriver):
            raise TypeError(f"Expected VideoDriver, got {type(self._video).__qualname__}")

        self._content = content
        if self._content is not None and not isinstance(self._content, ContentDriver):
            raise TypeError(
                f"Expected ContentDriver or None, got {type(self._content).__qualname__}"
            )

        self._overscan = overscan
        if self._overscan is not None and not isinstance(self._overscan, bool):
            raise TypeError(f"Expected bool or None, got {type(self._overscan).__qualname__}")

        self._message = message
        if self._message is not None and not isinstance(self._message, MessageInterface):
            raise TypeError(
                f"Expected MessageInterface or None, got {type(self._message).__qualname__}"
            )

        self.__shutdown = False
        self._performance_level: int | None = None
        self._path = path
        if self._path is not None and not isinstance(self._path, PathDriver):
            raise TypeError(f"Expected PathDriver or None, got {type(self._path).__qualname__}")

        self._options = options
        if self._options is not None and not isinstance(self._options, OptionDriver):
            raise TypeError(
                f"Expected OptionDriver or None, got {type(self._options).__qualname__}"
            )

        self._rumble = rumble
        if self._rumble is not None and not isinstance(self._rumble, RumbleDriver):
            raise TypeError(
                f"Expected RumbleDriver or None, got {type(self._rumble).__qualname__}"
            )

        self._sensor = sensor
        if self._sensor is not None and not isinstance(self._sensor, SensorDriver):
            raise TypeError(
                f"Expected SensorDriver or None, got {type(self._sensor).__qualname__}"
            )

        self._camera = camera
        if self._camera is not None and not isinstance(self._camera, CameraDriver):
            raise TypeError(
                f"Expected CameraDriver or None, got {type(self._camera).__qualname__}"
            )

        self._log_driver = log
        if self._log_driver is not None and not isinstance(self._log_driver, LogDriver):
            raise TypeError(
                f"Expected LogDriver or None, got {type(self._log_driver).__qualname__}"
            )

        self._perf = perf
        if self._perf is not None and not isinstance(self._perf, PerfDriver):
            raise TypeError(f"Expected PerfDriver or None, got {type(self._perf).__qualname__}")

        self._location = location
        if self._location is not None and not isinstance(self._location, LocationDriver):
            raise TypeError(
                f"Expected LocationDriver or None, got {type(self._location).__qualname__}"
            )

        self._proc_address_callback: retro_get_proc_address_interface | None = None
        self._memory_maps: retro_memory_map | None = None
        self._user = user
        if self._user is not None and not isinstance(self._user, UserDriver):
            raise TypeError(f"Expected UserDriver or None, got {type(self._user).__qualname__}")

        self._supports_achievements: bool | None = None
        self._serialization_quirks: SerializationQuirks | None = None
        self._vfs = vfs
        if self._vfs is not None and not isinstance(self._vfs, FileSystemInterface):
            raise TypeError(
                f"Expected FileSystemInterface or None, got {type(self._vfs).__qualname__}"
            )

        self._led = led
        if self._led is not None and not isinstance(self._led, LedDriver):
            raise TypeError(f"Expected LedDriver or None, got {type(self._led).__qualname__}")

        self._av_enable = av_enable
        if self._av_enable is not None and not isinstance(self._av_enable, AvEnableFlags):
            raise TypeError(
                f"Expected AvEnableFlags or None, got {type(self._av_enable).__qualname__}"
            )

        self._midi = midi
        if self._midi is not None and not isinstance(self._midi, MidiDriver):
            raise TypeError(f"Expected MidiDriver or None, got {type(self._midi).__qualname__}")

        self._timing = timing
        if self._timing is not None and not isinstance(self._timing, TimingDriver):
            raise TypeError(
                f"Expected TimingDriver or None, got {type(self._timing).__qualname__}"
            )

        self._preferred_hw = preferred_hw
        if self._preferred_hw is not None and not isinstance(self._preferred_hw, HardwareContext):
            raise TypeError(
                f"Expected HardwareContext or None, got {type(self._preferred_hw).__qualname__}"
            )

        self._driver_switch_enable = driver_switch_enable
        if self._driver_switch_enable is not None and not isinstance(
            self._driver_switch_enable, bool
        ):
            raise TypeError(
                f"Expected bool or None, got {type(self._driver_switch_enable).__qualname__}"
            )

        self._savestate_context = savestate_context
        if self._savestate_context is not None and not isinstance(
            self._savestate_context, SavestateContext
        ):
            raise TypeError(
                f"Expected SavestateContext or None, got {type(self._savestate_context).__qualname__}"
            )

        self._jit_capable = jit_capable
        if self._jit_capable is not None and not isinstance(self._jit_capable, bool):
            raise TypeError(f"Expected bool or None, got {type(self._jit_capable).__qualname__}")

        self._mic = mic
        if self._mic is not None and not isinstance(self._mic, MicrophoneDriver):
            raise TypeError(
                f"Expected MicrophoneDriver or None, got {type(self._mic).__qualname__}"
            )

        self._device_power = device_power
        if self._device_power is not None and not isinstance(self._device_power, PowerDriver):
            raise TypeError(
                f"Expected PowerDriver or None, got {type(self._device_power).__qualname__}"
            )

        self._hw_render_callback: retro_hw_render_callback | None = None
        self._rumble_interface: retro_rumble_interface | None = None
        self._camera_callback: retro_camera_callback | None = None
        self._sensor_interface: retro_sensor_interface | None = None
        self._log_callback: retro_log_callback | None = None
        self._perf_callback: retro_perf_callback | None = None
        self._location_callback: retro_location_callback | None = None
        self._vfs_interface: retro_vfs_interface | None = None
        self._led_interface: retro_led_interface | None = None
        self._midi_interface: retro_midi_interface | None = None
        self._mic_interface: retro_microphone_interface | None = None

    @property
    def audio(self) -> Audio:
        return self._audio

    @property
    def input(self) -> Input:
        return self._input

    @property
    def video(self) -> Video:
        return self._video

    @property
    def content(self) -> Content:
        return self._content

    @property
    def sensor(self) -> Sensor:
        return self._sensor

    @property
    def camera(self) -> Camera:
        return self._camera

    @property
    def user(self) -> User:
        return self._user

    @property
    def path(self) -> Path:
        return self._path

    @property
    def timing(self) -> Timing:
        return self._timing

    @property
    def rumble(self) -> Rumble:
        return self._rumble

    @override
    def video_refresh(self, data: c_void_ptr, width: int, height: int, pitch: int) -> None:
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
    def audio_sample_batch(self, data: TypedPointer[c_int16], frames: int) -> int:
        sample_view = memoryview_at(data, frames * 2 * sizeof(c_int16)).cast("h")
        assert (
            len(sample_view) == frames * 2
        ), f"Expected view to have {frames * 2} samples, got {len(sample_view)} samples"
        return self._audio.sample_batch(sample_view)

    @override
    def input_poll(self) -> None:
        # TODO: Ensure this isn't called more than once per frame
        self._input.poll()

        if self._sensor is not None:
            self._sensor.poll()

    @override
    def input_state(self, port: Port, device: int, index: int, id: int) -> int:
        return self._input.state(port, InputDevice(device), index, id)

    @property
    def rotation(self) -> Rotation:
        return self._video.rotation

    @override
    def _set_rotation(self, rotation: TypedPointer[c_uint]) -> bool:
        if not rotation:
            raise ValueError("RETRO_ENVIRONMENT_SET_ROTATION doesn't accept NULL")

        self._video.rotation = Rotation(rotation[0])
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
    def _get_overscan(self, overscan: TypedPointer[c_bool]) -> bool:
        if self.overscan is None:
            return False

        if not overscan:
            raise ValueError("RETRO_ENVIRONMENT_GET_OVERSCAN doesn't accept NULL")

        overscan[0] = self.overscan
        return True

    @property
    def can_dupe(self) -> bool | None:
        return self._video.can_dupe

    @override
    def _get_can_dupe(self, can_dupe: TypedPointer[c_bool]) -> bool:
        if not can_dupe:
            raise ValueError("RETRO_ENVIRONMENT_GET_CAN_DUPE doesn't accept NULL")

        if self._video.can_dupe is None:
            return False

        can_dupe[0] = self._video.can_dupe
        return True

    @property
    def message(self) -> Message:
        return self._message

    @override
    def _set_message(self, message: TypedPointer[retro_message]) -> bool:
        if self._message is None:
            return False

        if not message:
            raise ValueError("RETRO_ENVIRONMENT_SET_MESSAGE doesn't accept NULL")

        return self._message.set_message(message[0])

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
    def _set_performance_level(self, level: TypedPointer[c_uint]) -> bool:
        if not level:
            raise ValueError("RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL doesn't accept NULL")

        self._performance_level = level[0]
        return True

    @override
    def _get_system_directory(self, dir: TypedPointer[c_char_p]) -> bool:
        if self._path is None or self._path.system_dir is None:
            return False

        if not dir:
            raise ValueError("RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY doesn't accept NULL")

        dir[0] = self._path.system_dir
        return True

    @property
    def pixel_format(self) -> PixelFormat:
        return self._video.pixel_format

    @override
    def _set_pixel_format(self, fmt: TypedPointer[retro_pixel_format]) -> bool:
        if not fmt:
            raise ValueError("RETRO_ENVIRONMENT_SET_PIXEL_FORMAT doesn't accept NULL")

        self._video.pixel_format = PixelFormat(fmt[0])
        return True

    @property
    def input_descriptors(self) -> Sequence[retro_input_descriptor] | None:
        return self._input.descriptors

    @override
    def _set_input_descriptors(self, descriptors: TypedPointer[retro_input_descriptor]) -> bool:
        if not descriptors:
            raise ValueError("RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS doesn't accept NULL")

        self._input.descriptors = tuple(deepcopy(d) for d in from_zero_terminated(descriptors))
        return True

    @property
    def keyboard_callback(self) -> retro_keyboard_callback | None:
        return self._input.keyboard_callback

    @override
    def _set_keyboard_callback(self, callback: TypedPointer[retro_keyboard_callback]) -> bool:
        if not callback:
            raise ValueError("RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK doesn't accept NULL")

        self._input.keyboard_callback = deepcopy(callback[0])
        return True

    @override
    def _set_disk_control_interface(
        self, callback: TypedPointer[retro_disk_control_callback]
    ) -> bool:
        return False  # TODO: Implement

    @override
    def _set_hw_render(self, callback: TypedPointer[retro_hw_render_callback]) -> bool:
        if not callback:
            raise ValueError("RETRO_ENVIRONMENT_SET_HW_RENDER doesn't accept NULL")

        core_callback = callback[0]
        self._video.set_context(core_callback)

        if not self._hw_render_callback:
            self._hw_render_callback = retro_hw_render_callback(
                get_current_framebuffer=retro_hw_get_current_framebuffer_t(
                    self._get_current_framebuffer
                ),
                get_proc_address=retro_hw_get_proc_address_t(self._get_hw_proc_address),
            )

        core_callback.get_current_framebuffer = self._hw_render_callback.get_current_framebuffer
        core_callback.get_proc_address = self._hw_render_callback.get_proc_address
        # Give the core the callbacks that the video driver defines

        return True

    def _get_current_framebuffer(self) -> int:
        return self._video.current_framebuffer or 0

    def _get_hw_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        return self._video.get_proc_address(sym)

    @property
    def options(self) -> Option:
        return self._options

    @override
    def _get_variable(self, variable: TypedPointer[retro_variable]) -> bool:
        if self._options is None:
            return False

        if variable:
            key = variable[0].key

            if key is not None:
                variable[0].value = self._options.get_variable(key)

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _set_variables(self, variables: TypedPointer[retro_variable]) -> bool:
        if self._options is None:
            return False

        if variables:
            definitions = tuple(deepcopy(s) for s in from_zero_terminated(variables))
            self._options.set_variables(definitions)
        else:
            self._options.set_variables(None)

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _get_variable_update(self, updated: TypedPointer[c_bool]) -> bool:
        if self._options is None:
            return False

        if not updated:
            raise ValueError("RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE doesn't accept NULL")

        updated[0] = self._options.variable_updated
        return True

    @property
    def support_no_game(self) -> bool | None:
        if self._content is None:
            return None

        return self._content.support_no_game

    @override
    def _set_support_no_game(self, support: TypedPointer[c_bool]) -> bool:
        if self._content is None:
            return False

        if not support:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME doesn't accept NULL")

        self._content.support_no_game = support[0]
        return True

    @override
    def _get_libretro_path(self, path: TypedPointer[c_char_p]) -> bool:
        if self._path is None or not self._path.libretro_path:
            return False

        if not path:
            raise ValueError("RETRO_ENVIRONMENT_GET_LIBRETRO_PATH doesn't accept NULL")

        path[0] = self._path.libretro_path
        return True

    @override
    def _set_frame_time_callback(self, callback: TypedPointer[retro_frame_time_callback]) -> bool:
        if self._timing is None:
            return False

        if not callback:
            raise ValueError("RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK doesn't accept NULL")

        self._timing.frame_time_callback = deepcopy(callback[0])
        return True

    @override
    def _set_audio_callback(self, callback: TypedPointer[retro_audio_callback]) -> bool:
        if callback:
            self._audio.callbacks = deepcopy(callback[0])

        return True

    @override
    def _get_rumble_interface(self, rumble: TypedPointer[retro_rumble_interface]) -> bool:
        if not rumble:
            raise ValueError("RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE doesn't accept NULL")

        if not self._rumble:
            return False

        if not self._rumble_interface:
            self._rumble_interface = retro_rumble_interface(
                retro_set_rumble_state_t(self._set_rumble_state)
            )
            # So that even if the rumble/input drivers are swapped out,
            # the core still has valid function pointers tied to non-GC'd callable objects

        rumble[0] = self._rumble_interface
        return True

    def _set_rumble_state(self, port: Port, effect: int, strength: int) -> bool:
        if self._rumble is None:
            return False

        return self._rumble.set_rumble_state(port, RumbleEffect(effect), strength)

    @override
    def _get_input_device_capabilities(self, capabilities: TypedPointer[c_uint64]) -> bool:
        if not capabilities:
            raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES doesn't accept NULL")

        caps = self._input.device_capabilities
        if caps is None:
            return False

        capabilities[0] = caps
        return True

    @override
    def _get_sensor_interface(self, interface: TypedPointer[retro_sensor_interface]) -> bool:
        if not interface:
            raise ValueError("RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE doesn't accept NULL")

        if not self._sensor:
            return False

        if not self._sensor_interface:
            self._sensor_interface = retro_sensor_interface(
                set_sensor_state=retro_set_sensor_state_t(self._set_sensor_state),
                get_sensor_input=retro_sensor_get_input_t(self._get_sensor_input),
            )
            # So that even if the sensor/input drivers are swapped out,
            # the core still has valid function pointers tied to non-GC'd callable objects

        interface[0] = self._sensor_interface
        return True

    def _set_sensor_state(self, port: Port, action: int, rate: int) -> bool:
        if self._sensor is None:
            return False

        if self._input.max_users is not None and port >= self._input.max_users:
            # If we have a max-user limit set, and the port number exceeds it...
            return False

        if action not in SensorAction:
            # If the action isn't a valid SensorAction, then we shouldn't pass it to the driver
            return False

        return self._sensor.set_sensor_state(port, SensorAction(action), rate)

    def _get_sensor_input(self, port: Port, sensor: int) -> float:
        if self._sensor is None:
            return 0.0

        if self._input.max_users is not None and port >= self._input.max_users:
            # If we have a max-user limit set, and the port number exceeds it...
            return False

        if sensor not in SensorAxis:
            # If the sensor isn't a valid SensorAxis, then we shouldn't pass it to the driver
            return False

        return self._sensor.get_sensor_input(port, SensorAxis(sensor))

    @override
    def _get_camera_interface(self, interface: TypedPointer[retro_camera_callback]) -> bool:
        if self._camera is None:
            return False

        if not interface:
            raise ValueError("RETRO_ENVIRONMENT_GET_CAMERA_INTERFACE doesn't accept NULL")

        if not self._camera_callback:
            self._camera_callback = retro_camera_callback(
                start=self._camera_start,
                stop=self._camera_stop,
            )

        callback = interface[0]
        self._camera.width = callback.width
        self._camera.height = callback.height
        self._camera.frame_raw_framebuffer = callback.frame_raw_framebuffer
        self._camera.frame_opengl_texture = callback.frame_opengl_texture
        self._camera.initialized = callback.initialized
        self._camera.deinitialized = callback.deinitialized

        callback.start = self._camera_callback.start
        callback.stop = self._camera_callback.stop

        return True

    def _camera_start(self) -> bool:
        if self._camera is None:
            return False

        return self._camera.start()

    def _camera_stop(self) -> None:
        if self._camera is not None:
            self._camera.stop()

    @property
    def log(self) -> Log:
        return self._log_driver

    @override
    def _get_log_interface(self, interface: TypedPointer[retro_log_callback]) -> bool:
        if self._log_driver is None:
            return False

        if not interface:
            raise ValueError("RETRO_ENVIRONMENT_GET_LOG_INTERFACE doesn't accept NULL")

        if not self._log_callback:
            self._log_callback = retro_log_callback(log=retro_log_printf_t(self._log))

        interface[0] = self._log_callback
        return True

    def _log(self, level: int, message: bytes):
        if self._log_driver is not None and level in LogLevel:
            self._log_driver.log(LogLevel(level), message)

    @property
    def perf(self) -> Perf:
        return self._perf

    @override
    def _get_perf_interface(self, interface: TypedPointer[retro_perf_callback]) -> bool:
        if self._perf is None:
            return False

        if not interface:
            raise ValueError("RETRO_ENVIRONMENT_GET_PERF_INTERFACE doesn't accept NULL")

        if not self._perf_callback:
            self._perf_callback = retro_perf_callback(
                get_time_usec=self._perf.get_time_usec,
                get_cpu_features=self._perf.get_cpu_features,
                get_perf_counter=self._perf.get_perf_counter,
                perf_register=self._perf.perf_register,
                perf_start=self._perf.perf_start,
                perf_stop=self._perf.perf_stop,
                perf_log=self._perf.perf_log,
            )

        interface[0] = self._perf_callback
        return True

    def _get_time_usec(self) -> int:
        if self._perf is None:
            return 0

        return self._perf.get_time_usec()

    def _get_cpu_features(self) -> int:
        if self._perf is None:
            return 0

        return self._perf.get_cpu_features()

    def _get_perf_counter(self) -> int:
        if self._perf is None:
            return 0

        return self._perf.get_perf_counter()

    def _perf_register(self, counter: TypedPointer[retro_perf_counter]):
        if self._perf is not None and counter:
            self._perf.perf_register(counter[0])

    def _perf_start(self, counter: TypedPointer[retro_perf_counter]):
        if self._perf is not None and counter:
            self._perf.perf_start(counter[0])

    def _perf_stop(self, counter: TypedPointer[retro_perf_counter]):
        if self._perf is not None and counter:
            self._perf.perf_stop(counter[0])

    def _perf_log(self):
        if self._perf is not None:
            self._perf.perf_log()

    @property
    def location(self) -> Location:
        return self._location

    @override
    def _get_location_interface(self, interface: TypedPointer[retro_location_callback]) -> bool:
        if self._location is None:
            return False

        if not interface:
            raise ValueError("RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE doesn't accept NULL")

        if not self._location_callback:
            self._location_callback = retro_location_callback(
                start=retro_location_start_t(self._location_start),
                stop=retro_location_stop_t(self._location_stop),
                get_position=retro_location_get_position_t(self._location_get_position),
                set_interval=retro_location_set_interval_t(self._location_set_interval),
            )

        location = interface[0]

        self._location.initialized = location.initialized
        self._location.deinitialized = location.deinitialized

        location.start = self._location_callback.start
        location.stop = self._location_callback.stop
        location.get_position = self._location_callback.get_position
        location.set_interval = self._location_callback.set_interval

        return True

    def _location_start(self) -> bool:
        if self._location is None:
            return False

        return self._location.start()

    def _location_stop(self) -> None:
        if self._location is not None:
            self._location.stop()

    def _location_get_position(
        self,
        lat: TypedPointer[c_double],
        lon: TypedPointer[c_double],
        horiz_accuracy: TypedPointer[c_double],
        vert_accuracy: TypedPointer[c_double],
    ) -> bool:
        if self._location is None:
            return False

        if not lat or not lon or not horiz_accuracy or not vert_accuracy:
            raise ValueError("retro_location_get_position_t doesn't accept NULL")

        position = self._location.get_position()
        if position is None:
            return False

        lat[0] = position.latitude or 0.0
        lon[0] = position.longitude or 0.0
        horiz_accuracy[0] = position.horizontal_accuracy or 0.0
        vert_accuracy[0] = position.vertical_accuracy or 0.0
        return True

    def _location_set_interval(self, ms: int, distance: int) -> None:
        if self._location is not None:
            self._location.set_interval(ms, distance)

    @override
    def _get_core_assets_directory(self, dir: TypedPointer[c_char_p]) -> bool:
        if self._path is None or self._path.core_assets_dir is None:
            return False

        if not dir:
            raise ValueError("RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY doesn't accept NULL")

        dir[0] = self._path.core_assets_dir
        return True

    @override
    def _get_save_directory(self, dir: TypedPointer[c_char_p]) -> bool:
        if self._path is None or self._path.save_dir is None:
            return False

        if not dir:
            raise ValueError("RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY doesn't accept NULL")

        dir[0] = self._path.save_dir
        return True

    @override
    def _set_system_av_info(self, info: TypedPointer[retro_system_av_info]) -> bool:
        if not info:
            return False

        # TODO: Provide a way to disable this envcall
        av_info = info[0]
        self._video.system_av_info = av_info
        self._audio.system_av_info = av_info
        self._system_av_info = deepcopy(av_info)
        return True

    @property
    def proc_address_callback(self) -> retro_get_proc_address_interface | None:
        return self._proc_address_callback

    @overload
    def get_proc_address[
        T: _CFunctionType
    ](self, sym: str | bytes, funtype: type[T]) -> T | None: ...
    @overload
    def get_proc_address(
        self, sym: str | bytes, funtype: None = None
    ) -> retro_proc_address_t | None: ...
    @overload
    def get_proc_address[
        T: _CFunctionType
    ](self, sym: Literal[b"", ""], funtype: type[T] | None = None) -> None: ...

    def get_proc_address[
        T: _CFunctionType
    ](self, sym: str | bytes, funtype: type[T] | None = None) -> retro_proc_address_t | T | None:
        if not self._proc_address_callback or not sym:
            return None

        if not self._proc_address_callback.get_proc_address:
            return None

        name = as_bytes(sym)

        proc = self._proc_address_callback.get_proc_address(name)

        if not proc:
            return None

        if funtype:
            return cast(proc, funtype)

        return proc

    @override
    def _set_proc_address_callback(
        self, callback: TypedPointer[retro_get_proc_address_interface]
    ) -> bool:
        if not callback:
            self._proc_address_callback = None
        else:
            self._proc_address_callback = deepcopy(callback[0])

        return True

    @property
    def subsystems(self) -> Sequence[retro_subsystem_info] | None:
        if self._content is None:
            return None

        return self._content.subsystem_info

    @override
    def _set_subsystem_info(self, info: TypedPointer[retro_subsystem_info]) -> bool:
        if self._content is None:
            return False

        if not info:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO doesn't accept NULL")

        self._content.subsystem_info = tuple(deepcopy(s) for s in from_zero_terminated(info))
        return True

    @property
    def controller_info(self) -> Sequence[retro_controller_description] | None:
        return self._input.controller_info

    @override
    def _set_controller_info(self, info: TypedPointer[retro_controller_info]) -> bool:
        if not info:
            raise ValueError("RETRO_ENVIRONMENT_SET_CONTROLLER_INFO doesn't accept NULL")

        controller_info = info[0]
        array = (
            deepcopy_array(controller_info.types, controller_info.num_types)
            if controller_info.types
            else None
        )
        controller_infos = tuple(array) if array else ()
        self._input.controller_info = controller_infos

        return True

    @property
    def memory_maps(self) -> retro_memory_map | None:
        return self._memory_maps

    @override
    def _set_memory_maps(self, maps: TypedPointer[retro_memory_map]) -> bool:
        if not maps:
            raise ValueError("RETRO_ENVIRONMENT_SET_MEMORY_MAPS doesn't accept NULL")

        self._memory_maps = deepcopy(maps[0])
        return True

    @property
    def geometry(self) -> retro_game_geometry | None:
        return self._video.geometry

    @override
    def _set_geometry(self, geometry: TypedPointer[retro_game_geometry]) -> bool:
        if not geometry:
            raise ValueError("RETRO_ENVIRONMENT_SET_GEOMETRY doesn't accept NULL")

        self._video.geometry = geometry[0]
        return True

    @override
    def _get_username(self, username: TypedPointer[c_char_p]) -> bool:
        if self._user is None or self._user.username is None:
            return False

        if not username:
            raise ValueError("RETRO_ENVIRONMENT_GET_USERNAME doesn't accept NULL")

        username[0] = self._user.username
        return True

    @override
    def _get_language(self, language: TypedPointer[retro_language]) -> bool:
        if self._user is None or self._user.language is None:
            return False

        if not language:
            raise ValueError("RETRO_ENVIRONMENT_GET_LANGUAGE doesn't accept NULL")

        language[0] = self._user.language
        return True

    @override
    def _get_current_software_framebuffer(
        self, framebuffer: TypedPointer[retro_framebuffer]
    ) -> bool:
        if not framebuffer:
            raise ValueError(
                "RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER doesn't accept NULL"
            )

        core_fb = framebuffer[0]
        width = core_fb.width
        height = core_fb.height
        access = core_fb.access_flags
        fb = self._video.get_software_framebuffer(width, height, MemoryAccess(access))
        if not fb:
            return False

        core_fb.data = fb.data
        core_fb.pitch = fb.pitch
        core_fb.format = fb.format
        core_fb.memory_flags = fb.memory_flags
        return True

    @override
    def _get_hw_render_interface(self, interface: TypedPointer[retro_hw_render_interface]) -> bool:
        if not interface:
            raise ValueError("RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE doesn't accept NULL")

        driver_interface = self._video.hw_render_interface
        if not driver_interface:
            # This video driver doesn't provide (or need) a hardware render interface
            return False

        interface[0] = driver_interface
        return True

    @property
    def support_achievements(self) -> bool | None:
        return self._supports_achievements

    @override
    def _set_support_achievements(self, support: TypedPointer[c_bool]) -> bool:
        if not support:
            raise ValueError("RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS doesn't accept NULL")

        self._supports_achievements = support[0]
        return True

    @override
    def _set_hw_render_context_negotiation_interface(
        self, interface: TypedPointer[retro_hw_render_context_negotiation_interface]
    ) -> bool:
        return False  # TODO: Implement

    @property
    def serialization_quirks(self) -> SerializationQuirks | None:
        return self._serialization_quirks

    @override
    def _set_serialization_quirks(self, quirks: TypedPointer[c_uint64]) -> bool:
        if not quirks:
            raise ValueError("RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS doesn't accept NULL")

        self._serialization_quirks = SerializationQuirks(quirks[0])
        return True

    @property
    def hw_shared_context(self) -> bool:
        return self._video.shared_context

    @override
    def _set_hw_shared_context(self) -> bool:
        self._video.shared_context = True
        return True

    @property
    def vfs(self) -> Vfs:
        return self._vfs

    @override
    def _get_vfs_interface(self, vfs: TypedPointer[retro_vfs_interface_info]) -> bool:
        if self._vfs is None:
            return False

        if not vfs:
            raise ValueError("RETRO_ENVIRONMENT_GET_VFS_INTERFACE doesn't accept NULL")

        vfs_info = vfs[0]

        if vfs_info.required_interface_version > self._vfs.version:
            # If the core wants a higher version than what we offer...
            return False

        if self._vfs_interface is None:
            self._vfs_interface = retro_vfs_interface()

            if self._vfs.version >= 1:
                self._vfs_interface.get_path = retro_vfs_get_path_t(self._vfs_get_path)
                self._vfs_interface.open = retro_vfs_open_t(self._vfs_open)
                self._vfs_interface.close = retro_vfs_close_t(self._vfs_close)
                self._vfs_interface.size = retro_vfs_size_t(self._vfs_size)
                self._vfs_interface.tell = retro_vfs_tell_t(self._vfs_tell)
                self._vfs_interface.seek = retro_vfs_seek_t(self._vfs_seek)
                self._vfs_interface.read = retro_vfs_read_t(self._vfs_read)
                self._vfs_interface.write = retro_vfs_write_t(self._vfs_write)
                self._vfs_interface.flush = retro_vfs_flush_t(self._vfs_flush)
                self._vfs_interface.remove = retro_vfs_remove_t(self._vfs_remove)
                self._vfs_interface.rename = retro_vfs_rename_t(self._vfs_rename)

            if self._vfs.version >= 2:
                self._vfs_interface.truncate = retro_vfs_truncate_t(self._vfs_truncate)

            if self._vfs.version >= 3:
                self._vfs_interface.stat = retro_vfs_stat_t(self._vfs_stat)
                self._vfs_interface.mkdir = retro_vfs_mkdir_t(self._vfs_mkdir)
                self._vfs_interface.opendir = retro_vfs_opendir_t(self._vfs_opendir)
                self._vfs_interface.readdir = retro_vfs_readdir_t(self._vfs_readdir)
                self._vfs_interface.dirent_get_name = retro_vfs_dirent_get_name_t(
                    self._vfs_dirent_get_name
                )
                self._vfs_interface.dirent_is_dir = retro_vfs_dirent_is_dir_t(
                    self._vfs_dirent_is_dir
                )
                self._vfs_interface.closedir = retro_vfs_closedir_t(self._vfs_closedir)

        vfs_info.required_interface_version = self._vfs.version
        vfs_info.iface = pointer(self._vfs_interface)
        return True

    def _vfs_get_path(self, file: TypedPointer[retro_vfs_file_handle]) -> bytes | None:
        if self._vfs is None or not file:
            return None

        return self._vfs.get_path(file[0])

    def _vfs_open(self, path: bytes, mode: int, hints: int):
        if self._vfs is None or mode not in VfsFileAccess:
            return None

        file = self._vfs.open(path, VfsFileAccess(mode), VfsFileAccessHint(hints))
        if not file:
            return None

        return cast(pointer(file), c_void_p).value

    def _vfs_close(self, file: TypedPointer[retro_vfs_file_handle]):
        if self._vfs is None or not file:
            return -1

        return 0 if self._vfs.close(file[0]) else -1

    def _vfs_size(self, file: TypedPointer[retro_vfs_file_handle]) -> int:
        if self._vfs is None or not file:
            return -1

        return self._vfs.size(file[0])

    def _vfs_truncate(self, file: TypedPointer[retro_vfs_file_handle], length: int) -> int:
        if self._vfs is None or not file or length < 0:
            return -1

        return 0 if self._vfs.truncate(file[0], length) else -1

    def _vfs_tell(self, file: TypedPointer[retro_vfs_file_handle]) -> int:
        if self._vfs is None or not file:
            return -1

        return self._vfs.tell(file[0])

    def _vfs_seek(
        self, file: TypedPointer[retro_vfs_file_handle], offset: int, whence: int
    ) -> int:
        if self._vfs is None or not file or whence not in VfsSeekPosition:
            return -1

        return self._vfs.seek(file[0], offset, VfsSeekPosition(whence))

    def _vfs_read(
        self, file: TypedPointer[retro_vfs_file_handle], data: c_void_ptr, size: int
    ) -> int:
        if self._vfs is None or not file or not data or size < 0:
            return -1

        return self._vfs.read(file[0], memoryview_at(data, size, readonly=False))

    def _vfs_write(
        self, file: TypedPointer[retro_vfs_file_handle], data: c_void_ptr, size: int
    ) -> int:
        if self._vfs is None or not file or not data or size < 0:
            return -1

        return self._vfs.write(file[0], memoryview_at(data, size, readonly=True))

    def _vfs_flush(self, file: TypedPointer[retro_vfs_file_handle]) -> int:
        if self._vfs is None or not file:
            return -1

        return 0 if self._vfs.flush(file[0]) else -1

    def _vfs_remove(self, path: bytes) -> int:
        if self._vfs is None or not path:
            return -1

        return 0 if self._vfs.remove(path) else -1

    def _vfs_rename(self, old_path: bytes, new_path: bytes) -> int:
        if self._vfs is None or not old_path or not new_path:
            return -1

        return 0 if self._vfs.rename(old_path, new_path) else -1

    def _vfs_stat(self, path: bytes, size: TypedPointer[c_int32]) -> int:
        if self._vfs is None or not path:
            return 0

        stat = self._vfs.stat(path)
        if not stat:
            return 0

        vfs_stat, stat_size = stat
        if size:
            size[0] = stat_size

        return vfs_stat

    def _vfs_mkdir(self, path: bytes) -> int:
        if self._vfs is None or not path:
            return -1

        return self._vfs.mkdir(path)

    def _vfs_opendir(self, path: bytes, include_hidden: bool):
        if self._vfs is None or not path:
            return None

        dir = self._vfs.opendir(path, include_hidden)
        if not dir:
            return None

        return cast(pointer(dir), c_void_p).value

    def _vfs_readdir(self, dir: TypedPointer[retro_vfs_dir_handle]) -> bool:
        if self._vfs is None or not dir:
            return False

        return self._vfs.readdir(dir[0])

    def _vfs_dirent_get_name(self, dir: TypedPointer[retro_vfs_dir_handle]) -> bytes | None:
        if self._vfs is None or not dir:
            return None

        return self._vfs.dirent_get_name(dir[0])

    def _vfs_dirent_is_dir(self, dir: TypedPointer[retro_vfs_dir_handle]) -> bool:
        if self._vfs is None or not dir:
            return False

        return self._vfs.dirent_is_dir(dir[0])

    def _vfs_closedir(self, dir: TypedPointer[retro_vfs_dir_handle]) -> bool:
        if self._vfs is None or not dir:
            return False

        return self._vfs.closedir(dir[0])

    @property
    def led(self) -> Led:
        return self._led

    @override
    def _get_led_interface(self, led: TypedPointer[retro_led_interface]) -> bool:
        if self._led is None:
            return False

        if not led:
            # This envcall supports passing NULL to query for support
            return True

        if not self._led_interface:
            self._led_interface = retro_led_interface(
                set_led_state=retro_set_led_state_t(self._set_led_state)
            )

        led[0] = self._led_interface
        return True

    def _set_led_state(self, led: int, state: int) -> None:
        if self._led is not None:
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
    def _get_audio_video_enable(self, enable: TypedPointer[retro_av_enable_flags]) -> bool:
        if self._av_enable is None:
            return False

        if enable:
            enable[0] = self._av_enable

        # This envcall supports passing NULL to query for support
        return True
        # TODO: Derive this from the audio, video, and state drivers

    @property
    def midi(self) -> MidiDriver | None:
        return self._midi

    @override
    def _get_midi_interface(self, midi: TypedPointer[retro_midi_interface]) -> bool:
        if not self._midi:
            return False

        if not midi:
            # This envcall supports passing NULL to query for support
            return True

        if not self._midi_interface:
            self._midi_interface = retro_midi_interface(
                input_enabled=retro_midi_input_enabled_t(self._midi_input_enabled),
                output_enabled=retro_midi_output_enabled_t(self._midi_output_enabled),
                read=retro_midi_read_t(self._midi_read),
                write=retro_midi_write_t(self._midi_write),
                flush=retro_midi_flush_t(self._midi_flush),
            )

        midi[0] = self._midi_interface

        return True

    def _midi_input_enabled(self) -> bool:
        if self._midi is None:
            return False

        return self._midi.input_enabled

    def _midi_output_enabled(self) -> bool:
        if self._midi is None:
            return False

        return self._midi.output_enabled

    def _midi_read(self, byte: TypedPointer[c_uint8]) -> bool:
        if self._midi is None or not byte:
            return False

        result = self._midi.read()
        if result is None:
            return False

        byte[0] = result
        return True

    def _midi_write(self, byte: int, delta_time: int) -> bool:
        if self._midi is None:
            return False

        return self._midi.write(byte, delta_time)

    def _midi_flush(self) -> bool:
        if self._midi is None:
            return False

        return self._midi.flush()

    @override
    def _get_fastforwarding(self, is_fastforwarding: TypedPointer[c_bool]) -> bool:
        if self._timing is None:
            return False

        if self._timing.throttle_state is None:
            return False

        if not is_fastforwarding:
            raise ValueError("RETRO_ENVIRONMENT_GET_FASTFORWARDING doesn't accept NULL")

        is_fastforwarding[0] = (
            ThrottleMode(self._timing.throttle_state.mode) == ThrottleMode.FAST_FORWARD
        )
        return True

    @override
    def _get_target_refresh_rate(self, rate: TypedPointer[c_float]) -> bool:
        if self._timing is None or self._timing.target_refresh_rate is None:
            return False

        if not rate:
            raise ValueError("RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE doesn't accept NULL")

        rate[0] = self._timing.target_refresh_rate
        return True

    @property
    def input_bitmasks(self) -> bool | None:
        return self._input.bitmasks_supported

    @override
    def _get_input_bitmasks(self) -> bool:
        return bool(self._input.bitmasks_supported)

    @property
    def core_options_version(self) -> int | None:
        if self._options is None:
            return None

        return self._options.version

    @override
    def _get_core_options_version(self, version: TypedPointer[c_uint]) -> bool:
        if self._options is None:
            return False

        if not version:
            raise ValueError("RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION doesn't accept NULL")

        version[0] = self._options.version
        return True

    @override
    def _set_core_options(self, options: TypedPointer[retro_core_option_definition]) -> bool:
        if self._options is None:
            return False

        if options:
            if self._options.version < 1:
                return False

            self._options.set_options(tuple(deepcopy(o) for o in from_zero_terminated(options)))
        else:
            self._options.set_options(None)

        # This envcall supports passing NULL to reset the options
        return True

    @override
    def _set_core_options_intl(self, options: TypedPointer[retro_core_options_intl]) -> bool:
        if self._options is None:
            return False

        if options:
            if self._options.version < 1:
                return False

            self._options.set_options_intl(options[0])
        else:
            self._options.set_options_intl(None)

        # This envcall supports passing NULL to reset the options
        return True

    @override
    def _set_core_options_display(self, options: TypedPointer[retro_core_option_display]) -> bool:
        if self._options is None:
            return False

        if options:
            opt_display = options[0]

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
    def _get_preferred_hw_render(self, preferred: TypedPointer[retro_hw_context_type]) -> bool:
        if self._preferred_hw is None:
            return False

        if not preferred:
            raise ValueError("RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER doesn't accept NULL")

        preferred[0] = self._preferred_hw

        # This envcall returns True if the frontend supports the call
        # *and* the frontend can switch video drivers
        return bool(self._driver_switch_enable)
        # TODO: Move RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER to the VideoDriver and _driver_switch_enable to the VideoDriver

    @override
    def _get_disk_control_interface_version(self, version: TypedPointer[c_uint]) -> bool:
        return False  # TODO: Implement

    @override
    def _set_disk_control_ext_interface(
        self, interface: TypedPointer[retro_disk_control_ext_callback]
    ) -> bool:
        return False  # TODO: Implement

    @override
    def _get_message_interface_version(self, version: TypedPointer[c_uint]) -> bool:
        if self._message is None:
            return False

        if not version:
            raise ValueError("RETRO_ENVIRONMENT_GET_MESSAGE_INTERFACE_VERSION doesn't accept NULL")

        version[0] = self._message.version
        return True

    @override
    def _set_message_ext(self, message_ext: TypedPointer[retro_message_ext]) -> bool:
        if self._message is None:
            return False

        if not message_ext:
            raise ValueError("RETRO_ENVIRONMENT_SET_MESSAGE_EXT doesn't accept NULL")

        return self._message.set_message(message_ext[0])

    @override
    def _get_input_max_users(self, max_users: TypedPointer[c_uint]) -> bool:
        if not max_users:
            raise ValueError("RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS doesn't accept NULL")

        max_supported_users = self._input.max_users
        if max_supported_users is None:
            return False

        max_users[0] = max_supported_users
        return True

    @override
    def _set_audio_buffer_status_callback(
        self, callback: TypedPointer[retro_audio_buffer_status_callback]
    ) -> bool:
        if callback:
            self._audio.buffer_status = deepcopy(callback[0])
        else:
            self._audio.buffer_status = None

        return True

    @override
    def _set_minimum_audio_latency(self, latency: TypedPointer[c_uint]) -> bool:
        if latency:
            self._audio.minimum_latency = latency[0]

        return True

    @override
    def _set_fastforwarding_override(
        self, override: TypedPointer[retro_fastforwarding_override]
    ) -> bool:
        if self._timing is None:
            return False

        if override:
            self._timing.fastforwarding_override = deepcopy(override[0])

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _set_content_info_override(
        self, override: TypedPointer[retro_system_content_info_override]
    ) -> bool:
        if self._content is None:
            return False

        if not override:
            # This envcall supports passing NULL to query for support
            return True

        self._content.overrides = tuple(deepcopy(o) for o in from_zero_terminated(override))
        return True

    @override
    def _get_game_info_ext(self, info: TypedPointer[TypedPointer[retro_game_info_ext]]) -> bool:
        if self._content is None:
            return False

        if not info:
            return False

        info_ext = self._content.game_info_ext
        if info_ext is None:
            return False

        last_element = info_ext[-1]
        if not is_zeroed(last_element):
            raise ValueError(
                "The last element of game_info_ext must be zeroed out, or else the core may read out-of-bounds memory"
            )

        info_ptr = cast(pointer(info_ext), TypedPointer[retro_game_info_ext])
        info[0] = info_ptr
        return True

    @override
    def _set_core_options_v2(self, options: TypedPointer[retro_core_options_v2]) -> bool:
        if self._options is None:
            return False

        if self._options.version < 2:
            return False

        if options:
            self._options.set_options_v2(options[0])
        else:
            self._options.set_options_v2(None)

        return self._options.supports_categories

    @override
    def _set_core_options_v2_intl(self, options: TypedPointer[retro_core_options_v2_intl]) -> bool:
        if self._options is None:
            return False

        if self._options.version < 2:
            return False

        if options:
            self._options.set_options_v2_intl(options[0])
        else:
            self._options.set_options_v2_intl(None)

        return self._options.supports_categories

    @override
    def _set_core_options_update_display_callback(
        self, callback: TypedPointer[retro_core_options_update_display_callback]
    ) -> bool:
        if self._options is None:
            return False

        if callback:
            self._options.update_display_callback = callback[0]

        return True

    @override
    def _set_variable(self, variable: TypedPointer[retro_variable]) -> bool:
        if self._options is None:
            return False

        if not variable:
            # This envcall supports passing NULL to query for support
            return True

        var = variable[0]
        if not var.key:
            raise ValueError("Variable key cannot be empty")

        if not var.value:
            raise ValueError("Variable value cannot be empty")

        return self._options.set_variable(var.key, var.value)

    @override
    def _get_throttle_state(self, state: TypedPointer[retro_throttle_state]) -> bool:
        if self._timing is None or not self._timing.throttle_state:
            return False

        if not state:
            raise ValueError("RETRO_ENVIRONMENT_GET_THROTTLE_STATE doesn't accept NULL")

        state[0] = deepcopy(self._timing.throttle_state)

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
    def _get_savestate_context(self, context: TypedPointer[retro_savestate_context]) -> bool:
        if self._savestate_context is None:
            return False

        if context:
            context[0] = self._savestate_context

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _get_hw_render_context_negotiation_interface_support(
        self, support: TypedPointer[retro_hw_render_context_negotiation_interface]
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

    @override
    def _get_jit_capable(self, capable: TypedPointer[c_bool]) -> bool:
        if self._jit_capable is None:
            return False

        if not capable:
            raise ValueError("RETRO_ENVIRONMENT_GET_JIT_CAPABLE doesn't accept NULL")

        capable[0] = self._jit_capable
        return True

    @property
    def mic(self) -> Mic:
        return self._mic

    @override
    def _get_microphone_interface(
        self, interface: TypedPointer[retro_microphone_interface]
    ) -> bool:
        if self._mic is None:
            return False

        if self._mic_interface is None:
            self._mic_interface = retro_microphone_interface(
                interface_version=self._mic.version,
                open_mic=retro_open_mic_t(self._open_mic),
                close_mic=retro_close_mic_t(self._close_mic),
                get_params=retro_get_mic_params_t(self._get_mic_params),
                set_mic_state=retro_set_mic_state_t(self._set_mic_state),
                get_mic_state=retro_get_mic_state_t(self._get_mic_state),
                read_mic=retro_read_mic_t(self._read_mic),
            )

        if interface:
            target = interface[0]

            if target.interface_version != self._mic.version:
                return False

            target.open_mic = self._mic_interface.open_mic
            target.close_mic = self._mic_interface.close_mic
            target.get_params = self._mic_interface.get_params
            target.set_mic_state = self._mic_interface.set_mic_state
            target.get_mic_state = self._mic_interface.get_mic_state
            target.read_mic = self._mic_interface.read_mic

        # This envcall supports passing NULL to query for support
        return True

    def _open_mic(self, params: TypedPointer[retro_microphone_params]):
        if self._mic is None:
            return None

        mic = self._mic.open_mic(params[0] if params else None)
        if not mic:
            return None

        return cast(pointer(mic), c_void_p).value

    def _close_mic(self, mic: TypedPointer[retro_microphone]) -> None:
        if self._mic is not None and mic:
            self._mic.close_mic(mic[0])

    def _get_mic_params(
        self,
        mic: TypedPointer[retro_microphone],
        params: TypedPointer[retro_microphone_params],
    ) -> bool:
        if self._mic is None or not mic or not params:
            return False

        returned_params = self._mic.get_mic_params(mic[0])
        if not returned_params:
            return False

        params[0] = returned_params
        return True

    def _set_mic_state(self, mic: TypedPointer[retro_microphone], state: bool) -> bool:
        if self._mic is None or not mic:
            return False

        self._mic.set_mic_state(mic[0], state)
        return True

    def _get_mic_state(self, mic: TypedPointer[retro_microphone]) -> bool:
        if self._mic is None or not mic:
            return False

        return self._mic.get_mic_state(mic[0])

    def _read_mic(
        self, mic: TypedPointer[retro_microphone], buffer: TypedPointer[c_int16], frames: int
    ) -> int:
        if self._mic is None or not mic or not buffer or frames < 0:
            return -1

        returned_frames = self._mic.read_mic(mic[0], frames)
        if returned_frames is None:
            return -1

        returned_buffer, _ = returned_frames.buffer_info()
        memmove(buffer, returned_buffer, len(returned_frames) * returned_frames.itemsize)

        return len(returned_frames)

    @property
    def power(self) -> Power:
        return self._device_power

    @override
    def _get_device_power(self, power: TypedPointer[retro_device_power]) -> bool:
        if self._device_power is None:
            return False

        if power:
            power[0] = self._device_power.device_power

        # This envcall supports passing NULL to query for support
        return True

    @override
    def _set_netpacket_interface(self, interface: TypedPointer[retro_netpacket_callback]) -> bool:
        return False  # TODO: Implement

    @override
    def _get_playlist_directory(self, dir: TypedPointer[c_char_p]) -> bool:
        if self._path is None or self._path.playlist_dir is None:
            return False

        if not dir:
            raise ValueError("RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY doesn't accept NULL")

        dir[0] = self._path.playlist_dir
        return True


__all__ = ["CompositeEnvironmentDriver"]
