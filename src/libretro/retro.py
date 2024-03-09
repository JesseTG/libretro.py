__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import enum
import logging
import sys
from ctypes import *  # noqa: F401, F403
from typing import TYPE_CHECKING, get_type_hints

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types

if not hasattr(ctypes, "c_uintptr"):
    class c_uintptr(ctypes._SimpleCData):
        _type_ = "P"

    ctypes._check_size(c_uintptr)



class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):

    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value

# Taken from https://blag.nullteilerfrei.de/2021/06/20/prettier-struct-definitions-for-python-ctypes/
# Please use it for all future struct definitions
class FieldsFromTypeHints(type(ctypes.Structure)):
    def __new__(cls, name, bases, namespace):
        class AnnotationDummy:
            __annotations__ = namespace.get('__annotations__', {})
        annotations = get_type_hints(AnnotationDummy)
        namespace['_fields_'] = list(annotations.items())
        namespace['__slots__'] = list(annotations.keys())
        return type(ctypes.Structure).__new__(cls, name, bases, namespace)
# End preamble


class Rotation(enum.IntEnum):
    NONE = 0
    NINETY = 1
    ONE_EIGHTY = 2
    TWO_SEVENTY = 3

    def __init__(self, value):
        self._type_ = 'I'


retro_language = c_int
RETRO_LANGUAGE_ENGLISH = 0
RETRO_LANGUAGE_JAPANESE = 1
RETRO_LANGUAGE_FRENCH = 2
RETRO_LANGUAGE_SPANISH = 3
RETRO_LANGUAGE_GERMAN = 4
RETRO_LANGUAGE_ITALIAN = 5
RETRO_LANGUAGE_DUTCH = 6
RETRO_LANGUAGE_PORTUGUESE_BRAZIL = 7
RETRO_LANGUAGE_PORTUGUESE_PORTUGAL = 8
RETRO_LANGUAGE_RUSSIAN = 9
RETRO_LANGUAGE_KOREAN = 10
RETRO_LANGUAGE_CHINESE_TRADITIONAL = 11
RETRO_LANGUAGE_CHINESE_SIMPLIFIED = 12
RETRO_LANGUAGE_ESPERANTO = 13
RETRO_LANGUAGE_POLISH = 14
RETRO_LANGUAGE_VIETNAMESE = 15
RETRO_LANGUAGE_ARABIC = 16
RETRO_LANGUAGE_GREEK = 17
RETRO_LANGUAGE_TURKISH = 18
RETRO_LANGUAGE_SLOVAK = 19
RETRO_LANGUAGE_PERSIAN = 20
RETRO_LANGUAGE_HEBREW = 21
RETRO_LANGUAGE_ASTURIAN = 22
RETRO_LANGUAGE_FINNISH = 23
RETRO_LANGUAGE_INDONESIAN = 24
RETRO_LANGUAGE_SWEDISH = 25
RETRO_LANGUAGE_UKRAINIAN = 26
RETRO_LANGUAGE_CZECH = 27
RETRO_LANGUAGE_CATALAN_VALENCIA = 28
RETRO_LANGUAGE_CATALAN = 29
RETRO_LANGUAGE_BRITISH_ENGLISH = 30
RETRO_LANGUAGE_HUNGARIAN = 31
RETRO_LANGUAGE_BELARUSIAN = 32
RETRO_LANGUAGE_LAST = (RETRO_LANGUAGE_BELARUSIAN + 1)
RETRO_LANGUAGE_DUMMY = 0x7fffffff


class Language(enum.IntEnum):
    ENGLISH = RETRO_LANGUAGE_ENGLISH
    JAPANESE = RETRO_LANGUAGE_JAPANESE
    FRENCH = RETRO_LANGUAGE_FRENCH
    SPANISH = RETRO_LANGUAGE_SPANISH
    GERMAN = RETRO_LANGUAGE_GERMAN
    ITALIAN = RETRO_LANGUAGE_ITALIAN
    DUTCH = RETRO_LANGUAGE_DUTCH
    PORTUGUESE_BRAZIL = RETRO_LANGUAGE_PORTUGUESE_BRAZIL
    PORTUGUESE_PORTUGAL = RETRO_LANGUAGE_PORTUGUESE_PORTUGAL
    RUSSIAN = RETRO_LANGUAGE_RUSSIAN
    KOREAN = RETRO_LANGUAGE_KOREAN
    CHINESE_TRADITIONAL = RETRO_LANGUAGE_CHINESE_TRADITIONAL
    CHINESE_SIMPLIFIED = RETRO_LANGUAGE_CHINESE_SIMPLIFIED
    ESPERANTO = RETRO_LANGUAGE_ESPERANTO
    POLISH = RETRO_LANGUAGE_POLISH
    VIETNAMESE = RETRO_LANGUAGE_VIETNAMESE
    ARABIC = RETRO_LANGUAGE_ARABIC
    GREEK = RETRO_LANGUAGE_GREEK
    TURKISH = RETRO_LANGUAGE_TURKISH
    SLOVAK = RETRO_LANGUAGE_SLOVAK
    PERSIAN = RETRO_LANGUAGE_PERSIAN
    HEBREW = RETRO_LANGUAGE_HEBREW
    ASTURIAN = RETRO_LANGUAGE_ASTURIAN
    FINNISH = RETRO_LANGUAGE_FINNISH
    INDONESIAN = RETRO_LANGUAGE_INDONESIAN
    SWEDISH = RETRO_LANGUAGE_SWEDISH
    UKRAINIAN = RETRO_LANGUAGE_UKRAINIAN
    CZECH = RETRO_LANGUAGE_CZECH
    CATALAN_VALENCIA = RETRO_LANGUAGE_CATALAN_VALENCIA
    CATALAN = RETRO_LANGUAGE_CATALAN
    BRITISH_ENGLISH = RETRO_LANGUAGE_BRITISH_ENGLISH
    HUNGARIAN = RETRO_LANGUAGE_HUNGARIAN
    BELARUSIAN = RETRO_LANGUAGE_BELARUSIAN

    def __init__(self, value):
        self._type_ = 'I'


retro_key = c_int
RETROK_UNKNOWN = 0
RETROK_FIRST = 0
RETROK_BACKSPACE = 8
RETROK_TAB = 9
RETROK_CLEAR = 12
RETROK_RETURN = 13
RETROK_PAUSE = 19
RETROK_ESCAPE = 27
RETROK_SPACE = 32
RETROK_EXCLAIM = 33
RETROK_QUOTEDBL = 34
RETROK_HASH = 35
RETROK_DOLLAR = 36
RETROK_AMPERSAND = 38
RETROK_QUOTE = 39
RETROK_LEFTPAREN = 40
RETROK_RIGHTPAREN = 41
RETROK_ASTERISK = 42
RETROK_PLUS = 43
RETROK_COMMA = 44
RETROK_MINUS = 45
RETROK_PERIOD = 46
RETROK_SLASH = 47
RETROK_0 = 48
RETROK_1 = 49
RETROK_2 = 50
RETROK_3 = 51
RETROK_4 = 52
RETROK_5 = 53
RETROK_6 = 54
RETROK_7 = 55
RETROK_8 = 56
RETROK_9 = 57
RETROK_COLON = 58
RETROK_SEMICOLON = 59
RETROK_LESS = 60
RETROK_EQUALS = 61
RETROK_GREATER = 62
RETROK_QUESTION = 63
RETROK_AT = 64
RETROK_LEFTBRACKET = 91
RETROK_BACKSLASH = 92
RETROK_RIGHTBRACKET = 93
RETROK_CARET = 94
RETROK_UNDERSCORE = 95
RETROK_BACKQUOTE = 96
RETROK_a = 97
RETROK_b = 98
RETROK_c = 99
RETROK_d = 100
RETROK_e = 101
RETROK_f = 102
RETROK_g = 103
RETROK_h = 104
RETROK_i = 105
RETROK_j = 106
RETROK_k = 107
RETROK_l = 108
RETROK_m = 109
RETROK_n = 110
RETROK_o = 111
RETROK_p = 112
RETROK_q = 113
RETROK_r = 114
RETROK_s = 115
RETROK_t = 116
RETROK_u = 117
RETROK_v = 118
RETROK_w = 119
RETROK_x = 120
RETROK_y = 121
RETROK_z = 122
RETROK_LEFTBRACE = 123
RETROK_BAR = 124
RETROK_RIGHTBRACE = 125
RETROK_TILDE = 126
RETROK_DELETE = 127
RETROK_KP0 = 256
RETROK_KP1 = 257
RETROK_KP2 = 258
RETROK_KP3 = 259
RETROK_KP4 = 260
RETROK_KP5 = 261
RETROK_KP6 = 262
RETROK_KP7 = 263
RETROK_KP8 = 264
RETROK_KP9 = 265
RETROK_KP_PERIOD = 266
RETROK_KP_DIVIDE = 267
RETROK_KP_MULTIPLY = 268
RETROK_KP_MINUS = 269
RETROK_KP_PLUS = 270
RETROK_KP_ENTER = 271
RETROK_KP_EQUALS = 272
RETROK_UP = 273
RETROK_DOWN = 274
RETROK_RIGHT = 275
RETROK_LEFT = 276
RETROK_INSERT = 277
RETROK_HOME = 278
RETROK_END = 279
RETROK_PAGEUP = 280
RETROK_PAGEDOWN = 281
RETROK_F1 = 282
RETROK_F2 = 283
RETROK_F3 = 284
RETROK_F4 = 285
RETROK_F5 = 286
RETROK_F6 = 287
RETROK_F7 = 288
RETROK_F8 = 289
RETROK_F9 = 290
RETROK_F10 = 291
RETROK_F11 = 292
RETROK_F12 = 293
RETROK_F13 = 294
RETROK_F14 = 295
RETROK_F15 = 296
RETROK_NUMLOCK = 300
RETROK_CAPSLOCK = 301
RETROK_SCROLLOCK = 302
RETROK_RSHIFT = 303
RETROK_LSHIFT = 304
RETROK_RCTRL = 305
RETROK_LCTRL = 306
RETROK_RALT = 307
RETROK_LALT = 308
RETROK_RMETA = 309
RETROK_LMETA = 310
RETROK_LSUPER = 311
RETROK_RSUPER = 312
RETROK_MODE = 313
RETROK_COMPOSE = 314
RETROK_HELP = 315
RETROK_PRINT = 316
RETROK_SYSREQ = 317
RETROK_BREAK = 318
RETROK_MENU = 319
RETROK_POWER = 320
RETROK_EURO = 321
RETROK_UNDO = 322
RETROK_OEM_102 = 323
RETROK_LAST = (RETROK_OEM_102 + 1)
RETROK_DUMMY = 0x7fffffff

