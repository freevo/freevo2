# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# linux_input.py - An interface to the linux event input device translated
#                  from the kernel's linux/input.h.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#  This file has lots of stuff left in comments to help me work on it and
#  complete it easier.  They will gradually go away.
#
# Todo:        
#  Test the ioctls and put some to use.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/09/25 04:37:41  rshortt
# Support files for freevo input.
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */


#struct input_event {
#struct timeval time;
#__u16 type;
#__u16 code;
#__s32 value;
#};

# * Protocol version.
# EV_VERSION0x010000

# * IOCTLs (0x00 - 0x7f)

#struct input_id {
#__u16 bustype;
#__u16 vendor;
#__u16 product;
#__u16 version;
#};
#struct input_absinfo {
#__s32 value;
#__s32 minimum;
#__s32 maximum;
#__s32 fuzz;
#__s32 flat;
#};

from util.ioctl import *

EVIOCGVERSION_ST = 'i'
EVIOCGVERSION_NO = IOR('E', 0x01, EVIOCGVERSION_ST)# get driver version 

EVIOCGID_ST = '4H' # struct input_id
EVIOCGID = IOR('E', 0x02, EVIOCGID_ST) # get device ID 

EVIOCGKEYCODE_ST = '2i'
EVIOCGKEYCODE_NO = IOR('E', 0x04, EVIOCGKEYCODE_ST) # get keycode 
# EVIOCGKEYCODE = IOR('E', 0x04, int[2]) # get keycode 

EVIOCSKEYCODE_ST = '2i'
EVIOCSKEYCODE_NO = IOW('E', 0x04, EVIOCSKEYCODE_ST) # set keycode 
# EVIOCSKEYCODE = IOW('E', 0x04, int[2]) # set keycode 

EVIOCGNAME_ST = '32s'
EVIOCGNAME_NO = IOR('E', 0x06, EVIOCGNAME_ST)# get device name 
# EVIOCGNAME(len) = IOC(IOC_READ, 'E', 0x06, len)# get device name 

EVIOCGPHYS_ST = '32s'
EVIOCGPHYS_NO = IOR('E', 0x07, EVIOCGPHYS_ST)# get physical location 
# EVIOCGPHYS(len) = IOC(IOC_READ, 'E', 0x07, len)# get physical location 

EVIOCGUNIQ_ST = '32s'
EVIOCGUNIQ_NO = IOR('E', 0x08, EVIOCGUNIQ_ST)# get unique identifier 
# EVIOCGUNIQ(len) = IOC(IOC_READ, 'E', 0x08, len)# get unique identifier 

EVIOCGKEY_ST = '32s'
EVIOCGKEY_NO = IOR('E', 0x18, EVIOCGKEY_ST)# get global keystate 
# EVIOCGKEY(len) = IOC(IOC_READ, 'E', 0x18, len)# get global keystate 

EVIOCGLED_ST = '32s'
EVIOCGLED_NO = IOR('E', 0x19, EVIOCGLED_ST)# get all LEDs 
# EVIOCGLED(len) = IOC(IOC_READ, 'E', 0x19, len)# get all LEDs 

EVIOCGSND_ST = '32s'
EVIOCGSND_NO = IOR('E', 0x1a, EVIOCGSND_ST)# get all sounds status 
# EVIOCGSND(len) = IOC(IOC_READ, 'E', 0x1a, len)# get all sounds status 

# EVIOCGBIT(ev,len) = IOC(IOC_READ, 'E', 0x20 + ev, len)# get event bits 
# EVIOCGABS(abs) = IOR('E', 0x40 + abs, struct input_absinfo)# get abs value/limits 
# EVIOCSABS(abs) = IOW('E', 0xc0 + abs, struct input_absinfo)# set abs value/limits 

# EVIOCSFF = IOC(IOC_WRITE, 'E', 0x80, sizeof(struct ff_effect))# send a force effect to a force feedback device 
# EVIOCRMFF = IOW('E', 0x81, int)# Erase a force effect 
# EVIOCGEFFECTS = IOR('E', 0x84, int)# Report number of effects playable at the same time 

