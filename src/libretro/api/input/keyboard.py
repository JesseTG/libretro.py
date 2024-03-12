from dataclasses import dataclass
from enum import IntEnum, IntFlag, EJECT

from ...h import *


class Key(IntEnum, boundary=EJECT):
    UNKNOWN = RETROK_UNKNOWN
    BACKSPACE = RETROK_BACKSPACE
    TAB = RETROK_TAB
    CLEAR = RETROK_CLEAR
    RETURN = RETROK_RETURN
    PAUSE = RETROK_PAUSE
    ESCAPE = RETROK_ESCAPE
    SPACE = RETROK_SPACE
    EXCLAIM = RETROK_EXCLAIM
    QUOTEDBL = RETROK_QUOTEDBL
    HASH = RETROK_HASH
    DOLLAR = RETROK_DOLLAR
    AMPERSAND = RETROK_AMPERSAND
    QUOTE = RETROK_QUOTE
    LEFTPAREN = RETROK_LEFTPAREN
    RIGHTPAREN = RETROK_RIGHTPAREN
    ASTERISK = RETROK_ASTERISK
    PLUS = RETROK_PLUS
    COMMA = RETROK_COMMA
    MINUS = RETROK_MINUS
    PERIOD = RETROK_PERIOD
    SLASH = RETROK_SLASH
    Zero = RETROK_0
    One = RETROK_1
    Two = RETROK_2
    Three = RETROK_3
    Four = RETROK_4
    Five = RETROK_5
    Six = RETROK_6
    Seven = RETROK_7
    Eight = RETROK_8
    Nine = RETROK_9
    COLON = RETROK_COLON
    SEMICOLON = RETROK_SEMICOLON
    LESS = RETROK_LESS
    EQUALS = RETROK_EQUALS
    GREATER = RETROK_GREATER
    QUESTION = RETROK_QUESTION
    AT = RETROK_AT
    LEFTBRACKET = RETROK_LEFTBRACKET
    BACKSLASH = RETROK_BACKSLASH
    RIGHTBRACKET = RETROK_RIGHTBRACKET
    CARET = RETROK_CARET
    UNDERSCORE = RETROK_UNDERSCORE
    BACKQUOTE = RETROK_BACKQUOTE
    A = RETROK_a
    B = RETROK_b
    C = RETROK_c
    D = RETROK_d
    E = RETROK_e
    F = RETROK_f
    G = RETROK_g
    H = RETROK_h
    I = RETROK_i
    J = RETROK_j
    K = RETROK_k
    L = RETROK_l
    M = RETROK_m
    N = RETROK_n
    O = RETROK_o
    P = RETROK_p
    Q = RETROK_q
    R = RETROK_r
    S = RETROK_s
    T = RETROK_t
    U = RETROK_u
    V = RETROK_v
    W = RETROK_w
    X = RETROK_x
    Y = RETROK_y
    Z = RETROK_z
    LEFTBRACE = RETROK_LEFTBRACE
    BAR = RETROK_BAR
    RIGHTBRACE = RETROK_RIGHTBRACE
    TILDE = RETROK_TILDE
    DELETE = RETROK_DELETE

    KP0 = RETROK_KP0
    KP1 = RETROK_KP1
    KP2 = RETROK_KP2
    KP3 = RETROK_KP3
    KP4 = RETROK_KP4
    KP5 = RETROK_KP5
    KP6 = RETROK_KP6
    KP7 = RETROK_KP7
    KP8 = RETROK_KP8
    KP9 = RETROK_KP9
    KP_PERIOD = RETROK_KP_PERIOD
    KP_DIVIDE = RETROK_KP_DIVIDE
    KP_MULTIPLY = RETROK_KP_MULTIPLY
    KP_MINUS = RETROK_KP_MINUS
    KP_PLUS = RETROK_KP_PLUS
    KP_ENTER = RETROK_KP_ENTER
    KP_EQUALS = RETROK_KP_EQUALS

    UP = RETROK_UP
    DOWN = RETROK_DOWN
    RIGHT = RETROK_RIGHT
    LEFT = RETROK_LEFT
    INSERT = RETROK_INSERT
    HOME = RETROK_HOME
    END = RETROK_END
    PAGEUP = RETROK_PAGEUP
    PAGEDOWN = RETROK_PAGEDOWN

    F1 = RETROK_F1
    F2 = RETROK_F2
    F3 = RETROK_F3
    F4 = RETROK_F4
    F5 = RETROK_F5
    F6 = RETROK_F6
    F7 = RETROK_F7
    F8 = RETROK_F8
    F9 = RETROK_F9
    F10 = RETROK_F10
    F11 = RETROK_F11
    F12 = RETROK_F12
    F13 = RETROK_F13
    F14 = RETROK_F14
    F15 = RETROK_F15

    NUMLOCK = RETROK_NUMLOCK
    CAPSLOCK = RETROK_CAPSLOCK
    SCROLLOCK = RETROK_SCROLLOCK
    RSHIFT = RETROK_RSHIFT
    LSHIFT = RETROK_LSHIFT
    RCTRL = RETROK_RCTRL
    LCTRL = RETROK_LCTRL
    RALT = RETROK_RALT
    LALT = RETROK_LALT
    RMETA = RETROK_RMETA
    LMETA = RETROK_LMETA
    LSUPER = RETROK_LSUPER
    RSUPER = RETROK_RSUPER
    MODE = RETROK_MODE
    COMPOSE = RETROK_COMPOSE

    HELP = RETROK_HELP
    PRINT = RETROK_PRINT
    SYSREQ = RETROK_SYSREQ
    BREAK = RETROK_BREAK
    MENU = RETROK_MENU
    POWER = RETROK_POWER
    EURO = RETROK_EURO
    UNDO = RETROK_UNDO
    OEM_102 = RETROK_OEM_102

    def __init__(self, value):
        self._type_ = 'I'

    def is_modifier(self):
        return self in (Key.LCTRL, Key.RCTRL, Key.LSHIFT, Key.RSHIFT, Key.LALT, Key.RALT, Key.LMETA, Key.RMETA, Key.NUMLOCK, Key.CAPSLOCK, Key.SCROLLOCK)

    @classmethod
    def is_valid(cls, value: int) -> bool:
        return value in cls.__members__.values()


