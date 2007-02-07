# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# freevo_config.py - System configuration
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al. 
# Please see the file doc/CREDITS for a complete list of authors.
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
# -----------------------------------------------------------------------


# ======================================================================
# General freevo settings:
# ======================================================================

#
# You can add more keybindings by adding them to the correct hash. 
# e.g. If you want to send 'contrast -100' to mplayer by pressing the '1' key, 
# just add the following line: 
#
# EVENTS['video']['1'] = Event(VIDEO_SEND_MPLAYER_CMD, 'contrast -100')
#
# See src/event.py for a list of all possible events.
#
EVENTS = input.EVENTMAP

#
# Use arrow keys for back and select (alternate way of navigating)
#
MENU_ARROW_NAVIGATION = 0

#
# Keymap to map keyboard keys to event strings. You can also add new keys
# here, e.g. KEYMAP[K_x] = 'SUBTITLE'. The K_-names are defined by pygame.
#
KEYBOARD_MAP = input.KEYBOARD_MAP
REMOTE_MAP   = input.REMOTE_MAP
DIRECTFB_MAP = input.DIRECTFB_MAP

#
# Suffix for playlist files
#
PLAYLIST_SUFFIX = [ 'm3u' ]

# ======================================================================
# Plugins:
# ======================================================================

# Remove undesired plugins by setting plugin.remove(code). 
# You can also use the name to remove a plugin. But if you do that, 
# all instances of this plugin will be removed.
#
# Examples:
# plugin.remove(plugin_tv) or
# plugin.remove('tv') will remove the tv module from the main menu

# Items in the main menu.
plugin.activate('tv', level=10)

# Audio Mixer
MIXER_MAJOR_AUDIO_CTRL = 'VOL'            # 'VOL', 'PCM' 'OGAIN' etc.
MIXER_CONTROL_ALL_AUDIO = True            # Freevo takes complete control of audio
MIXER_MAX_VOLUME        = 90              # Set maximum volume level.
MIXER_DEFAULT_VOLUME    = 40              # Set default volume level.
MIXER_DEVICE            = '/dev/mixer'    # mixer device 
plugin.activate('mixer')

# delete file in menu
plugin.activate('file_ops', level=20)

# Add delete image to the menu
FILE_OPS_ALLOW_DELETE_IMAGE = True

# Add delete info to the menu
FILE_OPS_ALLOW_DELETE_INFO = True

# support for settings bookmarks (key RECORD) while playing. Also
# auto bookmarking when playback is stopped
# plugin.activate('video.bookmarker', level=0)

# show some messages on the screen
plugin.activate('osd')

# control freevo over mbus
plugin.activate('mbus')

# special attributes for mbus address
MBUS_ADDR = {}


# ======================================================================
# Freevo remote control settings:
# ======================================================================

#
# Location of the lircrc file
#
# For remote control support, Freevo needs a lircrc file, like this:
#
# begin
#       prog = freevo
#       button = select
#       config = SELECT
# end
#
# Check contrib/lirc for examples and helpers/freevo2lirc.pl for a converter
# script.
#
LIRCRC = '/etc/freevo/lircrc'

if os.path.exists('/dev/lircd'):
    plugin.activate('input.lirc')
    

# plugin.activate('input.event_device')
EVDEV_NAME = 'Hauppauge PVR-250/350 IR remote'
EVDEV_DEVICE = '/dev/input/event0'
EVDEV_REPEAT_IGNORE = 400
EVDEV_REPEAT_RATE = 100

# ======================================================================
# Freevo TV settings:
# ======================================================================

#
# This is where recorded video is written.
#
TV_RECORD_DIR = None

TV_DATEFORMAT = '%e-%b' # Day-Month: 11-Jun
TV_TIMEFORMAT = '%H:%M' # Hour-Minute 14:05

plugin.activate('tv.genre')