EVIOCGRAB_ST = 'i'
EVIOCGRAB = IOW('E', 0x90, EVIOCGRAB_ST)# Grab/Release device 
# EVIOCGRAB = IOW('E', 0x90, int)# Grab/Release device 


# * Event types

EV_SYN       = 0x00
EV_KEY       = 0x01
EV_REL       = 0x02
EV_ABS       = 0x03
EV_MSC       = 0x04
EV_LED       = 0x11
EV_SND       = 0x12
EV_REP       = 0x14
EV_FF        = 0x15
EV_PWR       = 0x16
EV_FF_STATUS = 0x17
EV_MAX       = 0x1f


# * Synchronization events.

SYN_REPORT = 0
SYN_CONFIG = 1


# * Keys and buttons

KEY_RESERVED = 0
KEY_ESC = 1
KEY_1 = 2
KEY_2 = 3
KEY_3 = 4
KEY_4 = 5
KEY_5 = 6
KEY_6 = 7
KEY_7 = 8
KEY_8 = 9
KEY_9 = 10
KEY_0 = 11
KEY_MINUS = 12
KEY_EQUAL = 13
KEY_BACKSPACE = 14
KEY_TAB = 15
KEY_Q = 16
KEY_W = 17
KEY_E = 18
KEY_R = 19
KEY_T = 20
KEY_Y = 21
KEY_U = 22
KEY_I = 23
KEY_O = 24
KEY_P = 25
KEY_LEFTBRACE = 26
KEY_RIGHTBRACE = 27
KEY_ENTER = 28
KEY_LEFTCTRL = 29
KEY_A = 30
KEY_S = 31
KEY_D = 32
KEY_F = 33
KEY_G = 34
KEY_H = 35
KEY_J = 36
KEY_K = 37
KEY_L = 38
KEY_SEMICOLON = 39
KEY_APOSTROPHE = 40
KEY_GRAVE = 41
KEY_LEFTSHIFT = 42
KEY_BACKSLASH = 43
KEY_Z = 44
KEY_X = 45
KEY_C = 46
KEY_V = 47
KEY_B = 48
KEY_N = 49
KEY_M = 50
KEY_COMMA = 51
KEY_DOT = 52
KEY_SLASH = 53
KEY_RIGHTSHIFT = 54
KEY_KPASTERISK = 55
KEY_LEFTALT = 56
KEY_SPACE = 57
KEY_CAPSLOCK = 58
KEY_F1 = 59
KEY_F2 = 60
KEY_F3 = 61
KEY_F4 = 62
KEY_F5 = 63
KEY_F6 = 64
KEY_F7 = 65
KEY_F8 = 66
KEY_F9 = 67
KEY_F10 = 68
KEY_NUMLOCK = 69
KEY_SCROLLLOCK = 70
KEY_KP7 = 71
KEY_KP8 = 72
KEY_KP9 = 73
KEY_KPMINUS = 74
KEY_KP4 = 75
KEY_KP5 = 76
KEY_KP6 = 77
KEY_KPPLUS = 78
KEY_KP1 = 79
KEY_KP2 = 80
KEY_KP3 = 81
KEY_KP0 = 82
KEY_KPDOT = 83

KEY_ZENKAKUHANKAKU = 85
KEY_102ND = 86
KEY_F11 = 87
KEY_F12 = 88
KEY_RO = 89
KEY_KATAKANA = 90
KEY_HIRAGANA = 91
KEY_HENKAN = 92
KEY_KATAKANAHIRAGANA = 93
KEY_MUHENKAN = 94
KEY_KPJPCOMMA = 95
KEY_KPENTER = 96
KEY_RIGHTCTRL = 97
KEY_KPSLASH = 98
KEY_SYSRQ = 99
KEY_RIGHTALT = 100
KEY_LINEFEED = 101
KEY_HOME = 102
KEY_UP = 103
KEY_PAGEUP = 104
KEY_LEFT = 105
KEY_RIGHT = 106
KEY_END = 107
KEY_DOWN = 108
KEY_PAGEDOWN = 109
KEY_INSERT = 110
KEY_DELETE = 111
KEY_MACRO = 112
KEY_MUTE = 113
KEY_VOLUMEDOWN = 114
KEY_VOLUMEUP = 115
KEY_POWER = 116
KEY_KPEQUAL = 117
KEY_KPPLUSMINUS = 118
KEY_PAUSE = 119