retro_mod = c_int

RETROKMOD_NONE = 0x0000
RETROKMOD_SHIFT = 0x01
RETROKMOD_CTRL = 0x02
RETROKMOD_ALT = 0x04
RETROKMOD_META = 0x08
RETROKMOD_NUMLOCK = 0x10
RETROKMOD_CAPSLOCK = 0x20
RETROKMOD_SCROLLOCK = 0x40
RETROKMOD_DUMMY = 0x7fffffff


class retro_vfs_file_handle(Structure):
    pass


class retro_vfs_dir_handle(Structure):
    pass


retro_vfs_get_path_t = CFUNCTYPE(c_char_p, POINTER(retro_vfs_file_handle))
retro_vfs_open_t = CFUNCTYPE(UNCHECKED(POINTER(retro_vfs_file_handle)), String, c_uint, c_uint)
retro_vfs_close_t = CFUNCTYPE(c_int, POINTER(retro_vfs_file_handle))
retro_vfs_size_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle))
retro_vfs_truncate_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_int64)
retro_vfs_tell_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle))
retro_vfs_seek_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_int64, c_int)
retro_vfs_read_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_void_p, c_uint64)
retro_vfs_write_t = CFUNCTYPE(c_int64, POINTER(retro_vfs_file_handle), c_void_p, c_uint64)
retro_vfs_flush_t = CFUNCTYPE(c_int, POINTER(retro_vfs_file_handle))
retro_vfs_remove_t = CFUNCTYPE(c_int, String)
retro_vfs_rename_t = CFUNCTYPE(c_int, String, String)
retro_vfs_stat_t = CFUNCTYPE(c_int, String, POINTER(c_int32))
retro_vfs_mkdir_t = CFUNCTYPE(c_int, String)
retro_vfs_opendir_t = CFUNCTYPE(UNCHECKED(POINTER(retro_vfs_dir_handle)), String, c_bool)
retro_vfs_readdir_t = CFUNCTYPE(c_bool, POINTER(retro_vfs_dir_handle))
retro_vfs_dirent_get_name_t = CFUNCTYPE(c_char_p, POINTER(retro_vfs_dir_handle))
retro_vfs_dirent_is_dir_t = CFUNCTYPE(c_bool, POINTER(retro_vfs_dir_handle))
retro_vfs_closedir_t = CFUNCTYPE(c_int, POINTER(retro_vfs_dir_handle))


class retro_vfs_interface(Structure, metaclass=FieldsFromTypeHints):
    get_path: retro_vfs_get_path_t
    open: retro_vfs_open_t
    close: retro_vfs_close_t
    size: retro_vfs_size_t
    tell: retro_vfs_tell_t
    seek: retro_vfs_seek_t
    read: retro_vfs_read_t
    write: retro_vfs_write_t
    flush: retro_vfs_flush_t
    remove: retro_vfs_remove_t
    rename: retro_vfs_rename_t
    truncate: retro_vfs_truncate_t
    stat: retro_vfs_stat_t
    mkdir: retro_vfs_mkdir_t
    opendir: retro_vfs_opendir_t
    readdir: retro_vfs_readdir_t
    dirent_get_name: retro_vfs_dirent_get_name_t
    dirent_is_dir: retro_vfs_dirent_is_dir_t
    closedir: retro_vfs_closedir_t


class retro_vfs_interface_info(Structure, metaclass=FieldsFromTypeHints):
    required_interface_version: c_uint32
    iface: POINTER(retro_vfs_interface)


retro_hw_render_interface_type = c_int

RETRO_HW_RENDER_INTERFACE_VULKAN = 0

RETRO_HW_RENDER_INTERFACE_D3D9 = 1

RETRO_HW_RENDER_INTERFACE_D3D10 = 2

RETRO_HW_RENDER_INTERFACE_D3D11 = 3

RETRO_HW_RENDER_INTERFACE_D3D12 = 4

RETRO_HW_RENDER_INTERFACE_GSKIT_PS2 = 5

RETRO_HW_RENDER_INTERFACE_DUMMY = 0x7fffffff


class retro_hw_render_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_interface_type
    interface_version: c_uint


retro_set_led_state_t = CFUNCTYPE(None, c_int, c_int)

class retro_led_interface(Structure, metaclass=FieldsFromTypeHints):
    set_led_state: retro_set_led_state_t

retro_midi_input_enabled_t = CFUNCTYPE(c_bool, )

retro_midi_output_enabled_t = CFUNCTYPE(c_bool, )

retro_midi_read_t = CFUNCTYPE(c_bool, POINTER(c_uint8))

retro_midi_write_t = CFUNCTYPE(c_bool, c_uint8, c_uint32)

retro_midi_flush_t = CFUNCTYPE(c_bool, )

class retro_midi_interface(Structure, metaclass=FieldsFromTypeHints):
    input_enabled: retro_midi_input_enabled_t
    output_enabled: retro_midi_output_enabled_t
    read: retro_midi_read_t
    write: retro_midi_write_t
    flush: retro_midi_flush_t

retro_hw_render_context_negotiation_interface_type = c_int

RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN = 0

RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_DUMMY = 0x7fffffff

class retro_hw_render_context_negotiation_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_type: retro_hw_render_context_negotiation_interface_type
    interface_version: c_uint


class retro_memory_descriptor(Structure):
    pass

retro_memory_descriptor.__slots__ = [
    'flags',
    'ptr',
    'offset',
    'start',
    'select',
    'disconnect',
    'len',
    'addrspace',
]
retro_memory_descriptor._fields_ = [
    ('flags', c_uint64),
    ('ptr', c_void_p),
    ('offset', c_size_t),
    ('start', c_size_t),
    ('select', c_size_t),
    ('disconnect', c_size_t),
    ('len', c_size_t),
    ('addrspace', String),
]

class retro_memory_map(Structure, metaclass=FieldsFromTypeHints):
    descriptors: POINTER(retro_memory_descriptor)
    num_descriptors: c_uint


class retro_controller_description(Structure):
    _fields_ = [
        ('desc', String),
        ('id', c_uint),
    ]

    __slots__ = [f[0] for f in _fields_]


class retro_controller_info(Structure, metaclass=FieldsFromTypeHints):
    types: POINTER(retro_controller_description)
    num_types: c_uint


class retro_subsystem_memory_info(Structure, metaclass=FieldsFromTypeHints):
    extension: String
    type: c_uint


