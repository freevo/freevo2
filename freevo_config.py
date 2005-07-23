# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# freevo_config.py - System configuration
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#    This file contains the freevo settings. To change the settings
#    you can edit this file, or better, put a file named local_conf.py
#    # in the same directory and add your changes there.  E.g.: when
#    you # want a oss as mplayer audio out, just put
#    "MPLAYER_AO_DEV = # 'oss'" in local_conf.py
#
# How config files are loaded:
#  
# [$freevo-bindir/ is the directory where the freevo start-script is 
# located (i.e. the "shipping copy dir"). This can be any directory, e.g. 
# the download directory or /usr/local] 
#  
# [$cwd/ is the directory the user started freevo from. This can be 
# $freevo-bindir/, or any other directory] 
#  
# 1) freevo.conf is not shipped, but it is required and must be generated 
# using ./configure before freevo can be used. 
#  
# 2) freevo.conf is searched for in ['$cwd/', '~/.freevo/', 
# '/etc/freevo/', $freevo-bindir/]. The first one found is loaded. 
#  
# 3) freevo_config.py is always loaded from $freevo-bindir/, it is not 
# supposed to be changed by the user. It has a format version number in 
# the format "MAJOR.MINOR", e.g. "2.3". The version number reflects the 
# config file format, *not* the Freevo version number. 
#  
# 4) local_conf.py is searched for in ['$cwd/', '~/.freevo', 
# '/etc/freevo/', $freevo-bindir/]. The first one found is loaded. It is 
# not a required file. The search is independent of where freevo.conf was 
# found. 
#  
# 5) The same logic as in 4) applies for local_skin.xml. 
#  
# 6) The version MAJOR numbers must match in freevo_config.py and 
# local_conf.py, otherwise it is an error. 
#  
# 7) The version MINOR number is used for backwards-compatible changes, 
# i.e. when new options are added that have reasonable default values. 
#  
# 8) A warning is issued if freevo_config.py.MINOR > local_conf.py.MINOR. 
#  
# 9) It is an error if local_conf.py.MINOR > freevo_config.py.MINOR since 
# the user most likely did not intend to use a recent local_conf.py with 
# an old Freevo installation. 
#  
# 10) There is a list of change descriptions in freevo_config.py, 
# one per MAJOR.MINOR change. The user is informed of what has 
# changed between his local_conf.py and the new freevo_config.py format if 
# they differ in version numbers.
#
#
#
# Developer Notes:
#    The CVS log isn't used here. Write changes directly in this file
#    to make it easier for the user. Make alos sure that you insert new
#    options also in local_conf.py.example
#
# Todo:
#    o a nice configure or install script to ask these things
#    o different settings for MPG, AVI, VOB, etc
#
# -----------------------------------------------------------------------
#
# Changes:
#    o Generate ROM_DRIVES from /etc/fstab on startup
#    o Added FREEVO_CONF_VERSION and LOCAL_CONF_VERSION to keep the three
#      different files on sync
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
    (5.00, '''
    Changed some config variables. Use \'./freevo convert_config\' to
    convert your local_conf.py to change the variable names
    '''),
    (5.01, '''
    Add AUDIO_SHOW_VIDEOFILES to enable video files in the audio menu
    '''),
    (5.02, '''
    Add XINE_ARGS_DEF to set xine arguments and GUI_BUSYICON_TIMER to show
    a busy icon when the menu takes too much time building
    '''),
    (5.03, '''
    Add UMASK to set umask for files in vfs
    ''' ),
    (5.04, '''
    SKIN_XML_FILE set to nothing as default, SKIN_START_LAYOUT is removed.
    When GUI_XML_FILE is not set, the skin will remember the last settings
    '''),
    (5.05, '''
    Use MMPYTHON_CREATE_MD5_ID with current mmpython cvs to have a second
    way to generate the disc ids in case they are not unique on your system
    '''),
    (5.06, '''
    Add MEDIAINFO_USE_MEMORY. Setting this variable will keep all cache
    files in memory. Startup will be slower, but for large directories, this
    will speed up entering the dir
    '''),
    (5.07, '''
    Add MENU_ARROW_NAVIGATION to change navigation style. New one is default
    now. Also added GUI_FONT_PATH to search for fonts
    '''),
    (5.08, '''
    Change MENU_ARROW_NAVIGATION to old style and make blurr the new default
    skin. Also added RESTART_SYS_CMD, OSD_DIM_TEXT and
    OSD_UPDATE_COMPLETE_REDRAW.
    '''),
    (5.09, '''
    Add CACHE_IMAGES to turn off image caching. A new variable is
    IMAGEVIEWER_BLEND_MODE to control the blending effect in the image viewer
    '''),
    (5.11, '''
    Add IMAGEVIEWER_OSD to customize the osd and VIDEO_AUTOJOIN to auto join
    movies with more than one file
    '''),
    (5.12, '''
    Added TV_RECORD_SERVER_UID to set the uid for the recordserver and
    TV_RECORDFILE_SUFFIX for the suffix. If your TV_RECORD_FILEMASK contains
    the suffix, please remove it here
    '''),
    (5.13, '''
    Added TV_RECORD_SERVER_GID to set the gid for the recordserver. If you
    use TV_RECORD_SERVER_UID, the gui _must_ match one of the users gids
    '''),
    (5.14, '''
    Add IMAGEVIEWER_DURATION for auto slideshows
    ''' ),

    (6.00, '''
    Renamed all SKIN_* and OSD_* variables to GUI_*, removed the VideoGroups,
    logic is now in TV_CHANNELS. Removed old not needed variables (please
    check this file). The default audio device is now alsa not oss. 
    Some record and tv variables changed (like padding). See this sections in
    the freevo_config.py for details. Also add three mplayer filter
    MPLAYER_RESAMPLE_AUDIO, MPLAYER_VF_INTERLACED, MPLAYER_VF_PROGRESSIVE.
    ''' ),
    (7.00, '''
    Reworked the vfs/mediadb code. You should either start with a clean vfs
    or run the cache helper to clean up the old stuff (you can stop the helper
    when it starts to scan the directories). If you also want to use an older
    version of freevo, you should create a new vfs for Freevo 2.0. To do so,
    set vfs_dir = /path/to/vfs in your freevo.conf.
    ''' ),
    (8.00, '''
    Reworked event handling. The Event class has no parameter arg anymore.
    The args are now auto-detected based on the arguments of the init call.
    So instead if using Event(FOO, arg=1), you now need to use Event(FOO, 1).
    ''' )
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