KEY_KPCOMMA = 121
KEY_HANGUEL = 122
KEY_HANJA = 123
KEY_YEN = 124
KEY_LEFTMETA = 125
KEY_RIGHTMETA = 126
KEY_COMPOSE = 127

KEY_STOP = 128
KEY_AGAIN = 129
KEY_PROPS = 130
KEY_UNDO = 131
KEY_FRONT = 132
KEY_COPY = 133
KEY_OPEN = 134
KEY_PASTE = 135
KEY_FIND = 136
KEY_CUT = 137
KEY_HELP = 138
KEY_MENU = 139
KEY_CALC = 140
KEY_SETUP = 141
KEY_SLEEP = 142
KEY_WAKEUP = 143
KEY_FILE = 144
KEY_SENDFILE = 145
KEY_DELETEFILE = 146
KEY_XFER = 147
KEY_PROG1 = 148
KEY_PROG2 = 149
KEY_WWW = 150
KEY_MSDOS = 151
KEY_COFFEE = 152
KEY_DIRECTION = 153
KEY_CYCLEWINDOWS = 154
KEY_MAIL = 155
KEY_BOOKMARKS = 156
KEY_COMPUTER = 157
KEY_BACK = 158
KEY_FORWARD = 159
KEY_CLOSECD = 160
KEY_EJECTCD = 161
KEY_EJECTCLOSECD = 162
KEY_NEXTSONG = 163
KEY_PLAYPAUSE = 164
KEY_PREVIOUSSONG = 165
KEY_STOPCD = 166
KEY_RECORD = 167
KEY_REWIND = 168
KEY_PHONE = 169
KEY_ISO = 170
KEY_CONFIG = 171
KEY_HOMEPAGE = 172
KEY_REFRESH = 173
KEY_EXIT = 174
KEY_MOVE = 175
KEY_EDIT = 176
KEY_SCROLLUP = 177
KEY_SCROLLDOWN = 178
KEY_KPLEFTPAREN = 179
KEY_KPRIGHTPAREN = 180

KEY_F13 = 183
KEY_F14 = 184
KEY_F15 = 185
KEY_F16 = 186
KEY_F17 = 187
KEY_F18 = 188
KEY_F19 = 189
KEY_F20 = 190
KEY_F21 = 191
KEY_F22 = 192
KEY_F23 = 193
KEY_F24 = 194

KEY_PLAYCD = 200
KEY_PAUSECD = 201
KEY_PROG3 = 202
KEY_PROG4 = 203
KEY_SUSPEND = 205
KEY_CLOSE = 206
KEY_PLAY = 207
KEY_FASTFORWARD = 208
KEY_BASSBOOST = 209
KEY_PRINT = 210
KEY_HP = 211
KEY_CAMERA = 212
KEY_SOUND = 213
KEY_QUESTION = 214
KEY_EMAIL = 215
KEY_CHAT = 216
KEY_SEARCH = 217
KEY_CONNECT = 218
KEY_FINANCE = 219
KEY_SPORT = 220
KEY_SHOP = 221
KEY_ALTERASE = 222
KEY_CANCEL = 223
KEY_BRIGHTNESSDOWN = 224
KEY_BRIGHTNESSUP = 225
KEY_MEDIA = 226

KEY_UNKNOWN = 240

BTN_MISC = 0x100
BTN_0 = 0x100
BTN_1 = 0x101
BTN_2 = 0x102
BTN_3 = 0x103
BTN_4 = 0x104
BTN_5 = 0x105
BTN_6 = 0x106
BTN_7 = 0x107
BTN_8 = 0x108
BTN_9 = 0x109

BTN_MOUSE = 0x110
BTN_LEFT = 0x110
BTN_RIGHT = 0x111
BTN_MIDDLE = 0x112
BTN_SIDE = 0x113
BTN_EXTRA = 0x114
BTN_FORWARD = 0x115
BTN_BACK = 0x116
BTN_TASK = 0x117

