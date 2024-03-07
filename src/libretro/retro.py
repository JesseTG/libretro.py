__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import enum
import sys
from ctypes import *  # noqa: F401, F403

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

# End preamble

_libs = {}

import ctypes
import ctypes.util

enum_retro_language = c_int

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
    English = RETRO_LANGUAGE_ENGLISH
    Japanese = RETRO_LANGUAGE_JAPANESE
    French = RETRO_LANGUAGE_FRENCH
    Spanish = RETRO_LANGUAGE_SPANISH
    German = RETRO_LANGUAGE_GERMAN
    Italian = RETRO_LANGUAGE_ITALIAN
    Dutch = RETRO_LANGUAGE_DUTCH
    PortugueseBrazil = RETRO_LANGUAGE_PORTUGUESE_BRAZIL
    PortuguesePortugal = RETRO_LANGUAGE_PORTUGUESE_PORTUGAL
    Russian = RETRO_LANGUAGE_RUSSIAN
    Korean = RETRO_LANGUAGE_KOREAN
    ChineseTraditional = RETRO_LANGUAGE_CHINESE_TRADITIONAL
    ChineseSimplified = RETRO_LANGUAGE_CHINESE_SIMPLIFIED
    Esperanto = RETRO_LANGUAGE_ESPERANTO
    Polish = RETRO_LANGUAGE_POLISH
    Vietnamese = RETRO_LANGUAGE_VIETNAMESE
    Arabic = RETRO_LANGUAGE_ARABIC
    Greek = RETRO_LANGUAGE_GREEK
    Turkish = RETRO_LANGUAGE_TURKISH
    Slovak = RETRO_LANGUAGE_SLOVAK
    Persian = RETRO_LANGUAGE_PERSIAN
    Hebrew = RETRO_LANGUAGE_HEBREW
    Asturian = RETRO_LANGUAGE_ASTURIAN
    Finnish = RETRO_LANGUAGE_FINNISH
    Indonesian = RETRO_LANGUAGE_INDONESIAN
    Swedish = RETRO_LANGUAGE_SWEDISH
    Ukrainian = RETRO_LANGUAGE_UKRAINIAN
    Czech = RETRO_LANGUAGE_CZECH
    CatalanValencia = RETRO_LANGUAGE_CATALAN_VALENCIA
    Catalan = RETRO_LANGUAGE_CATALAN
    BritishEnglish = RETRO_LANGUAGE_BRITISH_ENGLISH
    Hungarian = RETRO_LANGUAGE_HUNGARIAN
    Belarusian = RETRO_LANGUAGE_BELARUSIAN
    Last = Belarusian

enum_retro_key = c_int

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

enum_retro_mod = c_int

RETROKMOD_NONE = 0x0000
RETROKMOD_SHIFT = 0x01
RETROKMOD_CTRL = 0x02
RETROKMOD_ALT = 0x04
RETROKMOD_META = 0x08
RETROKMOD_NUMLOCK = 0x10
RETROKMOD_CAPSLOCK = 0x20
RETROKMOD_SCROLLOCK = 0x40
RETROKMOD_DUMMY = 0x7fffffff

class struct_retro_vfs_file_handle(Structure):
    pass

class struct_retro_vfs_dir_handle(Structure):
    pass

retro_vfs_get_path_t = CFUNCTYPE(UNCHECKED(c_char_p), POINTER(struct_retro_vfs_file_handle))

retro_vfs_open_t = CFUNCTYPE(UNCHECKED(POINTER(struct_retro_vfs_file_handle)), String, c_uint, c_uint)

retro_vfs_close_t = CFUNCTYPE(UNCHECKED(c_int), POINTER(struct_retro_vfs_file_handle))

retro_vfs_size_t = CFUNCTYPE(UNCHECKED(c_int64), POINTER(struct_retro_vfs_file_handle))

retro_vfs_truncate_t = CFUNCTYPE(UNCHECKED(c_int64), POINTER(struct_retro_vfs_file_handle), c_int64)

retro_vfs_tell_t = CFUNCTYPE(UNCHECKED(c_int64), POINTER(struct_retro_vfs_file_handle))

retro_vfs_seek_t = CFUNCTYPE(UNCHECKED(c_int64), POINTER(struct_retro_vfs_file_handle), c_int64, c_int)

retro_vfs_read_t = CFUNCTYPE(UNCHECKED(c_int64), POINTER(struct_retro_vfs_file_handle), POINTER(None), c_uint64)

retro_vfs_write_t = CFUNCTYPE(UNCHECKED(c_int64), POINTER(struct_retro_vfs_file_handle), POINTER(None), c_uint64)

retro_vfs_flush_t = CFUNCTYPE(UNCHECKED(c_int), POINTER(struct_retro_vfs_file_handle))

retro_vfs_remove_t = CFUNCTYPE(UNCHECKED(c_int), String)

retro_vfs_rename_t = CFUNCTYPE(UNCHECKED(c_int), String, String)

retro_vfs_stat_t = CFUNCTYPE(UNCHECKED(c_int), String, POINTER(c_int32))

retro_vfs_mkdir_t = CFUNCTYPE(UNCHECKED(c_int), String)

retro_vfs_opendir_t = CFUNCTYPE(UNCHECKED(POINTER(struct_retro_vfs_dir_handle)), String, c_bool)

retro_vfs_readdir_t = CFUNCTYPE(UNCHECKED(c_bool), POINTER(struct_retro_vfs_dir_handle))

retro_vfs_dirent_get_name_t = CFUNCTYPE(UNCHECKED(c_char_p), POINTER(struct_retro_vfs_dir_handle))

retro_vfs_dirent_is_dir_t = CFUNCTYPE(UNCHECKED(c_bool), POINTER(struct_retro_vfs_dir_handle))

retro_vfs_closedir_t = CFUNCTYPE(UNCHECKED(c_int), POINTER(struct_retro_vfs_dir_handle))

class struct_retro_vfs_interface(Structure):
    pass

struct_retro_vfs_interface.__slots__ = [
    'get_path',
    'open',
    'close',
    'size',
    'tell',
    'seek',
    'read',
    'write',
    'flush',
    'remove',
    'rename',
    'truncate',
    'stat',
    'mkdir',
    'opendir',
    'readdir',
    'dirent_get_name',
    'dirent_is_dir',
    'closedir',
]
struct_retro_vfs_interface._fields_ = [
    ('get_path', retro_vfs_get_path_t),
    ('open', retro_vfs_open_t),
    ('close', retro_vfs_close_t),
    ('size', retro_vfs_size_t),
    ('tell', retro_vfs_tell_t),
    ('seek', retro_vfs_seek_t),
    ('read', retro_vfs_read_t),
    ('write', retro_vfs_write_t),
    ('flush', retro_vfs_flush_t),
    ('remove', retro_vfs_remove_t),
    ('rename', retro_vfs_rename_t),
    ('truncate', retro_vfs_truncate_t),
    ('stat', retro_vfs_stat_t),
    ('mkdir', retro_vfs_mkdir_t),
    ('opendir', retro_vfs_opendir_t),
    ('readdir', retro_vfs_readdir_t),
    ('dirent_get_name', retro_vfs_dirent_get_name_t),
    ('dirent_is_dir', retro_vfs_dirent_is_dir_t),
    ('closedir', retro_vfs_closedir_t),
]