AUDIO_DEVICE        = '/dev/dsp'      # e.g.: /dev/dsp0, /dev/audio
AUDIO_INPUT_DEVICE  = '/dev/dsp1'     # e.g.: /dev/dsp0, /dev/audio
MAJOR_AUDIO_CTRL    = 'VOL'           # Freevo takes control over audio ctrl
                                      # 'VOL', 'PCM' 'OGAIN' etc.
CONTROL_ALL_AUDIO   = 1               # Freevo takes complete control of audio
MAX_VOLUME          = 90              # Set maximum volume level.
DEFAULT_VOLUME      = 40              # Set default volume level.
TV_IN_VOLUME        = 60              # Set this to your preferred level 0-100.
VCR_IN_VOLUME       = 90              # If you use different input from TV
DEV_MIXER           = '/dev/mixer'    # mixer device 

START_FULLSCREEN_X  = 0               # Start in fullscreen mode if using x11

CONFIRM_SHUTDOWN    = 1               # ask before shutdown

#
# Physical ROM drives, multiple ones can be specified
# by adding comma-seperated and quoted entries.
#
# Format [ ('mountdir1', 'devicename1', 'displayed name1'),
#          ('mountdir2', 'devicename2', 'displayed name2'), ...]
#
# Set to None to autodetect drives in during startup from /etc/fstab,
# set to [] to disable rom drive support at all
#
ROM_DRIVES = None

#
# hide discs from the wrong menu (e.g. VCDs in audio menu) and empty discs
#
HIDE_UNUSABLE_DISCS = 1               

#
# Attempt to set the speed of the ROM drive. A good value for keeping the
# drive silent while playing movies is 8.
#
ROM_SPEED = 0                

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
# HOST_ALIVE_CHECK tests if the given host is online.
# Will be used to avoid extremely long automounter timeouts.
#
HOST_ALIVE_CHECK = 'ping -c 1 -W 1 %s > /dev/null 2>&1'

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

