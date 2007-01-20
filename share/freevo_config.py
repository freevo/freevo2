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


########################################################################
# If you want to change some things for your personal setup, please
# write this in a file called local_conf.py, see that file for more info.
########################################################################

# Version information for the two config files. When the major version
# of the config file doesn't match, Freevo won't start. If the minor version
# is different, there will be only a warning

LOCAL_CONF_VERSION  = 8.00

# Description of changes in each new version
FREEVO_CONF_CHANGES = [
    (2.0,
     '''Changed xmame_SDL to just xmame'''), ]

LOCAL_CONF_CHANGES = [
    (8.00, '''Major config changes for 2.0. Please check freevo_config.py''' )
    ]

# NOW check if freevo.conf is up-to-date. An older version may break the next
# steps

FREEVO_CONF_VERSION = setup.CONFIG_VERSION

if int(str(CONF.version).split('.')[0]) != \
   int(str(FREEVO_CONF_VERSION).split('.')[0]):
    print "\nERROR: The version information in freevo_config.py does't"
    print 'match the version in %s.' % sysconfig.CONFIGFILE
    print 'please rerun "freevo setup" to generate a new freevo.conf'
    print_config_changes(FREEVO_CONF_VERSION, CONF.version,
                         FREEVO_CONF_CHANGES)
    sys.exit(1)

if int(str(CONF.version).split('.')[1]) != \
   int(str(FREEVO_CONF_VERSION).split('.')[1]):
    print 'WARNING: freevo_config.py was changed, please rerun "freevo setup"'
    print_config_changes(FREEVO_CONF_VERSION, CONF.version,
                         FREEVO_CONF_CHANGES)
    

# ======================================================================
# General freevo settings:
# ======================================================================

# MIXER SETTINGS
MAJOR_AUDIO_CTRL    = 'VOL'           # Freevo takes control over audio ctrl
                                      # 'VOL', 'PCM' 'OGAIN' etc.
CONTROL_ALL_AUDIO   = 1               # Freevo takes complete control of audio
MAX_VOLUME          = 90              # Set maximum volume level.
DEFAULT_VOLUME      = 40              # Set default volume level.
DEV_MIXER           = '/dev/mixer'    # mixer device 


# shutdown plugin
CONFIRM_SHUTDOWN    = 1               # ask before shutdown

SHUTDOWN_SYS_CMD = 'shutdown -h now'  # set this to 'sudo shutdown -h now' if
                                      # you don't have the permissions to
                                      # shutdown
RESTART_SYS_CMD  = 'shutdown -r now'  # like SHUTDOWN_SYS_CMD, only for reboot

ENABLE_SHUTDOWN_SYS = 0  # Performs a whole system shutdown at SHUTDOWN!
                         # For standalone boxes.


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
# Basic mouse support. It still needs much work and isn't working very
# good. E.g. you can't go a menu back, popups won't work and inside the
# player you have no control. Activate this if you want to help in the
# development of this feature. This only works when using sdl as gui engine.
#
INPUT_MOUSE_SUPPORT = 0

#
# Use Internet resources to fetch information?
# For example, Freevo can use CDDB for album information,
# the IMDB movie database for movie info, and Amazon for cover searches. 
# Set this to 0 if your computer isn't connected to a network.
#
USE_NETWORK = 1

#
# Umask setting for all files.
# 022 means only the user has write access. If you share your Freevo
# installation with different users, set this to 002
#
UMASK = 022

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

# basic input
plugin.activate('input')

# Items in the main menu.
plugin.activate('tv', level=10)
plugin.activate('video', level=20)
plugin.activate('audio', level=30)
plugin.activate('image', level=40)
plugin.activate('shutdown', level=50)

# FIXME: games is broken
# if CONF.xmame or CONF.snes:
#     plugin.activate('games', level=45)

# mixer
plugin.activate('mixer')

# add imdb search to the video item menu
# BEACON_FIXME:
# plugin.activate('video.imdb')

# delete file in menu
plugin.activate('file_ops', level=20)

# use mplayer for video playpack
# plugin.activate('video.mplayer')

# use mplayer for tv
# to use tvtime, put the following two lines in your local_conf.py:
# plugin.remove('tv.mplayer')
# plugin.activate('tv.tvtime')
# plugin.activate('tv.xine')

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

# You can change all this variables in the folder.fxd on a per folder
# basis
#
# Example:
# <freevo>
#   <folder title="Title of the directory" img-cover="nice-cover.png">
#     <setvar name="directory_autoplay_single_item" val="0"/>
#     <info>
#       <content>A small description of the directory</content>
#     </info>
#   </folder>
# </freevo>

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
# The following settings determine which features are available for
# which media types.
#
# If you set this variable in a folder.fxd, the value is 1 (enabled)
# or 0 (disabled).
# 
# Examples:
# To enable autoplay for audio and image files:
# DIRECTORY_AUTOPLAY_ITEMS = [ 'audio', 'image' ]
# To disable autoplay entirely:
# DIRECTORY_AUTOPLAY_ITEMS = []

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
# Directory containing images for tv shows. A tv show maches the regular
# expression VIDEO_SHOW_REGEXP, e.g. "Name 3x10 - Title". If an image
# name.(png|jpg) (lowercase) is in this directory, it will be taken as cover
# image
#
VIDEO_SHOW_DATA_DIR = None

#
# The list of filename suffixes that are used to match the files that
# are played wih MPlayer.
# 
VIDEO_SUFFIX = [ 'avi', 'mpg', 'mpeg', 'wmv', 'bin', 'rm',
                 'divx', 'ogm', 'vob', 'asf', 'm2v', 'm2p',
                 'mp4', 'viv', 'nuv', 'mov', 'iso',
                 'nsv', 'mkv', 'ts', 'rmvb', 'cue' ]


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
# Freevo games settings:
# ======================================================================

