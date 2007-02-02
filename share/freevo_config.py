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
plugin.activate('video', level=20)
plugin.activate('audio', level=30)
plugin.activate('image', level=40)
plugin.activate('shutdown', level=50)

# shutdown plugin config
SHUTDOWN_CONFIRM = True               # ask before shutdown
SHUTDOWN_SYS_CMD = 'shutdown -h now'  # or 'sudo shutdown -h now'
RESTART_SYS_CMD  = 'shutdown -r now'  # like SHUTDOWN_SYS_CMD, only for reboot
SHUTDOWN_SYS_DEFAULT = False          # Performs a whole system shutdown at SHUTDOWN!

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
plugin.activate('video.bookmarker', level=0)

# show some messages on the screen
plugin.activate('osd')

# control freevo over mbus
plugin.activate('mbus')

# special attributes for mbus address
MBUS_ADDR = {}


# ======================================================================
# Freevo directory settings:
# ======================================================================

#
# Should directories sorted by date instead of filename?
# 0 = No, always sort by filename.
# 1 = Yes, sort by date
# 2 = No, don't sory by date for normal directories, 
#     but sort by date for TV_RECORD_DIR.
#
DIRECTORY_SORT_BY_DATE = 2

#
# Should directory items be sorted in reverse order?
#
DIRECTORY_REVERSE_SORT = 0

#
# Should we use "smart" sorting?
# Smart sorting ignores the word "The" in item names.
#
DIRECTORY_SMART_SORT = 0

#
# Should Freevo autoplay an item if only one item is in the directory?
#
DIRECTORY_AUTOPLAY_SINGLE_ITEM = 1

#
# Force the skin to use a specific layout number. -1 == no force. The layout
# toggle with DISPLAY will be disabled
#
DIRECTORY_FORCE_SKIN_LAYOUT = -1

#
# Format string for the audio item names. 
#
# Possible strings:
# a = artist, n = tracknumber, t = title, y = year, f = filename
#
# Example:
# This will show the title and the track number:
# DIRECTORY_AUDIO_FORMAT_STRING = '%(n)s - %(t)s'
#
DIRECTORY_AUDIO_FORMAT_STRING = '%(t)s'

#
# Use media id tags to generate the name of the item. This should be
# enabled all the time. It should only be disabled for directories with 
# broken tags.
#
DIRECTORY_USE_MEDIADB_NAMES = 1

#
# Make all items a playlist. So when one is finished, the next one will
# start. It's also possible to browse through the list with UP and DOWN
#
DIRECTORY_CREATE_PLAYLIST      = [ 'audio', 'image' ]

#
# Add playlist files ('m3u') to the directory
#
DIRECTORY_ADD_PLAYLIST_FILES   = [ 'audio', 'image' ]

#
# Add the item 'Random Playlist' to the directory
#
DIRECTORY_ADD_RANDOM_PLAYLIST  = [ 'audio' ]

#
# Make 'Play' not 'Browse' the default action when only items and not
# subdirectories are in the directory
#
DIRECTORY_AUTOPLAY_ITEMS       = [ ]


# ======================================================================
# Freevo movie settings:
# ======================================================================

#
# Where the movie files can be found.
# This is a list of items (e.g. directories, fxd files). The items themselves
# can also be a list of (title, file)
#
# Example: VIDEO_ITEMS = [ ('action movies', '/files/movies/action'),
#                          ('funny stuff', '/files/movies/comedy') ]
#
# Some people access movies on a different machine using an automounter.
# To avoid timeouts, you can specify the machine name in the directory
# to check if the machine is alive first
# Directory myserver:/files/server-stuff will show the item for the
# directory /files/server-stuff if the computer myserver is alive.
#
VIDEO_ITEMS = None

#
# The list of filename suffixes that are used to match the files that
# are played wih MPlayer.
# 
VIDEO_SUFFIX = [ 'avi', 'mpg', 'mpeg', 'wmv', 'bin', 'rm',
                 'divx', 'ogm', 'vob', 'asf', 'm2v', 'm2p',
                 'mp4', 'viv', 'nuv', 'mov', 'iso',
                 'nsv', 'mkv', 'ts', 'rmvb', 'cue' ]