class struct_retro_vfs_interface_info(Structure):
    pass

struct_retro_vfs_interface_info.__slots__ = [
    'required_interface_version',
    'iface',
]
struct_retro_vfs_interface_info._fields_ = [
    ('required_interface_version', c_uint32),
    ('iface', POINTER(struct_retro_vfs_interface)),
]

enum_retro_hw_render_interface_type = c_int

RETRO_HW_RENDER_INTERFACE_VULKAN = 0

RETRO_HW_RENDER_INTERFACE_D3D9 = 1

RETRO_HW_RENDER_INTERFACE_D3D10 = 2

RETRO_HW_RENDER_INTERFACE_D3D11 = 3

RETRO_HW_RENDER_INTERFACE_D3D12 = 4

RETRO_HW_RENDER_INTERFACE_GSKIT_PS2 = 5

RETRO_HW_RENDER_INTERFACE_DUMMY = 0x7fffffff

class struct_retro_hw_render_interface(Structure):
    pass

struct_retro_hw_render_interface.__slots__ = [
    'interface_type',
    'interface_version',
]
struct_retro_hw_render_interface._fields_ = [
    ('interface_type', enum_retro_hw_render_interface_type),
    ('interface_version', c_uint),
]

retro_set_led_state_t = CFUNCTYPE(UNCHECKED(None), c_int, c_int)

class struct_retro_led_interface(Structure):
    pass

struct_retro_led_interface.__slots__ = [
    'set_led_state',
]
struct_retro_led_interface._fields_ = [
    ('set_led_state', retro_set_led_state_t),
]

retro_midi_input_enabled_t = CFUNCTYPE(UNCHECKED(c_bool), )

retro_midi_output_enabled_t = CFUNCTYPE(UNCHECKED(c_bool), )

retro_midi_read_t = CFUNCTYPE(UNCHECKED(c_bool), POINTER(c_uint8))

retro_midi_write_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint8, c_uint32)

retro_midi_flush_t = CFUNCTYPE(UNCHECKED(c_bool), )

class struct_retro_midi_interface(Structure):
    pass

struct_retro_midi_interface.__slots__ = [
    'input_enabled',
    'output_enabled',
    'read',
    'write',
    'flush',
]
struct_retro_midi_interface._fields_ = [
    ('input_enabled', retro_midi_input_enabled_t),
    ('output_enabled', retro_midi_output_enabled_t),
    ('read', retro_midi_read_t),
    ('write', retro_midi_write_t),
    ('flush', retro_midi_flush_t),
]

enum_retro_hw_render_context_negotiation_interface_type = c_int

RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_VULKAN = 0

RETRO_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_DUMMY = 0x7fffffff

class struct_retro_hw_render_context_negotiation_interface(Structure):
    pass

struct_retro_hw_render_context_negotiation_interface.__slots__ = [
    'interface_type',
    'interface_version',
]
struct_retro_hw_render_context_negotiation_interface._fields_ = [
    ('interface_type', enum_retro_hw_render_context_negotiation_interface_type),
    ('interface_version', c_uint),
]

class struct_retro_memory_descriptor(Structure):
    pass

struct_retro_memory_descriptor.__slots__ = [
    'flags',
    'ptr',
    'offset',
    'start',
    'select',
    'disconnect',
    'len',
    'addrspace',
]
struct_retro_memory_descriptor._fields_ = [
    ('flags', c_uint64),
    ('ptr', POINTER(None)),
    ('offset', c_size_t),
    ('start', c_size_t),
    ('select', c_size_t),
    ('disconnect', c_size_t),
    ('len', c_size_t),
    ('addrspace', String),
]

class struct_retro_memory_map(Structure):
    pass

struct_retro_memory_map.__slots__ = [
    'descriptors',
    'num_descriptors',
]
struct_retro_memory_map._fields_ = [
    ('descriptors', POINTER(struct_retro_memory_descriptor)),
    ('num_descriptors', c_uint),
]

class struct_retro_controller_description(Structure):
    pass

struct_retro_controller_description.__slots__ = [
    'desc',
    'id',
]
struct_retro_controller_description._fields_ = [
    ('desc', String),
    ('id', c_uint),
]

class struct_retro_controller_info(Structure):
    pass

struct_retro_controller_info.__slots__ = [
    'types',
    'num_types',
]
struct_retro_controller_info._fields_ = [
    ('types', POINTER(struct_retro_controller_description)),
    ('num_types', c_uint),
]

class struct_retro_subsystem_memory_info(Structure):
    pass

struct_retro_subsystem_memory_info.__slots__ = [
    'extension',
    'type',
]
struct_retro_subsystem_memory_info._fields_ = [
    ('extension', String),
    ('type', c_uint),
]

class struct_retro_subsystem_rom_info(Structure):
    pass

struct_retro_subsystem_rom_info.__slots__ = [
    'desc',
    'valid_extensions',
    'need_fullpath',
    'block_extract',
    'required',
    'memory',
    'num_memory',
]
struct_retro_subsystem_rom_info._fields_ = [
    ('desc', String),
    ('valid_extensions', String),
    ('need_fullpath', c_bool),
    ('block_extract', c_bool),
    ('required', c_bool),
    ('memory', POINTER(struct_retro_subsystem_memory_info)),
    ('num_memory', c_uint),
]

class struct_retro_subsystem_info(Structure):
    pass

struct_retro_subsystem_info.__slots__ = [
    'desc',
    'ident',
    'roms',
    'num_roms',
    'id',
]
struct_retro_subsystem_info._fields_ = [
    ('desc', String),
    ('ident', String),
    ('roms', POINTER(struct_retro_subsystem_rom_info)),
    ('num_roms', c_uint),
    ('id', c_uint),
]

retro_proc_address_t = CFUNCTYPE(UNCHECKED(None), )

retro_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)

class struct_retro_get_proc_address_interface(Structure):
    pass