#
# Use md5 in mmpython to create unique disc ids. Enable this if you have
# problems with different discs having the same id.
# FIXME: Why is this not used anymore?
#
MMPYTHON_CREATE_MD5_ID = 0

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
# plugin.remove(rom_plugins['image']) will remove the rom drives from the
#   image main menu,
# plugin.remove('rom_drives.rom_items') will remove the rom drives from all
#   menus

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


# ROM drive support
plugin.activate('rom_drives')

# autostarter when inserting roms while Freevo is in the MAIN MENU
plugin.activate('rom_drives.autostart')

# add the rom drives to each sub main menu
rom_plugins = {}
for t in ('video', 'audio', 'image', 'games'):
    rom_plugins[t] = plugin.activate('rom_drives.rom_items', type=t, level=50)


# mixer
plugin.activate('mixer')

# add imdb search to the video item menu
plugin.activate('video.imdb')

# list of regexp to be ignored on a disc label
IMDB_REMOVE_FROM_LABEL = ('season[\._ -][0-9]+', 'disc[\._ -][0-9]+',
                          'd[\._ -][0-9]+', 'german')

# list of words to ignore when searching based on a filename
IMDB_REMOVE_FROM_SEARCHSTRING = ('the', 'a')

# When searching for a movie title in imdb, should the result be
# autoaccepted if it is only one hit?
# 0 = show menu even if it is only one hit (gives you an opportunity to cancel)
# 1 = autoaccept
IMDB_AUTOACCEPT_SINGLE_HIT = True

# delete file in menu
plugin.activate('file_ops', level=20)

# use mplayer for video playpack
plugin.activate('video.mplayer')

# use mplayer for audio playpack
plugin.activate('audio.mplayer')

# make it possible to detach the player
#  argument tells the plugin to show the 
#  detachbar
plugin.activate('audio.detach', level=20, args=(True,))

# use mplayer for tv
# to use tvtime, put the following two lines in your local_conf.py:
# plugin.remove('tv.mplayer')
# plugin.activate('tv.tvtime')
plugin.activate('tv.mplayer')

# control an external tv tuner using irsend or another command
# to use this you must reassign plugin_external_tuner in local_conf.py:
# plugin_external_tuner = plugin.activate('tv.irsend_generic',
#                                         args=('...', '...', ))
# Please see each irsend plugin for individual arguments and be sure to
# alter VIDEO_GROUPS to tell a VideoGroup to use it (tuner_type='external').
plugin_external_tuner = 0

# support for settings bookmarks (key RECORD) while playing. Also
# auto bookmarking when playback is stopped
plugin.activate('video.bookmarker', level=0)

# show some messages on the screen
plugin.activate('tiny_osd')

# For recording tv
#

plugin.activate('record.fxdfile')
plugin.activate('record.thumbnail')


#
# Use ivtv_record instead if you have an ivtv based card (PVR-250/350)
# and want freevo to do everthing for you.  To use you need to set the 
# following two lines:
#
# plugin.remove('record.generic_record')
# plugin.activate('record.ivtv_record')

# TV menu plugin to view scheduled recordings
# plugin.activate('tv.scheduled_recordings')

# TV menu plugin to view and edit favorites
# plugin.activate('tv.view_favorites')

# TV menu plugin to manually schedule recordings
# plugin.activate('tv.manual_record')

#
# Enable this for joystick support:
# plugin.activate('joy')

# control freevo over mbus
plugin.activate('mbus')


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
DIRECTORY_USE_MEDIAID_TAG_NAMES = 1

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
VIDEO_MPLAYER_SUFFIX = [ 'avi', 'mpg', 'mpeg', 'wmv', 'bin', 'rm',
                         'divx', 'ogm', 'vob', 'asf', 'm2v', 'm2p',
                         'mp4', 'viv', 'nuv', 'mov', 'iso',
                         'nsv', 'mkv', 'ts', 'rmvb' ]

#
# The list of filename suffixes that are used to match the files that
# are played wih Xine.
# 
VIDEO_XINE_SUFFIX = [ 'avi', 'mpg', 'mpeg', 'rm', 'divx', 'ogm',
                      'asf', 'm2v', 'm2p', 'mp4', 'mov', 'cue',
                      'ts', 'iso', 'vob', 'rmvb' ]