class KeyModifier(IntFlag):
    NONE = RETROKMOD_NONE
    SHIFT = RETROKMOD_SHIFT
    CTRL = RETROKMOD_CTRL
    ALT = RETROKMOD_ALT
    META = RETROKMOD_META
    NUMLOCK = RETROKMOD_NUMLOCK
    CAPSLOCK = RETROKMOD_CAPSLOCK
    SCROLLOCK = RETROKMOD_SCROLLOCK

    def __init__(self, value):
        self._type_ = 'I'


@dataclass(frozen=True)
class KeyboardState:
    backspace: bool = False
    tab: bool = False
    clear: bool = False
    return_: bool = False
    pause: bool = False
    escape: bool = False
    space: bool = False
    exclaim: bool = False
    quotedbl: bool = False
    hash: bool = False
    dollar: bool = False
    ampersand: bool = False
    quote: bool = False
    leftparen: bool = False
    rightparen: bool = False
    asterisk: bool = False
    plus: bool = False
    comma: bool = False
    minus: bool = False
    period: bool = False
    slash: bool = False
    zero: bool = False
    one: bool = False
    two: bool = False
    three: bool = False
    four: bool = False
    five: bool = False
    six: bool = False
    seven: bool = False
    eight: bool = False
    nine: bool = False
    colon: bool = False
    semicolon: bool = False
    less: bool = False
    equals: bool = False
    greater: bool = False
    question: bool = False
    at: bool = False
    leftbracket: bool = False
    backslash: bool = False
    rightbracket: bool = False
    caret: bool = False
    underscore: bool = False
    backquote: bool = False
    a: bool = False
    b: bool = False
    c: bool = False
    d: bool = False
    e: bool = False
    f: bool = False
    g: bool = False
    h: bool = False
    i: bool = False
    j: bool = False
    k: bool = False
    l: bool = False
    m: bool = False
    n: bool = False
    o: bool = False
    p: bool = False
    q: bool = False
    r: bool = False
    s: bool = False
    t: bool = False
    u: bool = False
    v: bool = False
    w: bool = False
    x: bool = False
    y: bool = False
    z: bool = False
    leftbrace: bool = False
    bar: bool = False
    rightbrace: bool = False
    tilde: bool = False
    delete: bool = False

    kp0: bool = False
    kp1: bool = False
    kp2: bool = False
    kp3: bool = False
    kp4: bool = False
    kp5: bool = False
    kp6: bool = False
    kp7: bool = False
    kp8: bool = False
    kp9: bool = False
    kp_period: bool = False
    kp_divide: bool = False
    kp_multiply: bool = False
    kp_minus: bool = False
    kp_plus: bool = False
    kp_enter: bool = False
    kp_equals: bool = False

    up: bool = False
    down: bool = False
    right: bool = False
    left: bool = False
    insert: bool = False
    home: bool = False
    end: bool = False
    pageup: bool = False
    pagedown: bool = False

    f1: bool = False
    f2: bool = False
    f3: bool = False
    f4: bool = False
    f5: bool = False
    f6: bool = False
    f7: bool = False
    f8: bool = False
    f9: bool = False
    f10: bool = False
    f11: bool = False
    f12: bool = False
    f13: bool = False
    f14: bool = False
    f15: bool = False

    numlock: bool = False
    capslock: bool = False
    scrolllock: bool = False
    rshift: bool = False
    lshift: bool = False
    rctrl: bool = False
    lctrl: bool = False
    ralt: bool = False
    lalt: bool = False
    rmeta: bool = False
    lmeta: bool = False
    lsuper: bool = False
    rsuper: bool = False
    mode: bool = False
    compose: bool = False

    help: bool = False
    print: bool = False
    sysreq: bool = False
    break_: bool = False
    menu: bool = False
    power: bool = False
    euro: bool = False
    oem_102: bool = False

    def __getitem__(self, item: int) -> bool:
        if Key.is_valid(item):
            return getattr(self, Key(item).name.lower())
        else:
            return False