BTN_JOYSTICK = 0x120
BTN_TRIGGER = 0x120
BTN_THUMB = 0x121
BTN_THUMB2 = 0x122
BTN_TOP = 0x123
BTN_TOP2 = 0x124
BTN_PINKIE = 0x125
BTN_BASE = 0x126
BTN_BASE2 = 0x127
BTN_BASE3 = 0x128
BTN_BASE4 = 0x129
BTN_BASE5 = 0x12a
BTN_BASE6 = 0x12b
BTN_DEAD = 0x12f

BTN_GAMEPAD = 0x130
BTN_A = 0x130
BTN_B = 0x131
BTN_C = 0x132
BTN_X = 0x133
BTN_Y = 0x134
BTN_Z = 0x135
BTN_TL = 0x136
BTN_TR = 0x137
BTN_TL2 = 0x138
BTN_TR2 = 0x139
BTN_SELECT = 0x13a
BTN_START = 0x13b
BTN_MODE = 0x13c
BTN_THUMBL = 0x13d
BTN_THUMBR = 0x13e

BTN_DIGI = 0x140
BTN_TOOL_PEN = 0x140
BTN_TOOL_RUBBER = 0x141
BTN_TOOL_BRUSH = 0x142
BTN_TOOL_PENCIL = 0x143
BTN_TOOL_AIRBRUSH = 0x144
BTN_TOOL_FINGER = 0x145
BTN_TOOL_MOUSE = 0x146
BTN_TOOL_LENS = 0x147
BTN_TOUCH = 0x14a
BTN_STYLUS = 0x14b
BTN_STYLUS2 = 0x14c
BTN_TOOL_DOUBLETAP = 0x14d
BTN_TOOL_TRIPLETAP = 0x14e

BTN_WHEEL = 0x150
BTN_GEAR_DOWN = 0x150
BTN_GEAR_UP = 0x151

KEY_OK = 0x160
KEY_SELECT  = 0x161
KEY_GOTO = 0x162
KEY_CLEAR = 0x163
KEY_POWER2 = 0x164
KEY_OPTION = 0x165
KEY_INFO = 0x166
KEY_TIME = 0x167
KEY_VENDOR = 0x168
KEY_ARCHIVE = 0x169
KEY_PROGRAM = 0x16a
KEY_CHANNEL = 0x16b
KEY_FAVORITES = 0x16c
KEY_EPG = 0x16d
KEY_PVR = 0x16e
KEY_MHP = 0x16f
KEY_LANGUAGE = 0x170
KEY_TITLE = 0x171
KEY_SUBTITLE = 0x172
KEY_ANGLE = 0x173
KEY_ZOOM = 0x174
KEY_MODE = 0x175
KEY_KEYBOARD = 0x176
KEY_SCREEN = 0x177
KEY_PC = 0x178
KEY_TV = 0x179
KEY_TV2 = 0x17a
KEY_VCR = 0x17b
KEY_VCR2 = 0x17c
KEY_SAT = 0x17d
KEY_SAT2 = 0x17e
KEY_CD = 0x17f
KEY_TAPE = 0x180
KEY_RADIO = 0x181
KEY_TUNER = 0x182
KEY_PLAYER = 0x183
KEY_TEXT = 0x184
KEY_DVD = 0x185
KEY_AUX = 0x186
KEY_MP3 = 0x187
KEY_AUDIO = 0x188
KEY_VIDEO = 0x189
KEY_DIRECTORY = 0x18a
KEY_LIST = 0x18b
KEY_MEMO = 0x18c
KEY_CALENDAR = 0x18d
KEY_RED = 0x18e
KEY_GREEN = 0x18f
KEY_YELLOW = 0x190
KEY_BLUE = 0x191
KEY_CHANNELUP = 0x192
KEY_CHANNELDOWN = 0x193
KEY_FIRST = 0x194
KEY_LAST = 0x195
KEY_AB = 0x196
KEY_NEXT = 0x197
KEY_RESTART = 0x198
KEY_SLOW = 0x199
KEY_SHUFFLE = 0x19a
KEY_BREAK = 0x19b
KEY_PREVIOUS = 0x19c
KEY_DIGITS = 0x19d
KEY_TEEN = 0x19e
KEY_TWEN = 0x19f