struct_retro_get_proc_address_interface.__slots__ = [
    'get_proc_address',
]
struct_retro_get_proc_address_interface._fields_ = [
    ('get_proc_address', retro_get_proc_address_t),
]

enum_retro_log_level = c_int

RETRO_LOG_DEBUG = 0

RETRO_LOG_INFO = (RETRO_LOG_DEBUG + 1)

RETRO_LOG_WARN = (RETRO_LOG_INFO + 1)

RETRO_LOG_ERROR = (RETRO_LOG_WARN + 1)

RETRO_LOG_DUMMY = 0x7fffffff

retro_log_printf_t = CFUNCTYPE(UNCHECKED(None), enum_retro_log_level, String)

class struct_retro_log_callback(Structure):
    pass

struct_retro_log_callback.__slots__ = [
    'log',
]
struct_retro_log_callback._fields_ = [
    ('log', retro_log_printf_t),
]

retro_perf_tick_t = c_uint64

retro_time_t = c_int64

class struct_retro_perf_counter(Structure):
    pass

struct_retro_perf_counter.__slots__ = [
    'ident',
    'start',
    'total',
    'call_cnt',
    'registered',
]
struct_retro_perf_counter._fields_ = [
    ('ident', String),
    ('start', retro_perf_tick_t),
    ('total', retro_perf_tick_t),
    ('call_cnt', retro_perf_tick_t),
    ('registered', c_bool),
]

retro_perf_get_time_usec_t = CFUNCTYPE(UNCHECKED(retro_time_t), )

retro_perf_get_counter_t = CFUNCTYPE(UNCHECKED(retro_perf_tick_t), )

retro_get_cpu_features_t = CFUNCTYPE(UNCHECKED(c_uint64), )

retro_perf_log_t = CFUNCTYPE(UNCHECKED(None), )

retro_perf_register_t = CFUNCTYPE(UNCHECKED(None), POINTER(struct_retro_perf_counter))

retro_perf_start_t = CFUNCTYPE(UNCHECKED(None), POINTER(struct_retro_perf_counter))

retro_perf_stop_t = CFUNCTYPE(UNCHECKED(None), POINTER(struct_retro_perf_counter))

class struct_retro_perf_callback(Structure):
    pass

struct_retro_perf_callback.__slots__ = [
    'get_time_usec',
    'get_cpu_features',
    'get_perf_counter',
    'perf_register',
    'perf_start',
    'perf_stop',
    'perf_log',
]
struct_retro_perf_callback._fields_ = [
    ('get_time_usec', retro_perf_get_time_usec_t),
    ('get_cpu_features', retro_get_cpu_features_t),
    ('get_perf_counter', retro_perf_get_counter_t),
    ('perf_register', retro_perf_register_t),
    ('perf_start', retro_perf_start_t),
    ('perf_stop', retro_perf_stop_t),
    ('perf_log', retro_perf_log_t),
]

enum_retro_sensor_action = c_int

RETRO_SENSOR_ACCELEROMETER_ENABLE = 0

RETRO_SENSOR_ACCELEROMETER_DISABLE = (RETRO_SENSOR_ACCELEROMETER_ENABLE + 1)

RETRO_SENSOR_GYROSCOPE_ENABLE = (RETRO_SENSOR_ACCELEROMETER_DISABLE + 1)

RETRO_SENSOR_GYROSCOPE_DISABLE = (RETRO_SENSOR_GYROSCOPE_ENABLE + 1)

RETRO_SENSOR_ILLUMINANCE_ENABLE = (RETRO_SENSOR_GYROSCOPE_DISABLE + 1)

RETRO_SENSOR_ILLUMINANCE_DISABLE = (RETRO_SENSOR_ILLUMINANCE_ENABLE + 1)

RETRO_SENSOR_DUMMY = 0x7fffffff

retro_set_sensor_state_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint, enum_retro_sensor_action, c_uint)

retro_sensor_get_input_t = CFUNCTYPE(UNCHECKED(c_float), c_uint, c_uint)

class struct_retro_sensor_interface(Structure):
    pass

struct_retro_sensor_interface.__slots__ = [
    'set_sensor_state',
    'get_sensor_input',
]
struct_retro_sensor_interface._fields_ = [
    ('set_sensor_state', retro_set_sensor_state_t),
    ('get_sensor_input', retro_sensor_get_input_t),
]

enum_retro_camera_buffer = c_int

RETRO_CAMERA_BUFFER_OPENGL_TEXTURE = 0

RETRO_CAMERA_BUFFER_RAW_FRAMEBUFFER = (RETRO_CAMERA_BUFFER_OPENGL_TEXTURE + 1)

RETRO_CAMERA_BUFFER_DUMMY = 0x7fffffff

retro_camera_start_t = CFUNCTYPE(UNCHECKED(c_bool), )

retro_camera_stop_t = CFUNCTYPE(UNCHECKED(None), )

retro_camera_lifetime_status_t = CFUNCTYPE(UNCHECKED(None), )

retro_camera_frame_raw_framebuffer_t = CFUNCTYPE(UNCHECKED(None), POINTER(c_uint32), c_uint, c_uint, c_size_t)

retro_camera_frame_opengl_texture_t = CFUNCTYPE(UNCHECKED(None), c_uint, c_uint, POINTER(c_float))

class struct_retro_camera_callback(Structure):
    pass

struct_retro_camera_callback.__slots__ = [
    'caps',
    'width',
    'height',
    'start',
    'stop',
    'frame_raw_framebuffer',
    'frame_opengl_texture',
    'initialized',
    'deinitialized',
]
struct_retro_camera_callback._fields_ = [
    ('caps', c_uint64),
    ('width', c_uint),
    ('height', c_uint),
    ('start', retro_camera_start_t),
    ('stop', retro_camera_stop_t),
    ('frame_raw_framebuffer', retro_camera_frame_raw_framebuffer_t),
    ('frame_opengl_texture', retro_camera_frame_opengl_texture_t),
    ('initialized', retro_camera_lifetime_status_t),
    ('deinitialized', retro_camera_lifetime_status_t),
]

retro_location_set_interval_t = CFUNCTYPE(UNCHECKED(None), c_uint, c_uint)

retro_location_start_t = CFUNCTYPE(UNCHECKED(c_bool), )

retro_location_stop_t = CFUNCTYPE(UNCHECKED(None), )

retro_location_get_position_t = CFUNCTYPE(UNCHECKED(c_bool), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double))

retro_location_lifetime_status_t = CFUNCTYPE(UNCHECKED(None), )

class struct_retro_location_callback(Structure):
    pass