#
# MAME is an emulator for old arcade video games. It supports almost
# 2000 different games! The actual emulator is not included in Freevo,
# you'll need to download and install it separately. The main MAME
# website is at http://www.mame.net, but the version that is used here
# is at http://x.mame.net since the regular MAME is for Windows.
#
# SNES stands for Super Nintendo Entertainment System. Freevo relies
# on other programs that are not included in Freevo to play these games.
# 
# NEW GAMES SYSTEM :
# =================
# The GAMES_ITEMS structure is now build as follows :
# <NAME>, <FOLDER>, (<TYPE>, <COMMAND_PATH>, <COMMAND_ARGS>, <IMAGE_PATH>, \
# [<FILE_SUFFIX_FOR_GENERIC>])
# where :
#              - <TYPE> : Internal game types (MAME or SNES) or
#                         generic one (GENERIC)
#              - <COMMAND_PATH> : Emulator command
#              - <COMMAND_ARGS> : Arguments for the emulator
#              - <IMAGE_PATH>   : Optionnal path to the picture
#              - <FILE_SUFFIX_FOR_GENERIC> : If the folder use the GENERIC
#                                            type, then you must specify here
#                                        the file suffix used by the emulator
# GAMES_ITEMS = [ ('MAME', '/home/media/games/xmame/roms',     
#                ('MAME', '/usr/local/bin/xmame.SDL', '-fullscreen -modenumber 6', 
#                 '/home/media/games/xmame/shots', None)),
#               ('SUPER NINTENDO', '/home/media/games/snes/roms', 
#                ('SNES', '/usr/local/bin/zsnes', '-m -r 3 -k 100 -cs -u', '', None )),
#               ('Visual Boy Advance', '/home/media/games/vba/roms/',
#                ('GENERIC', '/usr/local/vba/VisualBoyAdvance', ' ', '', [ 'gba' ] )),
#               ('MEGADRIVE', '/home/media/games/megadrive/roms', 
#                ('GENESIS', '/usr/local/bin/generator-svgalib', '', '', '' )) ]

GAMES_ITEMS = None


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
# Imlib2 (X only), fb (framebuffer) and Bmovl. The Bmovl displays also need
# a background video set in GUI_BACKGROUND_VIDEO.
#
GUI_DISPLAY = 'imlib2'

# Some special settings for the different displays
if CONF.display == 'mga':
    GUI_OVERSCAN_X = 20
    GUI_OVERSCAN_Y = 10
    GUI_DISPLAY = 'fb'

if CONF.display in ( 'directfb', 'dfbmga' ):
    GUI_OVERSCAN_X = 50
    GUI_OVERSCAN_Y = 50
    GUI_DISPLAY = 'sdl'

if CONF.display == 'dxr3':
    GUI_OVERSCAN_X = 65
    GUI_OVERSCAN_Y = 45
    GUI_DISPLAY = 'sdl'
    
#
# Stop the osd before playing a movie with xine or mplayer. Some output
# devices need this. After playback, the osd will be restored
#
GUI_STOP_WHEN_PLAYING = 0

if CONF.display in ( 'directfb', 'dfbmga', 'dxr3', 'dga' ):
    GUI_STOP_WHEN_PLAYING = 1

#
# Video file for bmovl display
#
GUI_BACKGROUND_VIDEO = ''

#
# Fade steps on application change.
#
GUI_FADE_STEPS = 10

#
# XML file for the skin. If GUI_XML_FILE is set, this skin will be
# used, otherwise the skin will rememeber the last choosen skin.
#
GUI_XML_FILE         = ''
GUI_DEFAULT_XML_FILE = 'blurr'

#
# Select a way when to switch to text view even if a image menu is there
# 
# 1 = Force text view when all items have the same image and there are no
#     directories
# 2 = Ignore the directories, always switch to text view when all images
#     are the same
#
GUI_FORCE_TEXTVIEW_STYLE = 1

#
# Force text view for the media menu
# (The media menu is the first menu displayed for video, audio, images 
# and games). 
#
GUI_MEDIAMENU_FORCE_TEXTVIEW = 0

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
    

# ======================================================================
# Freevo TV settings:
# ======================================================================

#
# This is where recorded video is written.
#
TV_RECORD_DIR = None

TV_DATEFORMAT     = '%e-%b' # Day-Month: 11-Jun
TV_TIMEFORMAT     = '%H:%M' # Hour-Minute 14:05
TV_DATETIMEFORMAT = '%A %b %d %I:%M %p' # Thursday September 24 8:54 am

# ======================================================================
# Internal stuff, you shouldn't change anything here unless you know
# what you are doing
# ======================================================================

#
# Config for xml support in the movie browser
# the regexp has to be with ([0-9]|[0-9][0-9]) so we can get the numbers
#
VIDEO_SHOW_REGEXP = "s?([0-9]|[0-9][0-9])[xe]([0-9]|[0-9][0-9])[^0-9]"

#
# XML TV Logo Location
#
# Use the "makelogos.py" script to download all the
# Station logos into a directory. And then put the path
# to those logos here
#
# FIXME: OS_CACHEDIR is gone
if 0 and os.path.isdir(OS_CACHEDIR + '/xmltv/logos'):
    TV_LOGOS = OS_CACHEDIR + '/xmltv/logos'
else:
    if not os.path.isdir('/tmp/freevo/xmltv/logos'):
        os.makedirs('/tmp/freevo/xmltv/logos')
    TV_LOGOS = '/tmp/freevo/xmltv/logos'

#
# catch errors
#
FREEVO_EVENTHANDLER_SANDBOX = 1