#
# Preferred video player
#
VIDEO_PREFERED_PLAYER = 'mplayer'

#
# try to detect a movie with more than one file and join them as one
# item
#
VIDEO_AUTOJOIN = 1

#
# try to find out if deinterlacing is needed or not
#
VIDEO_INTERLACING = 1


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
# Regular expression used to recognize filenames which are likely to be 
# covers for an album 
#
# This will match front.jpg and cover-f.jpg, but not back.jpg nor cover-b.jpg
#
AUDIO_COVER_REGEXP = 'front|-f'

#
# Preferred audio player
#
AUDIO_PREFERED_PLAYER = 'mplayer'

#
# Show video files in the audio menu (for music-videos)
#
AUDIO_SHOW_VIDEOFILES = False

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
# The viewer now supports a new type of menu entry, a slideshow file.
# It also has the slideshow alarm signal handler for automated shows.
# It uses a new configuration option:
#
IMAGE_SSHOW_SUFFIX = [ 'ssr' ]


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

#
# These settings are used for the MAME arcade emulator:
#

# Priority of the game process
# 0 = Don't change the priority
# >0 - Lower priority
# <0 - Higher priority
#
GAMES_NICE        = -20
 
# 
# MAME cache directory
#
GAMES_MAME_CACHE = '%s/romlist-%s.pickled' % (FREEVO_CACHEDIR, os.getuid())


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
# Execute a script on GUI startup.
#
GUI_SDL_EXEC_AFTER_STARTUP = ""

#
# Execute a script on GUI close.
#
GUI_SDL_EXEC_AFTER_CLOSE = ""

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
    
#
# Set the Joy device to 0 to disable, 1 for js0, 2 for js1, etc...
# Supports as many buttons as your controller has,
# but make sure there is a corresponding entry in JOY_CMDS.
# You will also need to plugin.activate('joy').
# FYI: new kernels use /dev/input/jsX, but joy.py will fall back on /dev/jsX
#
JOY_DEV = 0
JOY_CMDS = {
    'up'             : 'UP',
    'down'           : 'DOWN',
    'left'           : 'LEFT',
    'right'          : 'RIGHT',
    'button 1'       : 'PLAY',
    'button 2'       : 'PAUSE',
    'button 3'       : 'STOP',
    'button 4'       : 'ENTER',
    }



# ======================================================================
# TVtime settings:
# ======================================================================

#
# Location of the TV time program
# Default: Use the value in freevo.conf
# 
TVTIME_CMD = CONF.tvtime


# ======================================================================
# MPlayer settings:
# ======================================================================

MPLAYER_CMD = CONF.mplayer
    
MPLAYER_AO_DEV       = 'alsa'            # e.g.: oss,sdl,alsa, see mplayer docs

if CONF.display == 'x11':
    MPLAYER_VO_DEV       = 'xv,sdl,x11,' # X11 drivers in order of preference
else:
    MPLAYER_VO_DEV       = CONF.display  # e.g.: x11,mga, see mplayer docs

MPLAYER_VO_DEV_OPTS  = ''	         # e.g.: ':some_var=vcal'

DVD_LANG_PREF        = 'en,se,no'        # Order of preferred languages on DVD.
DVD_SUBTITLE_PREF    = ''                # Order of preferred subtitles on DVD.

# Priority of mplayer process. 0 is unchanged, <0 is higher prio, >0 lower
# prio. prio <0 has no effect unless run as root.
MPLAYER_NICE         = -20             

if CONF.display in ( 'directfb', 'dfbmga' ):
    MPLAYER_ARGS_DEF     = ('-autosync 100 -nolirc ' +
                            '-autoq 100 -fs ')
else:
    MPLAYER_ARGS_DEF     = (('-autosync 100 -nolirc -autoq 100 -screenw %s '
                             + '-screenh %s -fs') % (CONF.width, CONF.height))