KEY_DEL_EOL = 0x1c0
KEY_DEL_EOS = 0x1c1
KEY_INS_LINE = 0x1c2
KEY_DEL_LINE = 0x1c3

KEY_MAX = 0x1ff


# * Relative axes

REL_X = 0x00
REL_Y = 0x01
REL_Z = 0x02
REL_HWHEEL = 0x06
REL_DIAL = 0x07
REL_WHEEL = 0x08
REL_MISC = 0x09
REL_MAX = 0x0f


# * Absolute axes

ABS_X = 0x00
ABS_Y = 0x01
ABS_Z = 0x02
ABS_RX = 0x03
ABS_RY = 0x04
ABS_RZ = 0x05
ABS_THROTTLE = 0x06
ABS_RUDDER = 0x07
ABS_WHEEL = 0x08
ABS_GAS = 0x09
ABS_BRAKE = 0x0a
ABS_HAT0X = 0x10
ABS_HAT0Y = 0x11
ABS_HAT1X = 0x12
ABS_HAT1Y = 0x13
ABS_HAT2X = 0x14
ABS_HAT2Y = 0x15
ABS_HAT3X = 0x16
ABS_HAT3Y = 0x17
ABS_PRESSURE = 0x18
ABS_DISTANCE = 0x19
ABS_TILT_X = 0x1a
ABS_TILT_Y = 0x1b
ABS_TOOL_WIDTH = 0x1c
ABS_VOLUME = 0x20
ABS_MISC = 0x28
ABS_MAX = 0x3f


# * Misc events

MSC_SERIAL = 0x00
MSC_PULSELED = 0x01
MSC_GESTURE = 0x02
MSC_MAX = 0x07


# * LEDs

LED_NUML = 0x00
LED_CAPSL = 0x01
LED_SCROLLL = 0x02
LED_COMPOSE = 0x03
LED_KANA = 0x04
LED_SLEEP = 0x05
LED_SUSPEND = 0x06
LED_MUTE = 0x07
LED_MISC = 0x08
LED_MAX = 0x0f


# * Autorepeat values

REP_DELAY = 0x00
REP_PERIOD = 0x01
REP_MAX = 0x01


# * Sounds

SND_CLICK = 0x00
SND_BELL = 0x01
SND_TONE = 0x02
SND_MAX = 0x07


# * IDs.

ID_BUS = 0
ID_VENDOR = 1
ID_PRODUCT = 2
ID_VERSION = 3

BUS_PCI = 0x01
BUS_ISAPNP = 0x02
BUS_USB = 0x03
BUS_HIL = 0x04
BUS_BLUETOOTH = 0x05

BUS_ISA = 0x10
BUS_I8042 = 0x11
BUS_XTKBD = 0x12
BUS_RS232 = 0x13
BUS_GAMEPORT = 0x14
BUS_PARPORT = 0x15
BUS_AMIGA = 0x16
BUS_ADB = 0x17
BUS_I2C = 0x18
BUS_HOST = 0x19


# * Values describing the status of an effect

FF_STATUS_STOPPED = 0x00
FF_STATUS_PLAYING = 0x01
FF_STATUS_MAX = 0x01


# * Structures used in ioctls to upload effects to a device
# * The first structures are not passed directly by using ioctls.
# * They are sub-structures of the actually sent structure (called ff_effect)

#struct ff_replay {
# = __u16 length; /* Duration of an effect in ms. All other times are also expressed in ms */
# = __u16 delay;  /* Time to wait before to start playing an effect */
#};

#struct ff_trigger {
# = __u16 button;   /* Number of button triggering an effect */
# = __u16 interval; /* Time to wait before an effect can be re-triggered (ms) */
#};

#struct ff_envelope {
# = __u16 attack_length;/* Duration of attack (ms) */
# = __u16 attack_level;/* Level at beginning of attack */
# = __u16 fade_length;/* Duration of fade (ms) */
# = __u16 fade_level;/* Level at end of fade */
#};

#/* FF_CONSTANT */
#struct ff_constant_effect {
# = __s16 level;    /* Strength of effect. Negative values are OK */
# = struct ff_envelope envelope;
#};