struct_retro_location_callback.__slots__ = [
    'start',
    'stop',
    'get_position',
    'set_interval',
    'initialized',
    'deinitialized',
]
struct_retro_location_callback._fields_ = [
    ('start', retro_location_start_t),
    ('stop', retro_location_stop_t),
    ('get_position', retro_location_get_position_t),
    ('set_interval', retro_location_set_interval_t),
    ('initialized', retro_location_lifetime_status_t),
    ('deinitialized', retro_location_lifetime_status_t),
]

enum_retro_rumble_effect = c_int

RETRO_RUMBLE_STRONG = 0

RETRO_RUMBLE_WEAK = 1

RETRO_RUMBLE_DUMMY = 0x7fffffff

retro_set_rumble_state_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint, enum_retro_rumble_effect, c_uint16)

class struct_retro_rumble_interface(Structure):
    pass

struct_retro_rumble_interface.__slots__ = [
    'set_rumble_state',
]
struct_retro_rumble_interface._fields_ = [
    ('set_rumble_state', retro_set_rumble_state_t),
]

retro_audio_callback_t = CFUNCTYPE(UNCHECKED(None), )

retro_audio_set_state_callback_t = CFUNCTYPE(UNCHECKED(None), c_bool)

class struct_retro_audio_callback(Structure):
    pass

struct_retro_audio_callback.__slots__ = [
    'callback',
    'set_state',
]
struct_retro_audio_callback._fields_ = [
    ('callback', retro_audio_callback_t),
    ('set_state', retro_audio_set_state_callback_t),
]

retro_usec_t = c_int64

retro_frame_time_callback_t = CFUNCTYPE(UNCHECKED(None), retro_usec_t)

class struct_retro_frame_time_callback(Structure):
    pass

struct_retro_frame_time_callback.__slots__ = [
    'callback',
    'reference',
]
struct_retro_frame_time_callback._fields_ = [
    ('callback', retro_frame_time_callback_t),
    ('reference', retro_usec_t),
]

retro_audio_buffer_status_callback_t = CFUNCTYPE(UNCHECKED(None), c_bool, c_uint, c_bool)

class struct_retro_audio_buffer_status_callback(Structure):
    pass

struct_retro_audio_buffer_status_callback.__slots__ = [
    'callback',
]
struct_retro_audio_buffer_status_callback._fields_ = [
    ('callback', retro_audio_buffer_status_callback_t),
]

retro_hw_context_reset_t = CFUNCTYPE(UNCHECKED(None), )

retro_hw_get_current_framebuffer_t = CFUNCTYPE(UNCHECKED(c_uintptr), )

retro_hw_get_proc_address_t = CFUNCTYPE(UNCHECKED(retro_proc_address_t), String)

enum_retro_hw_context_type = c_int

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

class struct_retro_hw_render_callback(Structure):
    pass

struct_retro_hw_render_callback.__slots__ = [
    'context_type',
    'context_reset',
    'get_current_framebuffer',
    'get_proc_address',
    'depth',
    'stencil',
    'bottom_left_origin',
    'version_major',
    'version_minor',
    'cache_context',
    'context_destroy',
    'debug_context',
]
struct_retro_hw_render_callback._fields_ = [
    ('context_type', enum_retro_hw_context_type),
    ('context_reset', retro_hw_context_reset_t),
    ('get_current_framebuffer', retro_hw_get_current_framebuffer_t),
    ('get_proc_address', retro_hw_get_proc_address_t),
    ('depth', c_bool),
    ('stencil', c_bool),
    ('bottom_left_origin', c_bool),
    ('version_major', c_uint),
    ('version_minor', c_uint),
    ('cache_context', c_bool),
    ('context_destroy', retro_hw_context_reset_t),
    ('debug_context', c_bool),
]

retro_keyboard_event_t = CFUNCTYPE(UNCHECKED(None), c_bool, c_uint, c_uint32, c_uint16)

class struct_retro_keyboard_callback(Structure):
    pass

struct_retro_keyboard_callback.__slots__ = [
    'callback',
]
struct_retro_keyboard_callback._fields_ = [
    ('callback', retro_keyboard_event_t),
]

retro_set_eject_state_t = CFUNCTYPE(UNCHECKED(c_bool), c_bool)

retro_get_eject_state_t = CFUNCTYPE(UNCHECKED(c_bool), )

retro_get_image_index_t = CFUNCTYPE(UNCHECKED(c_uint), )

retro_set_image_index_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint)

retro_get_num_images_t = CFUNCTYPE(UNCHECKED(c_uint), )

class struct_retro_game_info(Structure):
    pass

retro_replace_image_index_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint, POINTER(struct_retro_game_info))

retro_add_image_index_t = CFUNCTYPE(UNCHECKED(c_bool), )

retro_set_initial_image_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint, String)

retro_get_image_path_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint, String, c_size_t)

retro_get_image_label_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint, String, c_size_t)

class struct_retro_disk_control_callback(Structure):
    pass

struct_retro_disk_control_callback.__slots__ = [
    'set_eject_state',
    'get_eject_state',
    'get_image_index',
    'set_image_index',
    'get_num_images',
    'replace_image_index',
    'add_image_index',
]
struct_retro_disk_control_callback._fields_ = [
    ('set_eject_state', retro_set_eject_state_t),
    ('get_eject_state', retro_get_eject_state_t),
    ('get_image_index', retro_get_image_index_t),
    ('set_image_index', retro_set_image_index_t),
    ('get_num_images', retro_get_num_images_t),
    ('replace_image_index', retro_replace_image_index_t),
    ('add_image_index', retro_add_image_index_t),
]

class struct_retro_disk_control_ext_callback(Structure):
    pass

struct_retro_disk_control_ext_callback.__slots__ = [
    'set_eject_state',
    'get_eject_state',
    'get_image_index',
    'set_image_index',
    'get_num_images',
    'replace_image_index',
    'add_image_index',
    'set_initial_image',
    'get_image_path',
    'get_image_label',
]
struct_retro_disk_control_ext_callback._fields_ = [
    ('set_eject_state', retro_set_eject_state_t),
    ('get_eject_state', retro_get_eject_state_t),
    ('get_image_index', retro_get_image_index_t),
    ('set_image_index', retro_set_image_index_t),
    ('get_num_images', retro_get_num_images_t),
    ('replace_image_index', retro_replace_image_index_t),
    ('add_image_index', retro_add_image_index_t),
    ('set_initial_image', retro_set_initial_image_t),
    ('get_image_path', retro_get_image_path_t),
    ('get_image_label', retro_get_image_label_t),
]

retro_netpacket_send_t = CFUNCTYPE(UNCHECKED(None), c_int, POINTER(None), c_size_t, c_uint16, c_bool)

retro_netpacket_start_t = CFUNCTYPE(UNCHECKED(None), c_uint16, retro_netpacket_send_t)