#
# Mplayer options to use the software scaler. If your CPU is fast enough, you
# should use a software scaler. You can disable it later for some larger files
# with the mplayer option '-nosws'. If you have -framedrop or -hardframedrop
# as mplayer option, the software scaler will also not be used.
# The bmovl plugin depends on a software scaler, so you should give it a try
#
MPLAYER_SOFTWARE_SCALER = "-subfont-text-scale 15 -sws 2 -vf scale=%s:-2,"\
                          "expand=%s:%s -font /usr/share/mplayer/fonts/"\
                          "font-arial-28-iso-8859-2/font.desc" % \
                          ( CONF.width, CONF.width, CONF.height )

#
# Mplayer arguments for different media formats. (eg DVDs, CDs, AVI files, etc)
# Uses a default value if nothing else matches.
#
MPLAYER_ARGS = { 'dvd'    : '-cache 8192',
                 'vcd'    : '-cache 4096',
                 'cd'     : '-cache 1024 -cdda speed=2',
                 'tv'     : '-nocache',
                 'ivtv'   : '-cache 8192',
                 'dvb'    : '-cache 1024',
                 'avi'    : '-cache 5000 -idx',
                 'rm'     : '-cache 5000 -forceidx',
                 'rmvb'   : '-cache 5000 -forceidx',
                 'default': '-cache 5000',
                 'webcam' : ('tv:// -tv driver=v4l:width=352:height=288:' +
                             'outfmt=yuy2:device=/dev/video2')
                 }

#
# Number of seconds before seek value times out. This is used when
# seeking a specified number of minutes into a movie. If you make
# a mistake or change your mind, the seek value will timeout after
# this many seconds.
#
MPLAYER_SEEK_TIMEOUT = 8

#
# Autocrop files when playing. This is useful for files in 4:3 with black
# bars on a 16:9 tv
#
MPLAYER_AUTOCROP = 0

#
# Try to set correct 'delay' and 'mc' values for mplayer based on the delay
# from mmpython. 
#
# This should correct av sync problems with mplayer for some files, but 
# may also break things. (I don't know, that's why it's disabled by default). 
# WARNING: When seeking, the playback is out of sync for some seconds! 
#
MPLAYER_SET_AUDIO_DELAY = 0

#
# Resample audio channel if the samplerate is lower than 40kHz to a values
# between 41100Hz and 48000Hz. This is needed for some external digital
# receiver. It will only work if mmpython can detect the samplerate
#
MPLAYER_RESAMPLE_AUDIO = 0

#
# Mplayer video filter for interlaced or progressive videos. If you have
# a slow pc, do not use post processing
# MPLAYER_VF_INTERLACED  = ''
# MPLAYER_VF_PROGRESSIVE = 'pp=fd'
# For pal and dvb-t recordings, the following looks good
# MPLAYER_VF_INTERLACED  = 'pp=md/de,phase=U'
#
MPLAYER_VF_INTERLACED  = 'pp=de/fd'
MPLAYER_VF_PROGRESSIVE = 'pp=de'


# ======================================================================
# Xine settings:
# ======================================================================

# You need xine-ui version greater 0.9.21 to use the all the features
# of the xine plugin

XINE_COMMAND = ''

if CONF.display in ('mga', 'fbdev') and CONF.fbxine:
    XINE_VO_DEV  = 'vidixfb'
    XINE_COMMAND = CONF.fbxine
    
if CONF.display == 'dxr3' and CONF.fbxine:
    XINE_VO_DEV  = 'dxr3'
    XINE_COMMAND = CONF.fbxine
    
if CONF.display == 'x11' and CONF.xine:
    XINE_VO_DEV  = 'xv'
    XINE_COMMAND = ('%s --hide-gui -pq -g -B --geometry %sx%s+0+0 ' + \
                    '--no-splash') % (CONF.xine, CONF.width, CONF.height)

XINE_ARGS_DEF = '--post=pp:quality=10;expand'

XINE_AO_DEV = 'alsa'    # alsa or oss

if XINE_COMMAND:
    plugin.activate('video.xine')
if CONF.fbxine:
    plugin.activate('audio.xine')

XINE_USE_VDR = 0

# ======================================================================
# Freevo TV settings:
# ======================================================================

#
# This is where recorded video is written.
#
TV_RECORD_DIR = None