#/* FF_RAMP */
#struct ff_ramp_effect {
# = __s16 start_level;
# = __s16 end_level;
# = struct ff_envelope envelope;
#};

#/* FF_SPRING of FF_FRICTION */
#struct ff_condition_effect {
# = __u16 right_saturation; /* Max level when joystick is on the right */
# = __u16 left_saturation;  /* Max level when joystick in on the left */
#
# = __s16 right_coeff;/* Indicates how fast the force grows when the
# =   joystick moves to the right */
# = __s16 left_coeff;/* Same for left side */
#
# = __u16 deadband;/* Size of area where no force is produced */
# = __s16 center;/* Position of dead zone */
#
#};

#/* FF_PERIODIC */
#struct ff_periodic_effect {
# = __u16 waveform;/* Kind of wave (sine, square...) */
# = __u16 period;/* in ms */
# = __s16 magnitude;/* Peak value */
# = __s16 offset;/* Mean value of wave (roughly) */
# = __u16 phase;/* 'Horizontal' shift */
#
# = struct ff_envelope envelope;

#/* Only used if waveform  = = FF_CUSTOM */
# = __u32 custom_len;/* Number of samples */
# = __s16 *custom_data;/* Buffer of samples */
#/* Note: the data pointed by custom_data is copied by the driver. You can
# * therefore dispose of the memory after the upload/update */
#};

#/* FF_RUMBLE */
#/* Some rumble pads have two motors of different weight.
#   strong_magnitude represents the magnitude of the vibration generated
#   by the heavy motor.
#*/
#struct ff_rumble_effect {
# = __u16 strong_magnitude;  /* Magnitude of the heavy motor */
# = __u16 weak_magnitude;    /* Magnitude of the light one */
#};

#/*
# * Structure sent through ioctl from the application to the driver
# */
#struct ff_effect {
# = __u16 type;
#/* Following field denotes the unique id assigned to an effect.
# * If user sets if to -1, a new effect is created, and its id is returned in the same field
# * Else, the user sets it to the effect id it wants to update.
# */
# = __s16 id;
#
# = __u16 direction;/* Direction. 0 deg -> 0x0000 (down)
# =     90 deg -> 0x4000 (left)
# =    180 deg -> 0x8000 (up)
# =    270 deg -> 0xC000 (right)
# = */
#
# = struct ff_trigger trigger;
# = struct ff_replay replay;
#
# = union {
# = struct ff_constant_effect constant;
# = struct ff_ramp_effect ramp;
# = struct ff_periodic_effect periodic;
# = struct ff_condition_effect condition[2]; /* One for each axis */
# = struct ff_rumble_effect rumble;
# = } u;
#};


#/*
# * Force feedback effect types
# */

FF_RUMBLE = 0x50
FF_PERIODIC = 0x51
FF_CONSTANT = 0x52
FF_SPRING = 0x53
FF_FRICTION = 0x54
FF_DAMPER = 0x55
FF_INERTIA = 0x56
FF_RAMP = 0x57


#/*
# * Force feedback periodic effect types
# */

FF_SQUARE = 0x58
FF_TRIANGLE = 0x59
FF_SINE = 0x5a
FF_SAW_UP = 0x5b
FF_SAW_DOWN = 0x5c
FF_CUSTOM = 0x5d


#/*
# * Set ff device properties
# */

FF_GAIN = 0x60
FF_AUTOCENTER = 0x61

FF_MAX = 0x7f

#ifdef __KERNEL__


#/*
# * In-kernel definitions.
# */

#include <linux/fs.h>
#include <linux/timer.h>

#NBITS(x) ((((x)-1)/BITS_PER_LONG)+1)
#BIT(x) = (1UL<<((x)%BITS_PER_LONG))
#LONG(x) ((x)/BITS_PER_LONG)

#INPUT_KEYCODE(dev, scancode) ((dev->keycodesize  = = 1) ? ((u8*)dev->keycode)[scancode] : \
# = ((dev->keycodesize == 2) ? ((u16*)dev->keycode)[scancode] : (((u32*)dev->keycode)[scancode])))