retro_netpacket_receive_t = CFUNCTYPE(UNCHECKED(None), POINTER(None), c_size_t, c_uint16)

retro_netpacket_stop_t = CFUNCTYPE(UNCHECKED(None), )

retro_netpacket_poll_t = CFUNCTYPE(UNCHECKED(None), )

retro_netpacket_connected_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint16)

retro_netpacket_disconnected_t = CFUNCTYPE(UNCHECKED(None), c_uint16)

class struct_retro_netpacket_callback(Structure):
    pass

struct_retro_netpacket_callback.__slots__ = [
    'start',
    'receive',
    'stop',
    'poll',
    'connected',
    'disconnected',
]
struct_retro_netpacket_callback._fields_ = [
    ('start', retro_netpacket_start_t),
    ('receive', retro_netpacket_receive_t),
    ('stop', retro_netpacket_stop_t),
    ('poll', retro_netpacket_poll_t),
    ('connected', retro_netpacket_connected_t),
    ('disconnected', retro_netpacket_disconnected_t),
]

enum_retro_pixel_format = c_int

RETRO_PIXEL_FORMAT_0RGB1555 = 0

RETRO_PIXEL_FORMAT_XRGB8888 = 1

RETRO_PIXEL_FORMAT_RGB565 = 2

RETRO_PIXEL_FORMAT_UNKNOWN = 0x7fffffff

enum_retro_savestate_context = c_int

RETRO_SAVESTATE_CONTEXT_NORMAL = 0

RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_INSTANCE = 1

RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_BINARY = 2

RETRO_SAVESTATE_CONTEXT_ROLLBACK_NETPLAY = 3

RETRO_SAVESTATE_CONTEXT_UNKNOWN = 0x7fffffff

class struct_retro_message(Structure):
    pass

struct_retro_message.__slots__ = [
    'msg',
    'frames',
]
struct_retro_message._fields_ = [
    ('msg', String),
    ('frames', c_uint),
]

enum_retro_message_target = c_int

RETRO_MESSAGE_TARGET_ALL = 0

RETRO_MESSAGE_TARGET_OSD = (RETRO_MESSAGE_TARGET_ALL + 1)

RETRO_MESSAGE_TARGET_LOG = (RETRO_MESSAGE_TARGET_OSD + 1)

enum_retro_message_type = c_int

RETRO_MESSAGE_TYPE_NOTIFICATION = 0

RETRO_MESSAGE_TYPE_NOTIFICATION_ALT = (RETRO_MESSAGE_TYPE_NOTIFICATION + 1)

RETRO_MESSAGE_TYPE_STATUS = (RETRO_MESSAGE_TYPE_NOTIFICATION_ALT + 1)

RETRO_MESSAGE_TYPE_PROGRESS = (RETRO_MESSAGE_TYPE_STATUS + 1)

class struct_retro_message_ext(Structure):
    pass

struct_retro_message_ext.__slots__ = [
    'msg',
    'duration',
    'priority',
    'level',
    'target',
    'type',
    'progress',
]
struct_retro_message_ext._fields_ = [
    ('msg', String),
    ('duration', c_uint),
    ('priority', c_uint),
    ('level', enum_retro_log_level),
    ('target', enum_retro_message_target),
    ('type', enum_retro_message_type),
    ('progress', c_int8),
]

class struct_retro_input_descriptor(Structure):
    pass

struct_retro_input_descriptor.__slots__ = [
    'port',
    'device',
    'index',
    'id',
    'description',
]
struct_retro_input_descriptor._fields_ = [
    ('port', c_uint),
    ('device', c_uint),
    ('index', c_uint),
    ('id', c_uint),
    ('description', String),
]

class struct_retro_system_info(Structure):
    pass

struct_retro_system_info.__slots__ = [
    'library_name',
    'library_version',
    'valid_extensions',
    'need_fullpath',
    'block_extract',
]
struct_retro_system_info._fields_ = [
    ('library_name', String),
    ('library_version', String),
    ('valid_extensions', String),
    ('need_fullpath', c_bool),
    ('block_extract', c_bool),
]

class struct_retro_system_content_info_override(Structure):
    pass

struct_retro_system_content_info_override.__slots__ = [
    'extensions',
    'need_fullpath',
    'persistent_data',
]
struct_retro_system_content_info_override._fields_ = [
    ('extensions', String),
    ('need_fullpath', c_bool),
    ('persistent_data', c_bool),
]

class struct_retro_game_info_ext(Structure):
    pass

