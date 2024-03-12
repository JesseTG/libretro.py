__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
from abc import abstractmethod
from enum import IntEnum, IntFlag, unique, CONFORM, EJECT
import logging
import sys
from ctypes import *  # noqa: F401, F403
from typing import TYPE_CHECKING, get_type_hints, Sequence, overload

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


class retro_controller_description(Structure, metaclass=FieldsFromTypeHints):
    desc: c_char_p
    id: c_uint


class retro_controller_info(Structure, metaclass=FieldsFromTypeHints):
    types: POINTER(retro_controller_description)
    num_types: c_uint

    @overload
    def __getitem__(self, index: int) -> retro_controller_description: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[retro_controller_description]: ...

    def __getitem__(self, index):
        if not self.types:
            raise ValueError("No controller types available")

        match index:
            case int(i):
                if not (0 <= i < self.num_types):
                    raise IndexError(f"Expected 0 <= index < {len(self)}, got {i}")
                return self.types[i]

            case slice() as s:
                s: slice
                return self.types[s]

            case _:
                raise TypeError(f"Expected an int or slice index, got {type(index).__name__}")

    def __len__(self):
        return int(self.num_types)


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


retro_video_refresh_t = CFUNCTYPE(None, c_void_p, c_uint, c_uint, c_size_t)

retro_audio_sample_t = CFUNCTYPE(None, c_int16, c_int16)

retro_audio_sample_batch_t = CFUNCTYPE(c_size_t, POINTER(c_int16), c_size_t)


RETRO_MEMORY_MASK = 0xff
RETRO_MEMORY_SAVE_RAM = 0
RETRO_MEMORY_RTC = 1
RETRO_MEMORY_SYSTEM_RAM = 2
RETRO_MEMORY_VIDEO_RAM = 3


RETRO_MEMORY_ACCESS_WRITE = (1 << 0)
RETRO_MEMORY_ACCESS_READ = (1 << 1)
RETRO_MEMORY_TYPE_CACHED = (1 << 0)