#SET_INPUT_KEYCODE(dev, scancode, val) = \
# = ({unsigned __old;\
# = switch (dev->keycodesize) {\
# = case 1: {\
# = u8 *k = (u8 *)dev->keycode;\
# = __old = k[scancode];\
# = k[scancode] = val;\
# = break;\
# = }\
# = case 2: {\
# = u16 *k = (u16 *)dev->keycode;\
# = __old = k[scancode];\
# = k[scancode] = val;\
# = break;\
# = }\
# = default: {\
# = u32 *k = (u32 *)dev->keycode;\
# = __old = k[scancode];\
# = k[scancode] = val;\
# = break;\
# = }\
# = }\
# = __old; })

#struct input_dev {
#
# = void *private;
#
# = char *name;
# = char *phys;
# = char *uniq;
# = struct input_id id;
#
# = unsigned long evbit[NBITS(EV_MAX)];
# = unsigned long keybit[NBITS(KEY_MAX)];
# = unsigned long relbit[NBITS(REL_MAX)];
# = unsigned long absbit[NBITS(ABS_MAX)];
# = unsigned long mscbit[NBITS(MSC_MAX)];
# = unsigned long ledbit[NBITS(LED_MAX)];
# = unsigned long sndbit[NBITS(SND_MAX)];
# = unsigned long ffbit[NBITS(FF_MAX)];
# = int ff_effects_max;
#
# = unsigned int keycodemax;
# = unsigned int keycodesize;
# = void *keycode;
#
# = unsigned int repeat_key;
# = struct timer_list timer;
#
# = struct pm_dev *pm_dev;
# = struct pt_regs *regs;
# = int state;
#
# = int sync;
#
# = int abs[ABS_MAX + 1];
# = int rep[REP_MAX + 1];
#
# = unsigned long key[NBITS(KEY_MAX)];
# = unsigned long led[NBITS(LED_MAX)];
# = unsigned long snd[NBITS(SND_MAX)];
#
# = int absmax[ABS_MAX + 1];
# = int absmin[ABS_MAX + 1];
# = int absfuzz[ABS_MAX + 1];
# = int absflat[ABS_MAX + 1];
#
# = int (*open)(struct input_dev *dev);
# = void (*close)(struct input_dev *dev);
# = int (*accept)(struct input_dev *dev, struct file *file);
# = int (*flush)(struct input_dev *dev, struct file *file);
# = int (*event)(struct input_dev *dev, unsigned int type, unsigned int code, int value);
# = int (*upload_effect)(struct input_dev *dev, struct ff_effect *effect);
# = int (*erase_effect)(struct input_dev *dev, int effect_id);
#
# = struct input_handle *grab;
# = struct device *dev;
#
# = struct list_headh_list;
# = struct list_headnode;
#};


#/*
# * Structure for hotplug & device<->driver matching.
# */

INPUT_DEVICE_ID_MATCH_BUS = 1
INPUT_DEVICE_ID_MATCH_VENDOR = 2
INPUT_DEVICE_ID_MATCH_PRODUCT = 4
INPUT_DEVICE_ID_MATCH_VERSION = 8

INPUT_DEVICE_ID_MATCH_EVBIT = 0x010
INPUT_DEVICE_ID_MATCH_KEYBIT = 0x020
INPUT_DEVICE_ID_MATCH_RELBIT = 0x040
INPUT_DEVICE_ID_MATCH_ABSBIT = 0x080
INPUT_DEVICE_ID_MATCH_MSCIT = 0x100
INPUT_DEVICE_ID_MATCH_LEDBIT = 0x200
INPUT_DEVICE_ID_MATCH_SNDBIT = 0x400
INPUT_DEVICE_ID_MATCH_FFBIT = 0x800

#INPUT_DEVICE_ID_MATCH_DEVICE\
# = (INPUT_DEVICE_ID_MATCH_BUS | INPUT_DEVICE_ID_MATCH_VENDOR | INPUT_DEVICE_ID_MATCH_PRODUCT)
#INPUT_DEVICE_ID_MATCH_DEVICE_AND_VERSION\
# = (INPUT_DEVICE_ID_MATCH_DEVICE | INPUT_DEVICE_ID_MATCH_VERSION)