struct_retro_game_info_ext.__slots__ = [
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
struct_retro_game_info_ext._fields_ = [
    ('full_path', String),
    ('archive_path', String),
    ('archive_file', String),
    ('dir', String),
    ('name', String),
    ('ext', String),
    ('meta', String),
    ('data', POINTER(None)),
    ('size', c_size_t),
    ('file_in_archive', c_bool),
    ('persistent_data', c_bool),
]

class struct_retro_game_geometry(Structure):
    pass

struct_retro_game_geometry.__slots__ = [
    'base_width',
    'base_height',
    'max_width',
    'max_height',
    'aspect_ratio',
]
struct_retro_game_geometry._fields_ = [
    ('base_width', c_uint),
    ('base_height', c_uint),
    ('max_width', c_uint),
    ('max_height', c_uint),
    ('aspect_ratio', c_float),
]

class struct_retro_system_timing(Structure):
    pass

struct_retro_system_timing.__slots__ = [
    'fps',
    'sample_rate',
]
struct_retro_system_timing._fields_ = [
    ('fps', c_double),
    ('sample_rate', c_double),
]

class struct_retro_system_av_info(Structure):
    pass

struct_retro_system_av_info.__slots__ = [
    'geometry',
    'timing',
]
struct_retro_system_av_info._fields_ = [
    ('geometry', struct_retro_game_geometry),
    ('timing', struct_retro_system_timing),
]

class struct_retro_variable(Structure):
    pass

struct_retro_variable.__slots__ = [
    'key',
    'value',
]
struct_retro_variable._fields_ = [
    ('key', String),
    ('value', String),
]

class struct_retro_core_option_display(Structure):
    pass

struct_retro_core_option_display.__slots__ = [
    'key',
    'visible',
]
struct_retro_core_option_display._fields_ = [
    ('key', String),
    ('visible', c_bool),
]

class struct_retro_core_option_value(Structure):
    pass

struct_retro_core_option_value.__slots__ = [
    'value',
    'label',
]
struct_retro_core_option_value._fields_ = [
    ('value', String),
    ('label', String),
]

class struct_retro_core_option_definition(Structure):
    pass

struct_retro_core_option_definition.__slots__ = [
    'key',
    'desc',
    'info',
    'values',
    'default_value',
]
struct_retro_core_option_definition._fields_ = [
    ('key', String),
    ('desc', String),
    ('info', String),
    ('values', struct_retro_core_option_value * int(128)),
    ('default_value', String),
]

class struct_retro_core_options_intl(Structure):
    pass

struct_retro_core_options_intl.__slots__ = [
    'us',
    'local',
]
struct_retro_core_options_intl._fields_ = [
    ('us', POINTER(struct_retro_core_option_definition)),
    ('local', POINTER(struct_retro_core_option_definition)),
]

class struct_retro_core_option_v2_category(Structure):
    pass

struct_retro_core_option_v2_category.__slots__ = [
    'key',
    'desc',
    'info',
]
struct_retro_core_option_v2_category._fields_ = [
    ('key', String),
    ('desc', String),
    ('info', String),
]

class struct_retro_core_option_v2_definition(Structure):
    pass

struct_retro_core_option_v2_definition.__slots__ = [
    'key',
    'desc',
    'desc_categorized',
    'info',
    'info_categorized',
    'category_key',
    'values',
    'default_value',
]
struct_retro_core_option_v2_definition._fields_ = [
    ('key', String),
    ('desc', String),
    ('desc_categorized', String),
    ('info', String),
    ('info_categorized', String),
    ('category_key', String),
    ('values', struct_retro_core_option_value * int(128)),
    ('default_value', String),
]

class struct_retro_core_options_v2(Structure):
    pass

struct_retro_core_options_v2.__slots__ = [
    'categories',
    'definitions',
]
struct_retro_core_options_v2._fields_ = [
    ('categories', POINTER(struct_retro_core_option_v2_category)),
    ('definitions', POINTER(struct_retro_core_option_v2_definition)),
]

class struct_retro_core_options_v2_intl(Structure):
    pass

struct_retro_core_options_v2_intl.__slots__ = [
    'us',
    'local',
]
struct_retro_core_options_v2_intl._fields_ = [
    ('us', POINTER(struct_retro_core_options_v2)),
    ('local', POINTER(struct_retro_core_options_v2)),
]

retro_core_options_update_display_callback_t = CFUNCTYPE(UNCHECKED(c_bool), )

class struct_retro_core_options_update_display_callback(Structure):
    pass

struct_retro_core_options_update_display_callback.__slots__ = [
    'callback',
]
struct_retro_core_options_update_display_callback._fields_ = [
    ('callback', retro_core_options_update_display_callback_t),
]

struct_retro_game_info.__slots__ = [
    'path',
    'data',
    'size',
    'meta',
]
struct_retro_game_info._fields_ = [
    ('path', String),
    ('data', POINTER(None)),
    ('size', c_size_t),
    ('meta', String),
]

class struct_retro_framebuffer(Structure):
    pass

struct_retro_framebuffer.__slots__ = [
    'data',
    'width',
    'height',
    'pitch',
    'format',
    'access_flags',
    'memory_flags',
]
struct_retro_framebuffer._fields_ = [
    ('data', POINTER(None)),
    ('width', c_uint),
    ('height', c_uint),
    ('pitch', c_size_t),
    ('format', enum_retro_pixel_format),
    ('access_flags', c_uint),
    ('memory_flags', c_uint),
]

class struct_retro_fastforwarding_override(Structure):
    pass

struct_retro_fastforwarding_override.__slots__ = [
    'ratio',
    'fastforward',
    'notification',
    'inhibit_toggle',
]
struct_retro_fastforwarding_override._fields_ = [
    ('ratio', c_float),
    ('fastforward', c_bool),
    ('notification', c_bool),
    ('inhibit_toggle', c_bool),
]

class struct_retro_throttle_state(Structure):
    pass

struct_retro_throttle_state.__slots__ = [
    'mode',
    'rate',
]
struct_retro_throttle_state._fields_ = [
    ('mode', c_uint),
    ('rate', c_float),
]

class struct_retro_microphone(Structure):
    pass

retro_microphone_t = struct_retro_microphone

class struct_retro_microphone_params(Structure):
    pass

struct_retro_microphone_params.__slots__ = [
    'rate',
]
struct_retro_microphone_params._fields_ = [
    ('rate', c_uint),
]

retro_microphone_params_t = struct_retro_microphone_params

retro_open_mic_t = CFUNCTYPE(UNCHECKED(POINTER(retro_microphone_t)), POINTER(retro_microphone_params_t))

retro_close_mic_t = CFUNCTYPE(UNCHECKED(None), POINTER(retro_microphone_t))

retro_get_mic_params_t = CFUNCTYPE(UNCHECKED(c_bool), POINTER(retro_microphone_t), POINTER(retro_microphone_params_t))

retro_set_mic_state_t = CFUNCTYPE(UNCHECKED(c_bool), POINTER(retro_microphone_t), c_bool)

retro_get_mic_state_t = CFUNCTYPE(UNCHECKED(c_bool), POINTER(retro_microphone_t))

retro_read_mic_t = CFUNCTYPE(UNCHECKED(c_int), POINTER(retro_microphone_t), POINTER(c_int16), c_size_t)

class struct_retro_microphone_interface(Structure):
    pass

struct_retro_microphone_interface.__slots__ = [
    'interface_version',
    'open_mic',
    'close_mic',
    'get_params',
    'set_mic_state',
    'get_mic_state',
    'read_mic',
]
struct_retro_microphone_interface._fields_ = [
    ('interface_version', c_uint),
    ('open_mic', retro_open_mic_t),
    ('close_mic', retro_close_mic_t),
    ('get_params', retro_get_mic_params_t),
    ('set_mic_state', retro_set_mic_state_t),
    ('get_mic_state', retro_get_mic_state_t),
    ('read_mic', retro_read_mic_t),
]

enum_retro_power_state = c_int

RETRO_POWERSTATE_UNKNOWN = 0

RETRO_POWERSTATE_DISCHARGING = (RETRO_POWERSTATE_UNKNOWN + 1)

RETRO_POWERSTATE_CHARGING = (RETRO_POWERSTATE_DISCHARGING + 1)

RETRO_POWERSTATE_CHARGED = (RETRO_POWERSTATE_CHARGING + 1)

RETRO_POWERSTATE_PLUGGED_IN = (RETRO_POWERSTATE_CHARGED + 1)

class struct_retro_device_power(Structure):
    pass

struct_retro_device_power.__slots__ = [
    'state',
    'seconds',
    'percent',
]
struct_retro_device_power._fields_ = [
    ('state', enum_retro_power_state),
    ('seconds', c_int),
    ('percent', c_int8),
]

retro_environment_t = CFUNCTYPE(UNCHECKED(c_bool), c_uint, POINTER(None))

retro_video_refresh_t = CFUNCTYPE(UNCHECKED(None), POINTER(None), c_uint, c_uint, c_size_t)

retro_audio_sample_t = CFUNCTYPE(UNCHECKED(None), c_int16, c_int16)

retro_audio_sample_batch_t = CFUNCTYPE(UNCHECKED(c_size_t), POINTER(c_int16), c_size_t)

retro_input_poll_t = CFUNCTYPE(UNCHECKED(None), )

retro_input_state_t = CFUNCTYPE(UNCHECKED(c_int16), c_uint, c_uint, c_uint, c_uint)

for _lib in _libs.values():
    if not _lib.has("retro_set_environment", "cdecl"):
        continue
    retro_set_environment = _lib.get("retro_set_environment", "cdecl")
    retro_set_environment.argtypes = [retro_environment_t]
    retro_set_environment.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_set_video_refresh", "cdecl"):
        continue
    retro_set_video_refresh = _lib.get("retro_set_video_refresh", "cdecl")
    retro_set_video_refresh.argtypes = [retro_video_refresh_t]
    retro_set_video_refresh.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_set_audio_sample", "cdecl"):
        continue
    retro_set_audio_sample = _lib.get("retro_set_audio_sample", "cdecl")
    retro_set_audio_sample.argtypes = [retro_audio_sample_t]
    retro_set_audio_sample.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_set_audio_sample_batch", "cdecl"):
        continue
    retro_set_audio_sample_batch = _lib.get("retro_set_audio_sample_batch", "cdecl")
    retro_set_audio_sample_batch.argtypes = [retro_audio_sample_batch_t]
    retro_set_audio_sample_batch.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_set_input_poll", "cdecl"):
        continue
    retro_set_input_poll = _lib.get("retro_set_input_poll", "cdecl")
    retro_set_input_poll.argtypes = [retro_input_poll_t]
    retro_set_input_poll.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_set_input_state", "cdecl"):
        continue
    retro_set_input_state = _lib.get("retro_set_input_state", "cdecl")
    retro_set_input_state.argtypes = [retro_input_state_t]
    retro_set_input_state.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_init", "cdecl"):
        continue
    retro_init = _lib.get("retro_init", "cdecl")
    retro_init.argtypes = []
    retro_init.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_deinit", "cdecl"):
        continue
    retro_deinit = _lib.get("retro_deinit", "cdecl")
    retro_deinit.argtypes = []
    retro_deinit.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_api_version", "cdecl"):
        continue
    retro_api_version = _lib.get("retro_api_version", "cdecl")
    retro_api_version.argtypes = []
    retro_api_version.restype = c_uint
    break

for _lib in _libs.values():
    if not _lib.has("retro_get_system_info", "cdecl"):
        continue
    retro_get_system_info = _lib.get("retro_get_system_info", "cdecl")
    retro_get_system_info.argtypes = [POINTER(struct_retro_system_info)]
    retro_get_system_info.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_get_system_av_info", "cdecl"):
        continue
    retro_get_system_av_info = _lib.get("retro_get_system_av_info", "cdecl")
    retro_get_system_av_info.argtypes = [POINTER(struct_retro_system_av_info)]
    retro_get_system_av_info.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_set_controller_port_device", "cdecl"):
        continue
    retro_set_controller_port_device = _lib.get("retro_set_controller_port_device", "cdecl")
    retro_set_controller_port_device.argtypes = [c_uint, c_uint]
    retro_set_controller_port_device.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_reset", "cdecl"):
        continue
    retro_reset = _lib.get("retro_reset", "cdecl")
    retro_reset.argtypes = []
    retro_reset.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_run", "cdecl"):
        continue
    retro_run = _lib.get("retro_run", "cdecl")
    retro_run.argtypes = []
    retro_run.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_serialize_size", "cdecl"):
        continue
    retro_serialize_size = _lib.get("retro_serialize_size", "cdecl")
    retro_serialize_size.argtypes = []
    retro_serialize_size.restype = c_size_t
    break

for _lib in _libs.values():
    if not _lib.has("retro_serialize", "cdecl"):
        continue
    retro_serialize = _lib.get("retro_serialize", "cdecl")
    retro_serialize.argtypes = [POINTER(None), c_size_t]
    retro_serialize.restype = c_bool
    break

for _lib in _libs.values():
    if not _lib.has("retro_unserialize", "cdecl"):
        continue
    retro_unserialize = _lib.get("retro_unserialize", "cdecl")
    retro_unserialize.argtypes = [POINTER(None), c_size_t]
    retro_unserialize.restype = c_bool
    break

for _lib in _libs.values():
    if not _lib.has("retro_cheat_reset", "cdecl"):
        continue
    retro_cheat_reset = _lib.get("retro_cheat_reset", "cdecl")
    retro_cheat_reset.argtypes = []
    retro_cheat_reset.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_cheat_set", "cdecl"):
        continue
    retro_cheat_set = _lib.get("retro_cheat_set", "cdecl")
    retro_cheat_set.argtypes = [c_uint, c_bool, String]
    retro_cheat_set.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_load_game", "cdecl"):
        continue
    retro_load_game = _lib.get("retro_load_game", "cdecl")
    retro_load_game.argtypes = [POINTER(struct_retro_game_info)]
    retro_load_game.restype = c_bool
    break

for _lib in _libs.values():
    if not _lib.has("retro_load_game_special", "cdecl"):
        continue
    retro_load_game_special = _lib.get("retro_load_game_special", "cdecl")
    retro_load_game_special.argtypes = [c_uint, POINTER(struct_retro_game_info), c_size_t]
    retro_load_game_special.restype = c_bool
    break

for _lib in _libs.values():
    if not _lib.has("retro_unload_game", "cdecl"):
        continue
    retro_unload_game = _lib.get("retro_unload_game", "cdecl")
    retro_unload_game.argtypes = []
    retro_unload_game.restype = None
    break

for _lib in _libs.values():
    if not _lib.has("retro_get_region", "cdecl"):
        continue
    retro_get_region = _lib.get("retro_get_region", "cdecl")
    retro_get_region.argtypes = []
    retro_get_region.restype = c_uint
    break

for _lib in _libs.values():
    if not _lib.has("retro_get_memory_data", "cdecl"):
        continue
    retro_get_memory_data = _lib.get("retro_get_memory_data", "cdecl")
    retro_get_memory_data.argtypes = [c_uint]
    retro_get_memory_data.restype = POINTER(c_ubyte)
    retro_get_memory_data.errcheck = lambda v,*a : cast(v, c_void_p)
    break

for _lib in _libs.values():
    if not _lib.has("retro_get_memory_size", "cdecl"):
        continue
    retro_get_memory_size = _lib.get("retro_get_memory_size", "cdecl")
    retro_get_memory_size.argtypes = [c_uint]
    retro_get_memory_size.restype = c_size_t
    break

RETRO_API_VERSION = 1
RETRO_DEVICE_TYPE_SHIFT = 8
RETRO_DEVICE_MASK = ((1 << RETRO_DEVICE_TYPE_SHIFT) - 1)
def RETRO_DEVICE_SUBCLASS(base, id):
    return (((id + 1) << RETRO_DEVICE_TYPE_SHIFT) | base)

RETRO_DEVICE_NONE = 0
RETRO_DEVICE_JOYPAD = 1
RETRO_DEVICE_MOUSE = 2
RETRO_DEVICE_KEYBOARD = 3
RETRO_DEVICE_LIGHTGUN = 4
RETRO_DEVICE_ANALOG = 5
RETRO_DEVICE_POINTER = 6
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
RETRO_DEVICE_INDEX_ANALOG_LEFT = 0
RETRO_DEVICE_INDEX_ANALOG_RIGHT = 1
RETRO_DEVICE_INDEX_ANALOG_BUTTON = 2
RETRO_DEVICE_ID_ANALOG_X = 0
RETRO_DEVICE_ID_ANALOG_Y = 1
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
RETRO_VFS_FILE_ACCESS_READ = (1 << 0)
RETRO_VFS_FILE_ACCESS_WRITE = (1 << 1)
RETRO_VFS_FILE_ACCESS_READ_WRITE = (RETRO_VFS_FILE_ACCESS_READ | RETRO_VFS_FILE_ACCESS_WRITE)
RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING = (1 << 2)
RETRO_VFS_FILE_ACCESS_HINT_NONE = 0
RETRO_VFS_FILE_ACCESS_HINT_FREQUENT_ACCESS = (1 << 0)
RETRO_VFS_SEEK_POSITION_START = 0
RETRO_VFS_SEEK_POSITION_CURRENT = 1
RETRO_VFS_SEEK_POSITION_END = 2
RETRO_VFS_STAT_IS_VALID = (1 << 0)
RETRO_VFS_STAT_IS_DIRECTORY = (1 << 1)
RETRO_VFS_STAT_IS_CHARACTER_SPECIAL = (1 << 2)
RETRO_SERIALIZATION_QUIRK_INCOMPLETE = (1 << 0)
RETRO_SERIALIZATION_QUIRK_MUST_INITIALIZE = (1 << 1)
RETRO_SERIALIZATION_QUIRK_CORE_VARIABLE_SIZE = (1 << 2)
RETRO_SERIALIZATION_QUIRK_FRONT_VARIABLE_SIZE = (1 << 3)
RETRO_SERIALIZATION_QUIRK_SINGLE_SESSION = (1 << 4)
RETRO_SERIALIZATION_QUIRK_ENDIAN_DEPENDENT = (1 << 5)
RETRO_SERIALIZATION_QUIRK_PLATFORM_DEPENDENT = (1 << 6)
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
RETRO_HW_FRAME_BUFFER_VALID = cast((-1), POINTER(None))
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

retro_vfs_file_handle = struct_retro_vfs_file_handle

retro_vfs_dir_handle = struct_retro_vfs_dir_handle

retro_vfs_interface = struct_retro_vfs_interface

retro_vfs_interface_info = struct_retro_vfs_interface_info

retro_hw_render_interface = struct_retro_hw_render_interface

retro_led_interface = struct_retro_led_interface

retro_midi_interface = struct_retro_midi_interface

retro_hw_render_context_negotiation_interface = struct_retro_hw_render_context_negotiation_interface

retro_memory_descriptor = struct_retro_memory_descriptor

retro_memory_map = struct_retro_memory_map

retro_controller_description = struct_retro_controller_description

retro_controller_info = struct_retro_controller_info

retro_subsystem_memory_info = struct_retro_subsystem_memory_info

retro_subsystem_rom_info = struct_retro_subsystem_rom_info

retro_subsystem_info = struct_retro_subsystem_info

retro_get_proc_address_interface = struct_retro_get_proc_address_interface

retro_log_callback = struct_retro_log_callback

retro_perf_counter = struct_retro_perf_counter

retro_perf_callback = struct_retro_perf_callback

retro_sensor_interface = struct_retro_sensor_interface

retro_camera_callback = struct_retro_camera_callback

retro_location_callback = struct_retro_location_callback

retro_rumble_interface = struct_retro_rumble_interface

retro_audio_callback = struct_retro_audio_callback

retro_frame_time_callback = struct_retro_frame_time_callback

retro_audio_buffer_status_callback = struct_retro_audio_buffer_status_callback

retro_hw_render_callback = struct_retro_hw_render_callback

retro_keyboard_callback = struct_retro_keyboard_callback

retro_game_info = struct_retro_game_info

retro_disk_control_callback = struct_retro_disk_control_callback

retro_disk_control_ext_callback = struct_retro_disk_control_ext_callback

retro_netpacket_callback = struct_retro_netpacket_callback

retro_message = struct_retro_message

retro_message_ext = struct_retro_message_ext

retro_input_descriptor = struct_retro_input_descriptor

retro_system_info = struct_retro_system_info

retro_system_content_info_override = struct_retro_system_content_info_override

retro_game_info_ext = struct_retro_game_info_ext

retro_game_geometry = struct_retro_game_geometry

retro_system_timing = struct_retro_system_timing

retro_system_av_info = struct_retro_system_av_info

retro_variable = struct_retro_variable

retro_core_option_display = struct_retro_core_option_display

retro_core_option_value = struct_retro_core_option_value

retro_core_option_definition = struct_retro_core_option_definition

retro_core_options_intl = struct_retro_core_options_intl

retro_core_option_v2_category = struct_retro_core_option_v2_category

retro_core_option_v2_definition = struct_retro_core_option_v2_definition

retro_core_options_v2 = struct_retro_core_options_v2

retro_core_options_v2_intl = struct_retro_core_options_v2_intl

retro_core_options_update_display_callback = struct_retro_core_options_update_display_callback

retro_framebuffer = struct_retro_framebuffer

retro_fastforwarding_override = struct_retro_fastforwarding_override

retro_throttle_state = struct_retro_throttle_state

retro_microphone = struct_retro_microphone

retro_microphone_params = struct_retro_microphone_params

retro_microphone_interface = struct_retro_microphone_interface

retro_device_power = struct_retro_device_power