class retro_subsystem_rom_info(Structure, metaclass=FieldsFromTypeHints):
    desc: String
    valid_extensions: String
    need_fullpath: c_bool
    block_extract: c_bool
    required: c_bool
    memory: POINTER(retro_subsystem_memory_info)
    num_memory: c_uint


class retro_subsystem_info(Structure, metaclass=FieldsFromTypeHints):
    desc: String
    ident: String
    roms: POINTER(retro_subsystem_rom_info)
    num_roms: c_uint
    id: c_uint


retro_proc_address_t = CFUNCTYPE(None, )

retro_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)

class retro_get_proc_address_interface(Structure, metaclass=FieldsFromTypeHints):
    get_proc_address: retro_get_proc_address_t

retro_log_level = c_int
RETRO_LOG_DEBUG = 0
RETRO_LOG_INFO = (RETRO_LOG_DEBUG + 1)
RETRO_LOG_WARN = (RETRO_LOG_INFO + 1)
RETRO_LOG_ERROR = (RETRO_LOG_WARN + 1)
RETRO_LOG_DUMMY = 0x7fffffff


class LogLevel(enum.IntEnum):
    DEBUG = RETRO_LOG_DEBUG
    INFO = RETRO_LOG_INFO
    WARNING = RETRO_LOG_WARN
    ERROR = RETRO_LOG_ERROR

    def __init__(self, value: int):
        self._type_ = 'I'

    @property
    def logging_level(self) -> int:
        match self:
            case self.DEBUG:
                return logging.DEBUG
            case self.INFO:
                return logging.INFO
            case self.WARNING:
                return logging.WARN
            case self.ERROR:
                return logging.ERROR


retro_log_printf_t = CFUNCTYPE(None, retro_log_level, String)

class retro_log_callback(Structure, metaclass=FieldsFromTypeHints):
    log: retro_log_printf_t

retro_perf_tick_t = c_uint64

retro_time_t = c_int64

class retro_perf_counter(Structure):
    pass

retro_perf_counter.__slots__ = [
    'ident',
    'start',
    'total',
    'call_cnt',
    'registered',
]
retro_perf_counter._fields_ = [
    ('ident', String),
    ('start', retro_perf_tick_t),
    ('total', retro_perf_tick_t),
    ('call_cnt', retro_perf_tick_t),
    ('registered', c_bool),
]

retro_perf_get_time_usec_t = CFUNCTYPE(UNCHECKED(retro_time_t), )

retro_perf_get_counter_t = CFUNCTYPE(UNCHECKED(retro_perf_tick_t), )

retro_get_cpu_features_t = CFUNCTYPE(c_uint64, )

retro_perf_log_t = CFUNCTYPE(None, )

retro_perf_register_t = CFUNCTYPE(None, POINTER(retro_perf_counter))

retro_perf_start_t = CFUNCTYPE(None, POINTER(retro_perf_counter))

retro_perf_stop_t = CFUNCTYPE(None, POINTER(retro_perf_counter))

class retro_perf_callback(Structure, metaclass=FieldsFromTypeHints):
    get_time_usec: retro_perf_get_time_usec_t
    get_cpu_features: retro_get_cpu_features_t
    get_perf_counter: retro_perf_get_counter_t
    perf_register: retro_perf_register_t
    perf_start: retro_perf_start_t
    perf_stop: retro_perf_stop_t
    perf_log: retro_perf_log_t


retro_sensor_action = c_int

RETRO_SENSOR_ACCELEROMETER_ENABLE = 0

RETRO_SENSOR_ACCELEROMETER_DISABLE = (RETRO_SENSOR_ACCELEROMETER_ENABLE + 1)

RETRO_SENSOR_GYROSCOPE_ENABLE = (RETRO_SENSOR_ACCELEROMETER_DISABLE + 1)

RETRO_SENSOR_GYROSCOPE_DISABLE = (RETRO_SENSOR_GYROSCOPE_ENABLE + 1)

RETRO_SENSOR_ILLUMINANCE_ENABLE = (RETRO_SENSOR_GYROSCOPE_DISABLE + 1)

RETRO_SENSOR_ILLUMINANCE_DISABLE = (RETRO_SENSOR_ILLUMINANCE_ENABLE + 1)

RETRO_SENSOR_DUMMY = 0x7fffffff

retro_set_sensor_state_t = CFUNCTYPE(c_bool, c_uint, retro_sensor_action, c_uint)

retro_sensor_get_input_t = CFUNCTYPE(c_float, c_uint, c_uint)

class retro_sensor_interface(Structure, metaclass=FieldsFromTypeHints):
    set_sensor_state: retro_set_sensor_state_t
    get_sensor_input: retro_sensor_get_input_t


retro_camera_buffer = c_int

RETRO_CAMERA_BUFFER_OPENGL_TEXTURE = 0

RETRO_CAMERA_BUFFER_RAW_FRAMEBUFFER = (RETRO_CAMERA_BUFFER_OPENGL_TEXTURE + 1)

RETRO_CAMERA_BUFFER_DUMMY = 0x7fffffff

retro_camera_start_t = CFUNCTYPE(c_bool, )

retro_camera_stop_t = CFUNCTYPE(None, )

retro_camera_lifetime_status_t = CFUNCTYPE(None, )

retro_camera_frame_raw_framebuffer_t = CFUNCTYPE(None, POINTER(c_uint32), c_uint, c_uint, c_size_t)

retro_camera_frame_opengl_texture_t = CFUNCTYPE(None, c_uint, c_uint, POINTER(c_float))

class retro_camera_callback(Structure, metaclass=FieldsFromTypeHints):
    caps: c_uint64
    width: c_uint
    height: c_uint
    start: retro_camera_start_t
    stop: retro_camera_stop_t
    frame_raw_framebuffer: retro_camera_frame_raw_framebuffer_t
    frame_opengl_texture: retro_camera_frame_opengl_texture_t
    initialized: retro_camera_lifetime_status_t
    deinitialized: retro_camera_lifetime_status_t


retro_location_set_interval_t = CFUNCTYPE(None, c_uint, c_uint)

retro_location_start_t = CFUNCTYPE(c_bool, )

retro_location_stop_t = CFUNCTYPE(None, )

retro_location_get_position_t = CFUNCTYPE(c_bool, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double))

retro_location_lifetime_status_t = CFUNCTYPE(None, )

class retro_location_callback(Structure, metaclass=FieldsFromTypeHints):
    start: retro_location_start_t
    stop: retro_location_stop_t
    get_position: retro_location_get_position_t
    set_interval: retro_location_set_interval_t
    initialized: retro_location_lifetime_status_t
    deinitialized: retro_location_lifetime_status_t


retro_rumble_effect = c_int

RETRO_RUMBLE_STRONG = 0

RETRO_RUMBLE_WEAK = 1

RETRO_RUMBLE_DUMMY = 0x7fffffff

retro_set_rumble_state_t = CFUNCTYPE(c_bool, c_uint, retro_rumble_effect, c_uint16)

class retro_rumble_interface(Structure, metaclass=FieldsFromTypeHints):
    set_rumble_state: retro_set_rumble_state_t

retro_audio_callback_t = CFUNCTYPE(None, )

retro_audio_set_state_callback_t = CFUNCTYPE(None, c_bool)

class retro_audio_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_audio_callback_t
    set_state: retro_audio_set_state_callback_t


retro_usec_t = c_int64

retro_frame_time_callback_t = CFUNCTYPE(None, retro_usec_t)

class retro_frame_time_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_frame_time_callback_t
    reference: retro_usec_t


retro_audio_buffer_status_callback_t = CFUNCTYPE(None, c_bool, c_uint, c_bool)

class retro_audio_buffer_status_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_audio_buffer_status_callback_t


retro_hw_context_reset_t = CFUNCTYPE(None, )

retro_hw_get_current_framebuffer_t = CFUNCTYPE(c_uintptr, )

retro_hw_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)

retro_hw_context_type = c_int

RETRO_HW_CONTEXT_NONE = 0

RETRO_HW_CONTEXT_OPENGL = 1

RETRO_HW_CONTEXT_OPENGLES2 = 2

RETRO_HW_CONTEXT_OPENGL_CORE = 3

RETRO_HW_CONTEXT_OPENGLES3 = 4

RETRO_HW_CONTEXT_OPENGLES_VERSION = 5

RETRO_HW_CONTEXT_VULKAN = 6

RETRO_HW_CONTEXT_D3D11 = 7

RETRO_HW_CONTEXT_D3D10 = 8

