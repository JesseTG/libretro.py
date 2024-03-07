import logging
from collections.abc import *
from typing import *
import enum
from os import PathLike

from .retro import *


class Rotation(enum.IntEnum):
    NONE = 0
    Ninety = 1
    OneEighty = 2
    TwoSeventy = 3


class PixelFormat(enum.IntEnum):
    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565

    def bytes_per_pixel(self) -> int:
        match self:
            case self.RGB1555:
                return 2
            case self.XRGB8888:
                return 4
            case self.RGB565:
                return 2
            case _:
                raise ValueError(f"Unknown pixel format: {self}")

    def typecode(self) -> str:
        match self:
            case self.RGB1555:
                return 'H'
            case self.XRGB8888:
                return 'L'
            case self.RGB565:
                return 'H'
            case _:
                raise ValueError(f"Unknown pixel format: {self}")


class Region(enum.IntEnum):
    NTSC = RETRO_REGION_NTSC
    PAL = RETRO_REGION_PAL


class LogLevel(enum.IntEnum):
    Debug = RETRO_LOG_DEBUG
    Info = RETRO_LOG_INFO
    Warning = RETRO_LOG_WARN
    Error = RETRO_LOG_ERROR

    def to_logging_level(self) -> int:
        match self:
            case self.Debug:
                return logging.DEBUG
            case self.Info:
                return logging.INFO
            case self.Warning:
                return logging.WARN
            case self.Error:
                return logging.ERROR


@enum.unique
class EnvironmentCall(enum.IntEnum):
    SetRotation = RETRO_ENVIRONMENT_SET_ROTATION
    GetOverscan = RETRO_ENVIRONMENT_GET_OVERSCAN
    GetCanDupe = RETRO_ENVIRONMENT_GET_CAN_DUPE
    SetMessage = RETRO_ENVIRONMENT_SET_MESSAGE
    Shutdown = RETRO_ENVIRONMENT_SHUTDOWN
    SetPerformanceLevel = RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL
    GetSystemDirectory = RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY
    SetPixelFormat = RETRO_ENVIRONMENT_SET_PIXEL_FORMAT
    SetInputDescriptors = RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS
    SetKeyboardCallback = RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK
    SetDiskControlInterface = RETRO_ENVIRONMENT_SET_DISK_CONTROL_INTERFACE
    SetHwRender = RETRO_ENVIRONMENT_SET_HW_RENDER
    GetVariable = RETRO_ENVIRONMENT_GET_VARIABLE
    SetVariables = RETRO_ENVIRONMENT_SET_VARIABLES
    GetVariableUpdate = RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE
    SetSupportNoGame = RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME
    GetLibretroPath = RETRO_ENVIRONMENT_GET_LIBRETRO_PATH
    SetFrameTimeCallback = RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK
    SetAudioCallback = RETRO_ENVIRONMENT_SET_AUDIO_CALLBACK
    GetRumbleInterface = RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE
    GetInputDeviceCapabilities = RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES
    GetSensorInterface = RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE
    GetCameraInterface = RETRO_ENVIRONMENT_GET_CAMERA_INTERFACE
    GetLogInterface = RETRO_ENVIRONMENT_GET_LOG_INTERFACE
    GetPerfInterface = RETRO_ENVIRONMENT_GET_PERF_INTERFACE
    GetLocationInterface = RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE
    GetCoreAssetsDirectory = RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY
    GetSaveDirectory = RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY
    SetSystemAvInfo = RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO
    SetProcAddressCallback = RETRO_ENVIRONMENT_SET_PROC_ADDRESS_CALLBACK
    SetSubsystemInfo = RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO
    SetControllerInfo = RETRO_ENVIRONMENT_SET_CONTROLLER_INFO
    SetMemoryMaps = RETRO_ENVIRONMENT_SET_MEMORY_MAPS
    SetGeometry = RETRO_ENVIRONMENT_SET_GEOMETRY
    GetUsername = RETRO_ENVIRONMENT_GET_USERNAME
    GetLanguage = RETRO_ENVIRONMENT_GET_LANGUAGE
    GetCurrentSoftwareFramebuffer = RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER
    GetHwRenderInterface = RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE
    SetSupportAchievements = RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS
    SetHwRenderContextNegotiationInterface = RETRO_ENVIRONMENT_SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE
    SetSerializationQuirks = RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS
    SetHwSharedContext = RETRO_ENVIRONMENT_SET_HW_SHARED_CONTEXT
    GetVfsInterface = RETRO_ENVIRONMENT_GET_VFS_INTERFACE
    GetLedInterface = RETRO_ENVIRONMENT_GET_LED_INTERFACE
    GetAudioVideoEnable = RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE
    GetMidiInterface = RETRO_ENVIRONMENT_GET_MIDI_INTERFACE
    GetFastForwarding = RETRO_ENVIRONMENT_GET_FASTFORWARDING
    GetTargetRefreshRate = RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE
    GetInputBitmasks = RETRO_ENVIRONMENT_GET_INPUT_BITMASKS
    GetCoreOptionsVersion = RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION
    SetCoreOptions = RETRO_ENVIRONMENT_SET_CORE_OPTIONS
    SetCoreOptionsIntl = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL
    SetCoreOptionsDisplay = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY
    GetPreferredHwRender = RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER
    GetDiskControlInterfaceVersion = RETRO_ENVIRONMENT_GET_DISK_CONTROL_INTERFACE_VERSION
    SetDiskControlExtInterface = RETRO_ENVIRONMENT_SET_DISK_CONTROL_EXT_INTERFACE
    GetMessageInterfaceVersion = RETRO_ENVIRONMENT_GET_MESSAGE_INTERFACE_VERSION
    SetMessageExt = RETRO_ENVIRONMENT_SET_MESSAGE_EXT
    GetInputMaxUsers = RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS
    SetAudioBufferStatusCallback = RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK
    SetMinimumAudioLatency = RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY
    SetFastForwardingOverride = RETRO_ENVIRONMENT_SET_FASTFORWARDING_OVERRIDE
    SetContentInfoOverride = RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE
    GetGameInfoExt = RETRO_ENVIRONMENT_GET_GAME_INFO_EXT
    SetCoreOptionsV2 = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2
    SetCoreOptionsV2Intl = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL
    SetCoreOptionsUpdateDisplayCallback = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK
    SetVariable = RETRO_ENVIRONMENT_SET_VARIABLE
    GetThrottleState = RETRO_ENVIRONMENT_GET_THROTTLE_STATE
    GetSaveStateContext = RETRO_ENVIRONMENT_GET_SAVESTATE_CONTEXT
    GetHwRenderContextNegotiationInterfaceSupport = RETRO_ENVIRONMENT_GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT
    GetJitCapable = RETRO_ENVIRONMENT_GET_JIT_CAPABLE
    GetMicrophoneInterface = RETRO_ENVIRONMENT_GET_MICROPHONE_INTERFACE
    SetNetpacketInterface = RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE
    GetDevicePower = RETRO_ENVIRONMENT_GET_DEVICE_POWER
    GetPlaylistDirectory = 79 # Not synced to libretro-common yet