#struct input_device_id {
#
# = unsigned long flags;
#
# = struct input_id id;
#
# = unsigned long evbit[NBITS(EV_MAX)];
# = unsigned long keybit[NBITS(KEY_MAX)];
# = unsigned long relbit[NBITS(REL_MAX)];
# = unsigned long absbit[NBITS(ABS_MAX)];
# = unsigned long mscbit[NBITS(MSC_MAX)];
# = unsigned long ledbit[NBITS(LED_MAX)];
# = unsigned long sndbit[NBITS(SND_MAX)];
# = unsigned long ffbit[NBITS(FF_MAX)];
#
# = unsigned long driver_info;
#};
#
#struct input_handle;
#
#struct input_handler {
#
# = void *private;
#
# = void (*event)(struct input_handle *handle, unsigned int type, unsigned int code, int value);
# = struct input_handle* (*connect)(struct input_handler *handler, struct input_dev *dev, struct input_device_id *id);
# = void (*disconnect)(struct input_handle *handle);
#
# = struct file_operations *fops;
# = int minor;
# = char *name;
#
# = struct input_device_id *id_table;
# = struct input_device_id *blacklist;
#
# = struct list_headh_list;
# = struct list_headnode;
#};
#
#struct input_handle {
#
# = void *private;
#
# = int open;
# = char *name;
#
# = struct input_dev *dev;
# = struct input_handler *handler;
#
# = struct list_headd_node;
# = struct list_headh_node;
#};
#
#to_dev(n) container_of(n,struct input_dev,node)
#to_handler(n) container_of(n,struct input_handler,node);
#to_handle(n) container_of(n,struct input_handle,d_node)
#to_handle_h(n) container_of(n,struct input_handle,h_node)
#
#static inline void init_input_dev(struct input_dev *dev)
#{
# = INIT_LIST_HEAD(&dev->h_list);
# = INIT_LIST_HEAD(&dev->node);
#}
#
#void input_register_device(struct input_dev *);
#void input_unregister_device(struct input_dev *);
#
#void input_register_handler(struct input_handler *);
#void input_unregister_handler(struct input_handler *);
#
#int input_grab_device(struct input_handle *);
#void input_release_device(struct input_handle *);
#
#int input_open_device(struct input_handle *);
#void input_close_device(struct input_handle *);
#
#int input_accept_process(struct input_handle *handle, struct file *file);
#int input_flush_device(struct input_handle* handle, struct file* file);
#
#void input_event(struct input_dev *dev, unsigned int type, unsigned int code, int value);
#
#static inline void input_report_key(struct input_dev *dev, unsigned int code, int value)
#{
# = input_event(dev, EV_KEY, code, !!value);
#}
#
#static inline void input_report_rel(struct input_dev *dev, unsigned int code, int value)
#{
# = input_event(dev, EV_REL, code, value);
#}
#
#static inline void input_report_abs(struct input_dev *dev, unsigned int code, int value)
#{
# = input_event(dev, EV_ABS, code, value);
#}
#
#static inline void input_report_ff(struct input_dev *dev, unsigned int code, int value)
#{
# = input_event(dev, EV_FF, code, value);
#}
#
#static inline void input_report_ff_status(struct input_dev *dev, unsigned int code, int value)
#{
# = input_event(dev, EV_FF_STATUS, code, value);
#}
#
#static inline void input_regs(struct input_dev *dev, struct pt_regs *regs)
#{
# = dev->regs = regs;
#}
#
#static inline void input_sync(struct input_dev *dev)
#{
# = input_event(dev, EV_SYN, SYN_REPORT, 0);
# = dev->regs = NULL;
#}
#
#static inline void input_set_abs_params(struct input_dev *dev, int axis, int min, int max, int fuzz, int flat)
#{
# = dev->absmin[axis] = min;
# = dev->absmax[axis] = max;
# = dev->absfuzz[axis] = fuzz;
# = dev->absflat[axis] = flat;
#
# = dev->absbit[LONG(axis)] |= BIT(axis);
#}
#
#extern struct class_simple *input_class;
#
##endif
##endif