RETRO_HW_CONTEXT_D3D12 = 9

RETRO_HW_CONTEXT_D3D9 = 10

RETRO_HW_CONTEXT_DUMMY = 0x7fffffff

class retro_hw_render_callback(Structure, metaclass=FieldsFromTypeHints):
    context_type: retro_hw_context_type
    context_reset: retro_hw_context_reset_t
    get_current_framebuffer: retro_hw_get_current_framebuffer_t
    get_proc_address: retro_hw_get_proc_address_t
    depth: c_bool
    stencil: c_bool
    bottom_left_origin: c_bool
    version_major: c_uint
    version_minor: c_uint
    cache_context: c_bool
    context_destroy: retro_hw_context_reset_t
    debug_context: c_bool


retro_keyboard_event_t = CFUNCTYPE(None, c_bool, c_uint, c_uint32, c_uint16)

class retro_keyboard_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_keyboard_event_t


retro_set_eject_state_t = CFUNCTYPE(c_bool, c_bool)

retro_get_eject_state_t = CFUNCTYPE(c_bool, )

retro_get_image_index_t = CFUNCTYPE(c_uint, )

retro_set_image_index_t = CFUNCTYPE(c_bool, c_uint)

retro_get_num_images_t = CFUNCTYPE(c_uint, )


class retro_game_info(Structure, metaclass=FieldsFromTypeHints):
    path: c_char_p
    data: c_void_p
    size: c_size_t
    meta: c_char_p


retro_replace_image_index_t = CFUNCTYPE(c_bool, c_uint, POINTER(retro_game_info))

retro_add_image_index_t = CFUNCTYPE(c_bool, )

retro_set_initial_image_t = CFUNCTYPE(c_bool, c_uint, String)

retro_get_image_path_t = CFUNCTYPE(c_bool, c_uint, String, c_size_t)

retro_get_image_label_t = CFUNCTYPE(c_bool, c_uint, String, c_size_t)

class retro_disk_control_callback(Structure, metaclass=FieldsFromTypeHints):
    set_eject_state: retro_set_eject_state_t
    get_eject_state: retro_get_eject_state_t
    get_image_index: retro_get_image_index_t
    set_image_index: retro_set_image_index_t
    get_num_images: retro_get_num_images_t
    replace_image_index: retro_replace_image_index_t
    add_image_index: retro_add_image_index_t


class retro_disk_control_ext_callback(retro_disk_control_callback, metaclass=FieldsFromTypeHints):
    set_initial_image: retro_set_initial_image_t
    get_image_path: retro_get_image_path_t
    get_image_label: retro_get_image_label_t


retro_netpacket_send_t = CFUNCTYPE(None, c_int, c_void_p, c_size_t, c_uint16, c_bool)

retro_netpacket_start_t = CFUNCTYPE(None, c_uint16, retro_netpacket_send_t)

retro_netpacket_receive_t = CFUNCTYPE(None, c_void_p, c_size_t, c_uint16)

retro_netpacket_stop_t = CFUNCTYPE(None, )

retro_netpacket_poll_t = CFUNCTYPE(None, )

retro_netpacket_connected_t = CFUNCTYPE(c_bool, c_uint16)

retro_netpacket_disconnected_t = CFUNCTYPE(None, c_uint16)

class retro_netpacket_callback(Structure, metaclass=FieldsFromTypeHints):
    start: retro_netpacket_start_t
    receive: retro_netpacket_receive_t
    stop: retro_netpacket_stop_t
    poll: retro_netpacket_poll_t
    connected: retro_netpacket_connected_t
    disconnected: retro_netpacket_disconnected_t


retro_pixel_format = c_int
RETRO_PIXEL_FORMAT_0RGB1555 = 0
RETRO_PIXEL_FORMAT_XRGB8888 = 1
RETRO_PIXEL_FORMAT_RGB565 = 2
RETRO_PIXEL_FORMAT_UNKNOWN = 0x7fffffff


class PixelFormat(enum.IntEnum):
    RGB1555 = RETRO_PIXEL_FORMAT_0RGB1555
    XRGB8888 = RETRO_PIXEL_FORMAT_XRGB8888
    RGB565 = RETRO_PIXEL_FORMAT_RGB565

    def __init__(self, value):
        self._type_ = 'I'

    @property
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

    @property
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


retro_savestate_context = c_int

RETRO_SAVESTATE_CONTEXT_NORMAL = 0
RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_INSTANCE = 1
RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_BINARY = 2
RETRO_SAVESTATE_CONTEXT_ROLLBACK_NETPLAY = 3
RETRO_SAVESTATE_CONTEXT_UNKNOWN = 0x7fffffff


class SavestateContext(enum.IntEnum):
    NORMAL = RETRO_SAVESTATE_CONTEXT_NORMAL
    RUNAHEAD_SAME_INSTANCE = RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_INSTANCE
    RUNAHEAD_SAME_BINARY = RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_BINARY
    ROLLBACK_NETPLAY = RETRO_SAVESTATE_CONTEXT_ROLLBACK_NETPLAY

    def __init__(self, value: int):
        self._type_ = 'i'


class retro_message(Structure):
    pass

retro_message.__slots__ = [
    'msg',
    'frames',
]
retro_message._fields_ = [
    ('msg', String),
    ('frames', c_uint),
]

retro_message_target = c_int
RETRO_MESSAGE_TARGET_ALL = 0
RETRO_MESSAGE_TARGET_OSD = (RETRO_MESSAGE_TARGET_ALL + 1)
RETRO_MESSAGE_TARGET_LOG = (RETRO_MESSAGE_TARGET_OSD + 1)


class MessageTarget(enum.IntEnum):
    ALL = RETRO_MESSAGE_TARGET_ALL
    OSD = RETRO_MESSAGE_TARGET_OSD
    LOG = RETRO_MESSAGE_TARGET_LOG

    def __init__(self, value: int):
        self._type_ = 'I'


retro_message_type = c_int
RETRO_MESSAGE_TYPE_NOTIFICATION = 0
RETRO_MESSAGE_TYPE_NOTIFICATION_ALT = (RETRO_MESSAGE_TYPE_NOTIFICATION + 1)
RETRO_MESSAGE_TYPE_STATUS = (RETRO_MESSAGE_TYPE_NOTIFICATION_ALT + 1)
RETRO_MESSAGE_TYPE_PROGRESS = (RETRO_MESSAGE_TYPE_STATUS + 1)


class MessageType(enum.IntEnum):
    NOTIFICATION = RETRO_MESSAGE_TYPE_NOTIFICATION
    NOTIFICATION_ALT = RETRO_MESSAGE_TYPE_NOTIFICATION_ALT
    STATUS = RETRO_MESSAGE_TYPE_STATUS
    PROGRESS = RETRO_MESSAGE_TYPE_PROGRESS

    def __init__(self, value: int):
        self._type_ = 'I'


class retro_message_ext(Structure):
    pass

retro_message_ext.__slots__ = [
    'msg',
    'duration',
    'priority',
    'level',
    'target',
    'type',
    'progress',
]
retro_message_ext._fields_ = [
    ('msg', String),
    ('duration', c_uint),
    ('priority', c_uint),
    ('level', retro_log_level),
    ('target', retro_message_target),
    ('type', retro_message_type),
    ('progress', c_int8),
]

class retro_input_descriptor(Structure):
    pass

retro_input_descriptor.__slots__ = [
    'port',
    'device',
    'index',
    'id',
    'description',
]
retro_input_descriptor._fields_ = [
    ('port', c_uint),
    ('device', c_uint),
    ('index', c_uint),
    ('id', c_uint),
    ('description', String),
]


class retro_system_info(Structure, metaclass=FieldsFromTypeHints):
    library_name: String
    library_version: String
    valid_extensions: String
    need_fullpath: c_bool
    block_extract: c_bool


class retro_system_content_info_override(Structure, metaclass=FieldsFromTypeHints):
    extensions: String
    need_fullpath: c_bool
    persistent_data: c_bool

    def __repr__(self):
        return f"retro_system_content_info_override({self.extensions}, {self.need_fullpath!r}, {self.persistent_data!r})"

class retro_game_info_ext(Structure):
    pass

retro_game_info_ext.__slots__ = [
    'full_path',
    'archive_path',
    'archive_file',
    'dir',
    'name',
    'ext',
    'meta',
    'data',
    'size',
    'file_in_archive',
    'persistent_data',
]
retro_game_info_ext._fields_ = [
    ('full_path', String),
    ('archive_path', String),
    ('archive_file', String),
    ('dir', String),
    ('name', String),
    ('ext', String),
    ('meta', String),
    ('data', c_void_p),
    ('size', c_size_t),
    ('file_in_archive', c_bool),
    ('persistent_data', c_bool),
]