#
# Config for xml support in the movie browser
# the regexp has to be with ([0-9]|[0-9][0-9]) so we can get the numbers
#
VIDEO_SHOW_REGEXP = "s?([0-9]|[0-9][0-9])[xe]([0-9]|[0-9][0-9])[^0-9]"


# ======================================================================
# Freevo audio settings:
# ======================================================================

#
# Where the Audio (mp3, ogg) files can be found.
# This is a list of items (e.g. directories, fxd files). The items itself
# can also be a list of (title, file)
#
# To add webradio support, add fxd/webradio.fxd to this list
#
AUDIO_ITEMS = None

#
# The list of filename suffixes that are used to match the files that
# are played as audio.
# 
AUDIO_SUFFIX     = [ 'mp3', 'ogg', 'wav','m4a', 'wma', 'aac', 'flac', 'mka',
                     'ac3' ]

#
# Show video files in the audio menu (for music-videos)
#
AUDIO_SHOW_VIDEOFILES = False

plugin.activate('audio.artist')

# ======================================================================
# Freevo image viewer settings:
# ======================================================================

#
# Where image files can be found.
# This is a list of items (e.g. directories, fxd files). The items itself
# can also be a list of (title, file)
#
IMAGE_ITEMS = None

#
# The list of filename suffixes that are used to match the files that
# are used for the image viewer.
# 
IMAGE_SUFFIX = [ 'jpg','gif','png', 'jpeg','bmp','tiff','psd' ]


#
# Mode of the blending effect in the image viewer between two images
# Possible values are:
#
# None: no blending
# -1    random effect
#  0    alpha blending
#  1    wipe effect
#
IMAGEVIEWER_BLEND_MODE = -1
    
#
# What information to display by pressing DISPLAY.
# You can add as many lists as you want and the viewer will toggle
# between no osd and the lists.
#
# Warning: this list may change in future versions of Freevo to support
# nice stuff like line breaks.
#
IMAGEVIEWER_OSD = [
    # First OSD info
    [ (_('Title')+': ',      'name'),
      (_('Description')+': ','description'),
      (_('Author')+': ',     'author') ],

    # Second OSD info
    [ (_('Title')+': ',    'name'),
      (_('Date')+': ' ,    'date'),
      ('W:',               'width'),
      ('H:',               'height'),
      (_('Model')+': ',    'hardware'),
      (_('Software')+': ', 'software') ]
    ]
    

#
# Default duration for images in a playlist. If set to 0, you need
# to press a button to get to the next image, a value > 0 is the time
# in seconds for an auto slideshow
#
IMAGEVIEWER_DURATION = 0

# ======================================================================
# Freevo GUI settings:
# ======================================================================

#
# GUI default font. It is only used for debug/error stuff, not regular
# skinning.
#
GUI_FONT_DEFAULT_NAME = 'Vera'
GUI_FONT_DEFAULT_SIZE = 18

#
# System Path to search for fonts not included in the Freevo distribution
#
GUI_FONT_PATH  = [ '/usr/X11R6/lib/X11/fonts/truetype/' ]

#
# Font aliases 
# All names must be lowercase! All alternate fonts must be in './share/fonts/'
#
GUI_FONT_ALIASES = { 'Arial_Bold' : 'VeraBd' }

#
# Overscan on the tv output. Set this values if you can't see everything
# from Freevo on the tv screen.
#
GUI_OVERSCAN_X = 0
GUI_OVERSCAN_Y = 0

#
# Output display to use. Possible values are SDL (using pygame),
# Imlib2 (X only) and fb (framebuffer).
#
GUI_DISPLAY = 'imlib2'

#
# Special settings for fb display
#
GUI_DISPLAY_FB_NORM = 'pal'             # pal or ntsc
GUI_DISPLAY_FB_MODE = ''                # set to 'mga' for special G400 support

#
# Window / Display size
#
GUI_WIDTH  = 800
GUI_HEIGHT = 600


#
# Fade steps on application change.
#
GUI_FADE_STEPS = 10

#
# XML file for the skin. If GUI_XML_FILE is set, this skin will be
# used, otherwise the skin will rememeber the last choosen skin.
#
GUI_XML_FILE = 'blurr'

GUI_DFB_LAYER = 0

# start GUI in fullscreen mode
GUI_FULLSCREEN = False

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