#
# Size (in MB) of the timeshift buffer. (ie: how long you can pause tv for.)  
# This is set to a low default because the default buffer location is 
# under FREEVO_CACHEDIR and we don't want to blow /var or /tmp.
#
TV_DATEFORMAT     = '%e-%b' # Day-Month: 11-Jun
TV_TIMEFORMAT     = '%H:%M' # Hour-Minute 14:05
TV_DATETIMEFORMAT = '%A %b %d %I:%M %p' # Thursday September 24 8:54 am

#
# This is the filename format for files recorded using Freevo.
# You can use any of the strftime variables in it, provided you
# put two '%%' at the beginning. 
# 
# Some examples:
# %%A - Full weekday name.
# %%H - Hour (24-hour clock) as a decimal number [00,23].
# %%M - Minute as a decimal number [00,59].
# %%m - Month as a decimal number [01,12].
# %%d - Day of the month as a decimal number [01,31].
# %%p - Locale's equivalent of either AM or PM.
# 
# More can be found at: http://www.python.org/doc/current/lib/module-time.html
#
TV_RECORD_FILEMASK = '%%m-%%d %%H:%%M %(progname)s - %(title)s'

#
# If the recordserver runs as root, set the uid to the given one
# after startup. The gui must also match one of the users group ids
#
TV_RECORD_SERVER_UID = 0
TV_RECORD_SERVER_GID = 0

#
# start every recording X minutes before scheduled,
# and stop X minutes after scheduled - default to zero minutes.
# This must be a value in seconds although at the moment only has
# the percision of one minute.
#
TV_RECORD_START_PADDING = 2 * 60
TV_RECORD_STOP_PADDING  = 5 * 60

#
# TV capture size for viewing and recording. Max 768x480 for NTSC,
# 768x576 for PAL. Set lower if you have a slow computer!
#
# For the 'tvtime' TV viewing application, only the horizontal size is used.
# Set the horizontal size to 400 or 480 if you have a slow (~500MHz) computer,
# it still looks OK, and the picture will not be as jerky.
# The vertical size is always either fullscreen or 480/576 (NTSC/PAL)
# for tvtime.
#
TV_VIEW_SIZE = (640, 480)
TV_REC_SIZE = (320, 240)   # Default for slower computers

#
# Input formats for viewing and recording. The format affect viewing
# and recording performance. It is specific to your hardware, so read
# the MPlayer docs and experiment with mplayer to see which one fits
# your computer best.
#
TV_VIEW_OUTFMT = 'yuy2'   # Better quality, slower on pure FB/X11
TV_REC_OUTFMT  = 'yuy2'

#
# FREQUENCY_TABLE - This is only used when Freevo changes the channel natively.
# This is only the case if you are using V4L2 and any of the following plugins:
# timeshift, ivtv_record, ivtv_basic_tv.
# For the standard frequancy tables see src/tv/freq.py.  To add your own just 
# replace tuner_id in the following example with a valid tuner id (ie: '5' or
# 'BBC1') and a frequency in KHz.  You may have as many entries as you like,
# anything here will simply override a corresponding entry in your standard
# frequency table and you can also have entries here that are not present in
# there.
#
FREQUENCY_TABLE = {
    'tuner_id'   :    55250,
}

#
# TV Channels. This list contains a mapping from the displayed channel name
# to the actual channel name as used by the TV watching application.
# The display name must match the names from the XMLTV guide,
# and the TV channel name must be what the tuner expects (usually a number).
#
# The TV menu is supposed to be supported by the XMLTV application for
# up to date listings, but can be used without it to just display
# the available channels.
#
# Format: [('xmltv channel id', 'freevo display name', 'tv channel name'), ...]
#
# If this variable is set to None (default), Freevo will try to auto-detect
# the channel list based on the xmltv file. This doesn't work for all
# xmltv grabber, e.g. the German list doesn't contain station lists. In this
# case Freevo will output the possible list for you to add them manually.
#
# If auto-detection doesn't work or you want to edit the list, run
# freevo tv_grab -query.
#
# If you don't have a tv card, you may also want to add plugin.remove('tv') to
# remove the whole tv menu.
#
# All channels listed here will be displayed on the TV menu, even if they're
# not present in the XMLTV listing.
# 
# The TV_CHANNELS-list can look like this:
#
# TV_CHANNELS = [('21', 'SVT1',              'E5'),
#                ('22', 'SVT2',              'E3'),
#                ('26', 'TV3',               'E10'),
#                ('27', 'TV4',               'E6'),
#                ('10', 'Kanal 5',           'E7'),
#                ('14', 'MTV Europe',        'E11') ]
#
TV_CHANNELS = []