class retro_game_geometry(Structure, metaclass=FieldsFromTypeHints):
    base_width: c_uint
    base_height: c_uint
    max_width: c_uint
    max_height: c_uint
    aspect_ratio: c_float


class retro_system_timing(Structure, metaclass=FieldsFromTypeHints):
    fps: c_double
    sample_rate: c_double


class retro_system_av_info(Structure, metaclass=FieldsFromTypeHints):
    geometry: retro_game_geometry
    timing: retro_system_timing


class retro_variable(Structure):
    pass

retro_variable.__slots__ = [
    'key',
    'value',
]
retro_variable._fields_ = [
    ('key', String),
    ('value', String),
]

class retro_core_option_display(Structure):
    pass

retro_core_option_display.__slots__ = [
    'key',
    'visible',
]
retro_core_option_display._fields_ = [
    ('key', String),
    ('visible', c_bool),
]

class retro_core_option_value(Structure):
    pass

retro_core_option_value.__slots__ = [
    'value',
    'label',
]
retro_core_option_value._fields_ = [
    ('value', String),
    ('label', String),
]

class retro_core_option_definition(Structure):
    pass

retro_core_option_definition.__slots__ = [
    'key',
    'desc',
    'info',
    'values',
    'default_value',
]
retro_core_option_definition._fields_ = [
    ('key', String),
    ('desc', String),
    ('info', String),
    ('values', retro_core_option_value * int(128)),
    ('default_value', String),
]

class retro_core_options_intl(Structure):
    pass

retro_core_options_intl.__slots__ = [
    'us',
    'local',
]
retro_core_options_intl._fields_ = [
    ('us', POINTER(retro_core_option_definition)),
    ('local', POINTER(retro_core_option_definition)),
]

class retro_core_option_v2_category(Structure):
    pass

retro_core_option_v2_category.__slots__ = [
    'key',
    'desc',
    'info',
]
retro_core_option_v2_category._fields_ = [
    ('key', String),
    ('desc', String),
    ('info', String),
]

class retro_core_option_v2_definition(Structure):
    pass

retro_core_option_v2_definition.__slots__ = [
    'key',
    'desc',
    'desc_categorized',
    'info',
    'info_categorized',
    'category_key',
    'values',
    'default_value',
]
retro_core_option_v2_definition._fields_ = [
    ('key', String),
    ('desc', String),
    ('desc_categorized', String),
    ('info', String),
    ('info_categorized', String),
    ('category_key', String),
    ('values', retro_core_option_value * int(128)),
    ('default_value', String),
]

class retro_core_options_v2(Structure):
    pass

retro_core_options_v2.__slots__ = [
    'categories',
    'definitions',
]
retro_core_options_v2._fields_ = [
    ('categories', POINTER(retro_core_option_v2_category)),
    ('definitions', POINTER(retro_core_option_v2_definition)),
]

class retro_core_options_v2_intl(Structure):
    pass

retro_core_options_v2_intl.__slots__ = [
    'us',
    'local',
]
retro_core_options_v2_intl._fields_ = [
    ('us', POINTER(retro_core_options_v2)),
    ('local', POINTER(retro_core_options_v2)),
]

retro_core_options_update_display_callback_t = CFUNCTYPE(c_bool, )

class retro_core_options_update_display_callback(Structure):
    pass

retro_core_options_update_display_callback.__slots__ = [
    'callback',
]
retro_core_options_update_display_callback._fields_ = [
    ('callback', retro_core_options_update_display_callback_t),
]

class retro_framebuffer(Structure, metaclass=FieldsFromTypeHints):
    data: c_void_p
    width: c_uint
    height: c_uint
    pitch: c_size_t
    format: retro_pixel_format
    access_flags: c_uint
    memory_flags: c_uint


class retro_fastforwarding_override(Structure, metaclass=FieldsFromTypeHints):
    ratio: c_float
    fastforward: c_bool
    notification: c_bool
    inhibit_toggle: c_bool


class retro_throttle_state(Structure, metaclass=FieldsFromTypeHints):
    mode: c_uint
    rate: c_float

# This one has no fields, it doesn't need the weight of a metaclass
class retro_microphone(Structure):
    pass

retro_microphone_t = retro_microphone

class retro_microphone_params(Structure, metaclass=FieldsFromTypeHints):
    rate: c_uint


retro_microphone_params_t = retro_microphone_params

retro_open_mic_t = CFUNCTYPE(UNCHECKED(POINTER(retro_microphone_t)), POINTER(retro_microphone_params_t))

retro_close_mic_t = CFUNCTYPE(None, POINTER(retro_microphone_t))

retro_get_mic_params_t = CFUNCTYPE(c_bool, POINTER(retro_microphone_t), POINTER(retro_microphone_params_t))

retro_set_mic_state_t = CFUNCTYPE(c_bool, POINTER(retro_microphone_t), c_bool)

retro_get_mic_state_t = CFUNCTYPE(c_bool, POINTER(retro_microphone_t))

retro_read_mic_t = CFUNCTYPE(c_int, POINTER(retro_microphone_t), POINTER(c_int16), c_size_t)

class retro_microphone_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_version: c_uint
    open_mic: retro_open_mic_t
    close_mic: retro_close_mic_t
    get_params: retro_get_mic_params_t
    set_mic_state: retro_set_mic_state_t
    get_mic_state: retro_get_mic_state_t
    read_mic: retro_read_mic_t

retro_power_state = c_int

RETRO_POWERSTATE_UNKNOWN = 0

RETRO_POWERSTATE_DISCHARGING = (RETRO_POWERSTATE_UNKNOWN + 1)

RETRO_POWERSTATE_CHARGING = (RETRO_POWERSTATE_DISCHARGING + 1)

RETRO_POWERSTATE_CHARGED = (RETRO_POWERSTATE_CHARGING + 1)

RETRO_POWERSTATE_PLUGGED_IN = (RETRO_POWERSTATE_CHARGED + 1)

class retro_device_power(Structure, metaclass=FieldsFromTypeHints):
    state: retro_power_state
    seconds: c_int
    percent: c_int8


retro_environment_t = CFUNCTYPE(c_bool, c_uint, c_void_p)

retro_video_refresh_t = CFUNCTYPE(None, c_void_p, c_uint, c_uint, c_size_t)

retro_audio_sample_t = CFUNCTYPE(None, c_int16, c_int16)

retro_audio_sample_batch_t = CFUNCTYPE(c_size_t, POINTER(c_int16), c_size_t)

retro_input_poll_t = CFUNCTYPE(None, )

retro_input_state_t = CFUNCTYPE(c_int16, c_uint, c_uint, c_uint, c_uint)

RETRO_API_VERSION = 1
RETRO_DEVICE_TYPE_SHIFT = 8
RETRO_DEVICE_MASK = ((1 << RETRO_DEVICE_TYPE_SHIFT) - 1)
def RETRO_DEVICE_SUBCLASS(base: int, id: int) -> int:
    return (((id + 1) << RETRO_DEVICE_TYPE_SHIFT) | base)


RETRO_DEVICE_NONE = 0
RETRO_DEVICE_JOYPAD = 1
RETRO_DEVICE_MOUSE = 2
RETRO_DEVICE_KEYBOARD = 3
RETRO_DEVICE_LIGHTGUN = 4
RETRO_DEVICE_ANALOG = 5
RETRO_DEVICE_POINTER = 6


class InputDevice(enum.IntEnum):
    NONE = RETRO_DEVICE_NONE
    JOYPAD = RETRO_DEVICE_JOYPAD
    MOUSE = RETRO_DEVICE_MOUSE
    KEYBOARD = RETRO_DEVICE_KEYBOARD
    LIGHTGUN = RETRO_DEVICE_LIGHTGUN
    ANALOG = RETRO_DEVICE_ANALOG
    POINTER = RETRO_DEVICE_POINTER

    def __init__(self, value: int):
        self._type_ = 'H'


class InputDeviceFlag(enum.IntFlag):
    NONE = 1 << RETRO_DEVICE_NONE
    JOYPAD = 1 << RETRO_DEVICE_JOYPAD
    MOUSE = 1 << RETRO_DEVICE_MOUSE
    KEYBOARD = 1 << RETRO_DEVICE_KEYBOARD
    LIGHTGUN = 1 << RETRO_DEVICE_LIGHTGUN
    ANALOG = 1 << RETRO_DEVICE_ANALOG
    POINTER = 1 << RETRO_DEVICE_POINTER