class SerializationQuirks(enum.IntFlag):
    Incomplete = RETRO_SERIALIZATION_QUIRK_INCOMPLETE
    MustInitialize = RETRO_SERIALIZATION_QUIRK_MUST_INITIALIZE
    CoreVariableSize = RETRO_SERIALIZATION_QUIRK_CORE_VARIABLE_SIZE
    FrontendVariableSize = RETRO_SERIALIZATION_QUIRK_FRONT_VARIABLE_SIZE
    SingleSession = RETRO_SERIALIZATION_QUIRK_SINGLE_SESSION
    EndianDependent = RETRO_SERIALIZATION_QUIRK_ENDIAN_DEPENDENT
    PlatformDependent = RETRO_SERIALIZATION_QUIRK_PLATFORM_DEPENDENT


class SavestateContext(enum.IntEnum):
    Normal = RETRO_SAVESTATE_CONTEXT_NORMAL
    RunaheadSameInstance = RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_INSTANCE
    RunaheadSameBinary = RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_BINARY
    RollbackNetplay = RETRO_SAVESTATE_CONTEXT_ROLLBACK_NETPLAY
    Unknown = RETRO_SAVESTATE_CONTEXT_UNKNOWN


class MessageTarget(enum.IntEnum):
    All = RETRO_MESSAGE_TARGET_ALL
    Osd = RETRO_MESSAGE_TARGET_OSD
    Log = RETRO_MESSAGE_TARGET_LOG


class MessageType(enum.IntEnum):
    Notification = RETRO_MESSAGE_TYPE_NOTIFICATION
    NotificationAlt = RETRO_MESSAGE_TYPE_NOTIFICATION_ALT
    Status = RETRO_MESSAGE_TYPE_STATUS
    Progress = RETRO_MESSAGE_TYPE_PROGRESS