#
# If you would like to change the display format of your channels and prefer
# not to list your entire TV_CHANNELS then you can apply rules using 
# TV_CHANNELS_DISPLAY_FORMAT.  This defaults to the plain name of the channel
# in order to not mess with TV_CHANNELS. 
# Valid keywords are:
#     %(id)s
#     %(tunerid)s
#     %(name)s
# For example, if you prefer to see the channel number with the name you 
# could use '%(tunerid)s %(name)s'.
#
TV_CHANNELS_DISPLAY_FORMAT = '%(name)s'

#
# Sometimes we can't control the contents of our XMLTV file and it may contain
# channels we don't want.  Here you can specify a list of channel_id values
# to explicitly remove from Freevo.
#
TV_CHANNELS_EXCLUDE = []

#
# Default device for TV_CHANNELS
# Set to a device group like dvb, tv or ivtv or a special device like
# dvb0 or dvb1. Set to None for auto detection
#
TV_DEFAULT_DEVICE = None


#
# Program to grab xmltv listings. To get a grabber, you need to download
# xmltv. A possible value for users in the USA is tv_grab_na
# Use the tv_grab helper to grab the listings and cache them. Start
# 'freevo tv_grab --help' for more informations.
#
XMLTV_GRABBER = ''

#
# If you want to run tv_sort on your listings add the path to tv_sort here.
# tv_sort will make sure all your programs have proper stop times, otherwise
# programs might get cut off at midnight.
#
XMLTV_SORT = ''

#
# Number of days the grabber should get
#
XMLTV_DAYS = 3

#
# EPG database backend (possible values are 'sqlite' and 'sqlite2')
#
EPG_DATABASE = 'sqlite'

# ======================================================================
# VDR settings for Freevo plugins and programs that interface to VDR.
# You can read about VDR at http://www.cadsoft.de/vdr/.
# ======================================================================

#
# The directory where the VDR config files can be found.
#
VDR_DIR = '/video'

#
# If VDR is on another host, which one.
#
VDR_HOST = 'localhost'

#
# The port (SVDRP) it is listening on.
#
VDR_PORT = 2001

#
# The EPG filename.
#
VDR_EPG = 'epg.data'

#
# The configuration file for VDR channels.
#
VDR_CHANNELS = 'channels.conf'

#
# The property of a channel we are going to access it with.  The options here
# are 'name', 'sid', and 'rid'.
#
VDR_ACCESS_ID = 'sid'


# ======================================================================
# Freevo builtin WWW server settings:
# ======================================================================

#
# To activate the built in web server, please activate the www plugin
# in your local_conf.py. You can also start the webserver as external
# program by running 'freevo webserver'.
#
# plugin.activate('www')

#
# Web server port number. 80 is the standard port, but is often
# taken already by apache, and cannot be used unless the server
# runs as root. Port 8080 is the default, change to 80 if
# needed.
#
WWW_PORT = 8080

#
# Username / Password combinations to login to the web interface.
# These should be overridden in local_conf.py
# 
# WWW_USERS = { "user1" : "changeme", 
#            "optional" : "changeme2" }
#
WWW_USERS = { 0 : 0 }

#
# Divide the TV guide into intervals of this length (in minutes)
#
WWW_GUIDE_INTERVAL = 30

#
# Precision for TV guide (in minutes)
#
WWW_GUIDE_PRECISION = 5

#
# Show this many blocks at once
#
WWW_GUIDE_COLS = 6

WWW_STYLESHEET = 'styles/main.css'

WWW_JAVASCRIPT = 'scripts/display_prog-head.js'





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
# XMLTV File
#
# This is the XMLTV file that can be optionally used for TV listings
#
# FIXME: OS_CACHEDIR is gone
if os.uname()[0] == 'FreeBSD':
    XMLTV_FILE = OS_CACHEDIR + '/xmltv/TV.xml'
else:
    XMLTV_FILE = '/tmp/TV.xml'

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