RETRO_DEVICE_ID_JOYPAD_B = 0
RETRO_DEVICE_ID_JOYPAD_Y = 1
RETRO_DEVICE_ID_JOYPAD_SELECT = 2
RETRO_DEVICE_ID_JOYPAD_START = 3
RETRO_DEVICE_ID_JOYPAD_UP = 4
RETRO_DEVICE_ID_JOYPAD_DOWN = 5
RETRO_DEVICE_ID_JOYPAD_LEFT = 6
RETRO_DEVICE_ID_JOYPAD_RIGHT = 7
RETRO_DEVICE_ID_JOYPAD_A = 8
RETRO_DEVICE_ID_JOYPAD_X = 9
RETRO_DEVICE_ID_JOYPAD_L = 10
RETRO_DEVICE_ID_JOYPAD_R = 11
RETRO_DEVICE_ID_JOYPAD_L2 = 12
RETRO_DEVICE_ID_JOYPAD_R2 = 13
RETRO_DEVICE_ID_JOYPAD_L3 = 14
RETRO_DEVICE_ID_JOYPAD_R3 = 15
RETRO_DEVICE_ID_JOYPAD_MASK = 256

class DeviceIdJoypad(enum.IntEnum):
    B = RETRO_DEVICE_ID_JOYPAD_B
    Y = RETRO_DEVICE_ID_JOYPAD_Y
    SELECT = RETRO_DEVICE_ID_JOYPAD_SELECT
    START = RETRO_DEVICE_ID_JOYPAD_START
    UP = RETRO_DEVICE_ID_JOYPAD_UP
    DOWN = RETRO_DEVICE_ID_JOYPAD_DOWN
    LEFT = RETRO_DEVICE_ID_JOYPAD_LEFT
    RIGHT = RETRO_DEVICE_ID_JOYPAD_RIGHT
    A = RETRO_DEVICE_ID_JOYPAD_A
    X = RETRO_DEVICE_ID_JOYPAD_X
    L = RETRO_DEVICE_ID_JOYPAD_L
    R = RETRO_DEVICE_ID_JOYPAD_R
    L2 = RETRO_DEVICE_ID_JOYPAD_L2
    R2 = RETRO_DEVICE_ID_JOYPAD_R2
    L3 = RETRO_DEVICE_ID_JOYPAD_L3
    R3 = RETRO_DEVICE_ID_JOYPAD_R3
    MASK = RETRO_DEVICE_ID_JOYPAD_MASK

    def __init__(self, value: int):
        self._type_ = 'H'


RETRO_DEVICE_INDEX_ANALOG_LEFT = 0
RETRO_DEVICE_INDEX_ANALOG_RIGHT = 1
RETRO_DEVICE_INDEX_ANALOG_BUTTON = 2


class DeviceIndexAnalog(enum.IntEnum):
    LEFT = RETRO_DEVICE_INDEX_ANALOG_LEFT
    RIGHT = RETRO_DEVICE_INDEX_ANALOG_RIGHT
    BUTTON = RETRO_DEVICE_INDEX_ANALOG_BUTTON

    def __init__(self, value: int):
        self._type_ = 'H'


RETRO_DEVICE_ID_ANALOG_X = 0
RETRO_DEVICE_ID_ANALOG_Y = 1

class DeviceIdAnalog(enum.IntEnum):
    X = RETRO_DEVICE_ID_ANALOG_X
    Y = RETRO_DEVICE_ID_ANALOG_Y

    def __init__(self, value: int):
        self._type_ = 'H'



RETRO_DEVICE_ID_MOUSE_X = 0
RETRO_DEVICE_ID_MOUSE_Y = 1
RETRO_DEVICE_ID_MOUSE_LEFT = 2
RETRO_DEVICE_ID_MOUSE_RIGHT = 3
RETRO_DEVICE_ID_MOUSE_WHEELUP = 4
RETRO_DEVICE_ID_MOUSE_WHEELDOWN = 5
RETRO_DEVICE_ID_MOUSE_MIDDLE = 6
RETRO_DEVICE_ID_MOUSE_HORIZ_WHEELUP = 7
RETRO_DEVICE_ID_MOUSE_HORIZ_WHEELDOWN = 8
RETRO_DEVICE_ID_MOUSE_BUTTON_4 = 9
RETRO_DEVICE_ID_MOUSE_BUTTON_5 = 10
RETRO_DEVICE_ID_LIGHTGUN_SCREEN_X = 13
RETRO_DEVICE_ID_LIGHTGUN_SCREEN_Y = 14
RETRO_DEVICE_ID_LIGHTGUN_IS_OFFSCREEN = 15
RETRO_DEVICE_ID_LIGHTGUN_TRIGGER = 2
RETRO_DEVICE_ID_LIGHTGUN_RELOAD = 16
RETRO_DEVICE_ID_LIGHTGUN_AUX_A = 3
RETRO_DEVICE_ID_LIGHTGUN_AUX_B = 4
RETRO_DEVICE_ID_LIGHTGUN_START = 6
RETRO_DEVICE_ID_LIGHTGUN_SELECT = 7
RETRO_DEVICE_ID_LIGHTGUN_AUX_C = 8
RETRO_DEVICE_ID_LIGHTGUN_DPAD_UP = 9
RETRO_DEVICE_ID_LIGHTGUN_DPAD_DOWN = 10
RETRO_DEVICE_ID_LIGHTGUN_DPAD_LEFT = 11
RETRO_DEVICE_ID_LIGHTGUN_DPAD_RIGHT = 12
RETRO_DEVICE_ID_LIGHTGUN_X = 0
RETRO_DEVICE_ID_LIGHTGUN_Y = 1
RETRO_DEVICE_ID_LIGHTGUN_CURSOR = 3
RETRO_DEVICE_ID_LIGHTGUN_TURBO = 4
RETRO_DEVICE_ID_LIGHTGUN_PAUSE = 5
RETRO_DEVICE_ID_POINTER_X = 0
RETRO_DEVICE_ID_POINTER_Y = 1
RETRO_DEVICE_ID_POINTER_PRESSED = 2
RETRO_DEVICE_ID_POINTER_COUNT = 3

RETRO_REGION_NTSC = 0
RETRO_REGION_PAL = 1


class Region(enum.IntEnum):
    NTSC = RETRO_REGION_NTSC
    PAL = RETRO_REGION_PAL

    def __init__(self, value: int):
        self._type_ = 'I'