class InputDevice(enum.IntEnum):
    None_ = RETRO_DEVICE_NONE
    Joypad = RETRO_DEVICE_JOYPAD
    Mouse = RETRO_DEVICE_MOUSE
    Keyboard = RETRO_DEVICE_KEYBOARD
    LightGun = RETRO_DEVICE_LIGHTGUN
    Analog = RETRO_DEVICE_ANALOG
    Pointer = RETRO_DEVICE_POINTER


class InputDeviceFlag(enum.IntFlag):
    None_ = 1 << RETRO_DEVICE_NONE
    Joypad = 1 << RETRO_DEVICE_JOYPAD
    Mouse = 1 << RETRO_DEVICE_MOUSE
    Keyboard = 1 << RETRO_DEVICE_KEYBOARD
    LightGun = 1 << RETRO_DEVICE_LIGHTGUN
    Analog = 1 << RETRO_DEVICE_ANALOG
    Pointer = 1 << RETRO_DEVICE_POINTER


class JoypadId(enum.IntEnum):
    B = RETRO_DEVICE_ID_JOYPAD_B
    Y = RETRO_DEVICE_ID_JOYPAD_Y
    Select = RETRO_DEVICE_ID_JOYPAD_SELECT
    Start = RETRO_DEVICE_ID_JOYPAD_START
    Up = RETRO_DEVICE_ID_JOYPAD_UP
    Down = RETRO_DEVICE_ID_JOYPAD_DOWN
    Left = RETRO_DEVICE_ID_JOYPAD_LEFT
    Right = RETRO_DEVICE_ID_JOYPAD_RIGHT
    A = RETRO_DEVICE_ID_JOYPAD_A
    X = RETRO_DEVICE_ID_JOYPAD_X
    L = RETRO_DEVICE_ID_JOYPAD_L
    R = RETRO_DEVICE_ID_JOYPAD_R
    L2 = RETRO_DEVICE_ID_JOYPAD_L2
    R2 = RETRO_DEVICE_ID_JOYPAD_R2
    L3 = RETRO_DEVICE_ID_JOYPAD_L3
    R3 = RETRO_DEVICE_ID_JOYPAD_R3
    Mask = RETRO_DEVICE_ID_JOYPAD_MASK


class AnalogId(enum.IntEnum):
    X = RETRO_DEVICE_ID_ANALOG_X
    Y = RETRO_DEVICE_ID_ANALOG_Y


class AnalogIndex(enum.IntEnum):
    Left = RETRO_DEVICE_INDEX_ANALOG_LEFT
    Right = RETRO_DEVICE_INDEX_ANALOG_RIGHT
    Button = RETRO_DEVICE_INDEX_ANALOG_BUTTON


class FileAccessMode(enum.IntFlag):
    Read = RETRO_VFS_FILE_ACCESS_READ
    Write = RETRO_VFS_FILE_ACCESS_WRITE
    ReadWrite = RETRO_VFS_FILE_ACCESS_READ_WRITE
    UpdateExisting = RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING


class FileAccessHint(enum.IntFlag):
    None_ = RETRO_VFS_FILE_ACCESS_HINT_NONE
    FrequentAccess = RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS


class FileSeekPos(enum.IntEnum):
    Start = RETRO_VFS_SEEK_POSITION_START
    Current = RETRO_VFS_SEEK_POSITION_CURRENT
    End = RETRO_VFS_SEEK_POSITION_END


class FileStat(enum.IntFlag):
    IsValid = RETRO_VFS_STAT_IS_VALID
    IsDirectory = RETRO_VFS_STAT_IS_DIRECTORY
    IsCharacterSpecial = RETRO_VFS_STAT_IS_CHARACTER_SPECIAL


class PowerState(enum.IntEnum):
    Unknown = RETRO_POWERSTATE_UNKNOWN
    Discharging = RETRO_POWERSTATE_DISCHARGING
    Charging = RETRO_POWERSTATE_CHARGING
    Charged = RETRO_POWERSTATE_CHARGED
    PluggedIn = RETRO_POWERSTATE_PLUGGED_IN


Directory = str | bytes
DevicePower = retro_device_power | Callable[[], retro_device_power]

if sys.version_info >= (3, 12):
    Content: TypeAlias = PathLike | bytes | bytearray | memoryview | Buffer
    # Buffer was added in Python 3.12
else:
    Content: TypeAlias = PathLike | bytes | bytearray | memoryview