RETRO_MEMORY_MASK = 0xff
RETRO_MEMORY_SAVE_RAM = 0
RETRO_MEMORY_RTC = 1
RETRO_MEMORY_SYSTEM_RAM = 2
RETRO_MEMORY_VIDEO_RAM = 3
RETRO_ENVIRONMENT_EXPERIMENTAL = 0x10000
RETRO_ENVIRONMENT_PRIVATE = 0x20000
RETRO_ENVIRONMENT_SET_ROTATION = 1
RETRO_ENVIRONMENT_GET_OVERSCAN = 2
RETRO_ENVIRONMENT_GET_CAN_DUPE = 3
RETRO_ENVIRONMENT_SET_MESSAGE = 6
RETRO_ENVIRONMENT_SHUTDOWN = 7
RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL = 8
RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY = 9
RETRO_ENVIRONMENT_SET_PIXEL_FORMAT = 10
RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS = 11
RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK = 12
RETRO_ENVIRONMENT_SET_DISK_CONTROL_INTERFACE = 13
RETRO_ENVIRONMENT_SET_HW_RENDER = 14
RETRO_ENVIRONMENT_GET_VARIABLE = 15
RETRO_ENVIRONMENT_SET_VARIABLES = 16
RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE = 17
RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME = 18
RETRO_ENVIRONMENT_GET_LIBRETRO_PATH = 19
RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK = 21
RETRO_ENVIRONMENT_SET_AUDIO_CALLBACK = 22
RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE = 23
RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES = 24
RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE = (25 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_CAMERA_INTERFACE = (26 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_LOG_INTERFACE = 27
RETRO_ENVIRONMENT_GET_PERF_INTERFACE = 28
RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE = 29
RETRO_ENVIRONMENT_GET_CONTENT_DIRECTORY = 30
RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY = 30
RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY = 31
RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO = 32
RETRO_ENVIRONMENT_SET_PROC_ADDRESS_CALLBACK = 33
RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO = 34
RETRO_ENVIRONMENT_SET_CONTROLLER_INFO = 35
RETRO_ENVIRONMENT_SET_MEMORY_MAPS = (36 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_SET_GEOMETRY = 37
RETRO_ENVIRONMENT_GET_USERNAME = 38
RETRO_ENVIRONMENT_GET_LANGUAGE = 39
RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER = (40 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE = (41 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS = (42 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE = (43 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS = 44
RETRO_ENVIRONMENT_SET_HW_SHARED_CONTEXT = (44 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_VFS_INTERFACE = (45 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_LED_INTERFACE = (46 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE = (47 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_MIDI_INTERFACE = (48 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_FASTFORWARDING = (49 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE = (50 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_INPUT_BITMASKS = (51 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION = 52
RETRO_ENVIRONMENT_SET_CORE_OPTIONS = 53
RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL = 54
RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY = 55
RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER = 56
RETRO_ENVIRONMENT_GET_DISK_CONTROL_INTERFACE_VERSION = 57
RETRO_ENVIRONMENT_SET_DISK_CONTROL_EXT_INTERFACE = 58
RETRO_ENVIRONMENT_GET_MESSAGE_INTERFACE_VERSION = 59
RETRO_ENVIRONMENT_SET_MESSAGE_EXT = 60
RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS = 61
RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK = 62
RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY = 63
RETRO_ENVIRONMENT_SET_FASTFORWARDING_OVERRIDE = 64
RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE = 65
RETRO_ENVIRONMENT_GET_GAME_INFO_EXT = 66
RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2 = 67
RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL = 68
RETRO_ENVIRONMENT_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK = 69
RETRO_ENVIRONMENT_SET_VARIABLE = 70
RETRO_ENVIRONMENT_GET_THROTTLE_STATE = (71 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_SAVESTATE_CONTEXT = (72 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT = (73 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_JIT_CAPABLE = 74
RETRO_ENVIRONMENT_GET_MICROPHONE_INTERFACE = (75 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE = 76
RETRO_ENVIRONMENT_GET_DEVICE_POWER = (77 | RETRO_ENVIRONMENT_EXPERIMENTAL)
RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY = 79


@enum.unique
class EnvironmentCall(enum.IntEnum):
    SET_ROTATION = RETRO_ENVIRONMENT_SET_ROTATION
    GET_OVERSCAN = RETRO_ENVIRONMENT_GET_OVERSCAN
    GET_CAN_DUPE = RETRO_ENVIRONMENT_GET_CAN_DUPE
    SET_MESSAGE = RETRO_ENVIRONMENT_SET_MESSAGE
    SHUTDOWN = RETRO_ENVIRONMENT_SHUTDOWN
    SET_PERFORMANCE_LEVEL = RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL
    GET_SYSTEM_DIRECTORY = RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY
    SET_PIXEL_FORMAT = RETRO_ENVIRONMENT_SET_PIXEL_FORMAT
    SET_INPUT_DESCRIPTORS = RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS
    SET_KEYBOARD_CALLBACK = RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK
    SET_DISK_CONTROL_INTERFACE = RETRO_ENVIRONMENT_SET_DISK_CONTROL_INTERFACE
    SET_HW_RENDER = RETRO_ENVIRONMENT_SET_HW_RENDER
    GET_VARIABLE = RETRO_ENVIRONMENT_GET_VARIABLE
    SET_VARIABLES = RETRO_ENVIRONMENT_SET_VARIABLES
    GET_VARIABLE_UPDATE = RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE
    SET_SUPPORT_NO_GAME = RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME
    GET_LIBRETRO_PATH = RETRO_ENVIRONMENT_GET_LIBRETRO_PATH
    SET_FRAME_TIME_CALLBACK = RETRO_ENVIRONMENT_SET_FRAME_TIME_CALLBACK
    SET_AUDIO_CALLBACK = RETRO_ENVIRONMENT_SET_AUDIO_CALLBACK
    GET_RUMBLE_INTERFACE = RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE
    GET_INPUT_DEVICE_CAPABILITIES = RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES
    GET_SENSOR_INTERFACE = RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE
    GET_CAMERA_INTERFACE = RETRO_ENVIRONMENT_GET_CAMERA_INTERFACE
    GET_LOG_INTERFACE = RETRO_ENVIRONMENT_GET_LOG_INTERFACE
    GET_PERF_INTERFACE = RETRO_ENVIRONMENT_GET_PERF_INTERFACE
    GET_LOCATION_INTERFACE = RETRO_ENVIRONMENT_GET_LOCATION_INTERFACE
    GET_CORE_ASSETS_DIRECTORY = RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY
    GET_SAVE_DIRECTORY = RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY
    SET_SYSTEM_AV_INFO = RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO
    SET_PROC_ADDRESS_CALLBACK = RETRO_ENVIRONMENT_SET_PROC_ADDRESS_CALLBACK
    SET_SUBSYSTEM_INFO = RETRO_ENVIRONMENT_SET_SUBSYSTEM_INFO
    SET_CONTROLLER_INFO = RETRO_ENVIRONMENT_SET_CONTROLLER_INFO
    SET_MEMORY_MAPS = RETRO_ENVIRONMENT_SET_MEMORY_MAPS
    SET_GEOMETRY = RETRO_ENVIRONMENT_SET_GEOMETRY
    GET_USERNAME = RETRO_ENVIRONMENT_GET_USERNAME
    GET_LANGUAGE = RETRO_ENVIRONMENT_GET_LANGUAGE
    GET_CURRENT_SOFTWARE_FRAMEBUFFER = RETRO_ENVIRONMENT_GET_CURRENT_SOFTWARE_FRAMEBUFFER
    GET_HW_RENDER_INTERFACE = RETRO_ENVIRONMENT_GET_HW_RENDER_INTERFACE
    SET_SUPPORT_ACHIEVEMENTS = RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS
    SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE = RETRO_ENVIRONMENT_SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE
    SET_SERIALIZATION_QUIRKS = RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS
    SET_HW_SHARED_CONTEXT = RETRO_ENVIRONMENT_SET_HW_SHARED_CONTEXT
    GET_VFS_INTERFACE = RETRO_ENVIRONMENT_GET_VFS_INTERFACE
    GET_LED_INTERFACE = RETRO_ENVIRONMENT_GET_LED_INTERFACE
    GET_AUDIO_VIDEO_ENABLE = RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE
    GET_MIDI_INTERFACE = RETRO_ENVIRONMENT_GET_MIDI_INTERFACE
    GET_FASTFORWARDING = RETRO_ENVIRONMENT_GET_FASTFORWARDING
    GET_TARGET_REFRESH_RATE = RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE
    GET_INPUT_BITMASKS = RETRO_ENVIRONMENT_GET_INPUT_BITMASKS
    GET_CORE_OPTIONS_VERSION = RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION
    SET_CORE_OPTIONS = RETRO_ENVIRONMENT_SET_CORE_OPTIONS
    SET_CORE_OPTIONS_INTL = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL
    SET_CORE_OPTIONS_DISPLAY = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY
    GET_PREFERRED_HW_RENDER = RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER
    GET_DISK_CONTROL_INTERFACE_VERSION = RETRO_ENVIRONMENT_GET_DISK_CONTROL_INTERFACE_VERSION
    SET_DISK_CONTROL_EXT_INTERFACE = RETRO_ENVIRONMENT_SET_DISK_CONTROL_EXT_INTERFACE
    GET_MESSAGE_INTERFACE_VERSION = RETRO_ENVIRONMENT_GET_MESSAGE_INTERFACE_VERSION
    SET_MESSAGE_EXT = RETRO_ENVIRONMENT_SET_MESSAGE_EXT
    GET_INPUT_MAX_USERS = RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS
    SET_AUDIO_BUFFER_STATUS_CALLBACK = RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK
    SET_MINIMUM_AUDIO_LATENCY = RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY
    SET_FASTFORWARDING_OVERRIDE = RETRO_ENVIRONMENT_SET_FASTFORWARDING_OVERRIDE
    SET_CONTENT_INFO_OVERRIDE = RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE
    GET_GAME_INFO_EXT = RETRO_ENVIRONMENT_GET_GAME_INFO_EXT
    SET_CORE_OPTIONS_V2 = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2
    SET_CORE_OPTIONS_V2_INTL = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL
    SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK = RETRO_ENVIRONMENT_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK
    SET_VARIABLE = RETRO_ENVIRONMENT_SET_VARIABLE
    GET_THROTTLE_STATE = RETRO_ENVIRONMENT_GET_THROTTLE_STATE
    GET_SAVE_STATE_CONTEXT = RETRO_ENVIRONMENT_GET_SAVESTATE_CONTEXT
    GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT = RETRO_ENVIRONMENT_GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT
    GET_JIT_CAPABLE = RETRO_ENVIRONMENT_GET_JIT_CAPABLE
    GET_MICROPHONE_INTERFACE = RETRO_ENVIRONMENT_GET_MICROPHONE_INTERFACE
    SET_NETPACKET_INTERFACE = RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE
    GET_DEVICE_POWER = RETRO_ENVIRONMENT_GET_DEVICE_POWER
    GET_PLAYLIST_DIRECTORY = RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY

    def __init__(self, value: int):
        self._type_ = 'I'


RETRO_VFS_FILE_ACCESS_READ = (1 << 0)
RETRO_VFS_FILE_ACCESS_WRITE = (1 << 1)
RETRO_VFS_FILE_ACCESS_READ_WRITE = (RETRO_VFS_FILE_ACCESS_READ | RETRO_VFS_FILE_ACCESS_WRITE)
RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING = (1 << 2)


class VfsFileAccess(enum.IntFlag):
    READ = RETRO_VFS_FILE_ACCESS_READ
    WRITE = RETRO_VFS_FILE_ACCESS_WRITE
    READ_WRITE = RETRO_VFS_FILE_ACCESS_READ_WRITE
    UPDATE_EXISTING = RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING

    def __init__(self, value: int):
        self._type_ = 'I'


RETRO_VFS_FILE_ACCESS_HINT_NONE = 0
RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS = (1 << 0)


class VfsFileAccessHint(enum.IntFlag):
    NONE = RETRO_VFS_FILE_ACCESS_HINT_NONE
    FREQUENT_ACCESS = RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS

    def __init__(self, value: int):
        self._type_ = 'I'


RETRO_VFS_SEEK_POSITION_START = 0
RETRO_VFS_SEEK_POSITION_CURRENT = 1
RETRO_VFS_SEEK_POSITION_END = 2


class VfsSeekPosition(enum.IntEnum):
    START = RETRO_VFS_SEEK_POSITION_START
    CURRENT = RETRO_VFS_SEEK_POSITION_CURRENT
    END = RETRO_VFS_SEEK_POSITION_END

    def __init__(self, value: int):
        self._type_ = 'I'


RETRO_VFS_STAT_IS_VALID = (1 << 0)
RETRO_VFS_STAT_IS_DIRECTORY = (1 << 1)
RETRO_VFS_STAT_IS_CHARACTER_SPECIAL = (1 << 2)


class VfsStat(enum.IntFlag):
    IS_VALID = RETRO_VFS_STAT_IS_VALID
    IS_DIRECTORY = RETRO_VFS_STAT_IS_DIRECTORY
    IS_CHARACTER_SPECIAL = RETRO_VFS_STAT_IS_CHARACTER_SPECIAL

    def __init__(self, value: int):
        self._type_ = 'I'


RETRO_SERIALIZATION_QUIRK_INCOMPLETE = (1 << 0)
RETRO_SERIALIZATION_QUIRK_MUST_INITIALIZE = (1 << 1)
RETRO_SERIALIZATION_QUIRK_CORE_VARIABLE_SIZE = (1 << 2)
RETRO_SERIALIZATION_QUIRK_FRONT_VARIABLE_SIZE = (1 << 3)
RETRO_SERIALIZATION_QUIRK_SINGLE_SESSION = (1 << 4)
RETRO_SERIALIZATION_QUIRK_ENDIAN_DEPENDENT = (1 << 5)
RETRO_SERIALIZATION_QUIRK_PLATFORM_DEPENDENT = (1 << 6)


class SerializationQuirks(enum.IntFlag):
    INCOMPLETE = RETRO_SERIALIZATION_QUIRK_INCOMPLETE
    MUST_INITIALIZE = RETRO_SERIALIZATION_QUIRK_MUST_INITIALIZE
    CORE_VARIABLE_SIZE = RETRO_SERIALIZATION_QUIRK_CORE_VARIABLE_SIZE
    FRONTEND_VARIABLE_SIZE = RETRO_SERIALIZATION_QUIRK_FRONT_VARIABLE_SIZE
    SINGLE_SESSION = RETRO_SERIALIZATION_QUIRK_SINGLE_SESSION
    ENDIAN_DEPENDENT = RETRO_SERIALIZATION_QUIRK_ENDIAN_DEPENDENT
    PLATFORM_DEPENDENT = RETRO_SERIALIZATION_QUIRK_PLATFORM_DEPENDENT


RETRO_MEMDESC_CONST = (1 << 0)
RETRO_MEMDESC_BIGENDIAN = (1 << 1)
RETRO_MEMDESC_SYSTEM_RAM = (1 << 2)
RETRO_MEMDESC_SAVE_RAM = (1 << 3)
RETRO_MEMDESC_VIDEO_RAM = (1 << 4)
RETRO_MEMDESC_ALIGN_2 = (1 << 16)
RETRO_MEMDESC_ALIGN_4 = (2 << 16)
RETRO_MEMDESC_ALIGN_8 = (3 << 16)
RETRO_MEMDESC_MINSIZE_2 = (1 << 24)
RETRO_MEMDESC_MINSIZE_4 = (2 << 24)
RETRO_MEMDESC_MINSIZE_8 = (3 << 24)
RETRO_SIMD_SSE = (1 << 0)
RETRO_SIMD_SSE2 = (1 << 1)
RETRO_SIMD_VMX = (1 << 2)
RETRO_SIMD_VMX128 = (1 << 3)
RETRO_SIMD_AVX = (1 << 4)
RETRO_SIMD_NEON = (1 << 5)
RETRO_SIMD_SSE3 = (1 << 6)
RETRO_SIMD_SSSE3 = (1 << 7)
RETRO_SIMD_MMX = (1 << 8)
RETRO_SIMD_MMXEXT = (1 << 9)
RETRO_SIMD_SSE4 = (1 << 10)
RETRO_SIMD_SSE42 = (1 << 11)
RETRO_SIMD_AVX2 = (1 << 12)
RETRO_SIMD_VFPU = (1 << 13)
RETRO_SIMD_PS = (1 << 14)
RETRO_SIMD_AES = (1 << 15)
RETRO_SIMD_VFPV3 = (1 << 16)
RETRO_SIMD_VFPV4 = (1 << 17)
RETRO_SIMD_POPCNT = (1 << 18)
RETRO_SIMD_MOVBE = (1 << 19)
RETRO_SIMD_CMOV = (1 << 20)
RETRO_SIMD_ASIMD = (1 << 21)
RETRO_SENSOR_ACCELEROMETER_X = 0
RETRO_SENSOR_ACCELEROMETER_Y = 1
RETRO_SENSOR_ACCELEROMETER_Z = 2
RETRO_SENSOR_GYROSCOPE_X = 3
RETRO_SENSOR_GYROSCOPE_Y = 4
RETRO_SENSOR_GYROSCOPE_Z = 5
RETRO_SENSOR_ILLUMINANCE = 6
RETRO_HW_FRAME_BUFFER_VALID = cast((-1), c_void_p)
RETRO_NETPACKET_UNRELIABLE = 0
RETRO_NETPACKET_RELIABLE = (1 << 0)
RETRO_NETPACKET_UNSEQUENCED = (1 << 1)
RETRO_NUM_CORE_OPTION_VALUES_MAX = 128
RETRO_MEMORY_ACCESS_WRITE = (1 << 0)
RETRO_MEMORY_ACCESS_READ = (1 << 1)
RETRO_MEMORY_TYPE_CACHED = (1 << 0)
RETRO_THROTTLE_NONE = 0
RETRO_THROTTLE_FRAME_STEPPING = 1
RETRO_THROTTLE_FAST_FORWARD = 2
RETRO_THROTTLE_SLOW_MOTION = 3
RETRO_THROTTLE_REWINDING = 4
RETRO_THROTTLE_VSYNC = 5
RETRO_THROTTLE_UNBLOCKED = 6
RETRO_MICROPHONE_INTERFACE_VERSION = 1
RETRO_POWERSTATE_NO_ESTIMATE = (-1)


class PowerState(enum.IntEnum):
    UNKNOWN = RETRO_POWERSTATE_UNKNOWN
    DISCHARGING = RETRO_POWERSTATE_DISCHARGING
    CHARGING = RETRO_POWERSTATE_CHARGING
    CHARGED = RETRO_POWERSTATE_CHARGED
    PLUGGED_IN = RETRO_POWERSTATE_PLUGGED_IN

    def __init__(self, value: int):
        self._type_ = 'I'
