#if 0
# -----------------------------------------------------------------------
# freevo_config.py - System configuration
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#    This file contains the freevo settings. To change the settings
#    you can edit this file, or better, put a file named local_conf.py
#    # in the same directory and add your changes there.  E.g.: when
#    you # want a alsa as mplayer audio out, just put
#    "MPLAYER_AO_DEV = # 'alsa9'" in local_conf.py
#
# Developer Notes:
#    The CVS log isn't used here. Write changes directly in this file
#    to make it easier for the user
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
#endif


########################################################################
# If you want to change some things for your personal setup, please
# write this in a file called local_conf.py, see that file for more info.
########################################################################

# Version information for the two config files. When the major version
# of the config file doesn't match, Freevo won't start. If the minor version
# is different, there will be only a warning

FREEVO_CONF_VERSION = 1.0
LOCAL_CONF_VERSION  = 1.0

# NOW check if freevo.conf is up-to-date. An older version may break the next
# steps

if int(str(CONF.version).split('.')[0]) != \
   int(str(FREEVO_CONF_VERSION).split('.')[0]):
    print '\nERROR: The version informations in freevo_config.py doesn\'t'
    print 'match the version in %s.' % freevoconf
    print 'please rerun configure to generate a new freevo.conf'
    sys.exit(1)

if int(str(CONF.version).split('.')[1]) != \
   int(str(FREEVO_CONF_VERSION).split('.')[1]):
    print 'WARNING: freevo_config.py was changed, please rerun ./configure'
    

# ======================================================================
# General freevo settings:
# ======================================================================

AUDIO_DEVICE        = '/dev/dsp'      # e.g.: /dev/dsp0, /dev/audio, /dev/alsa/?
MAJOR_AUDIO_CTRL    = 'VOL'           # Freevo takes control over one audio ctrl
                                      # 'VOL', 'PCM' 'OGAIN' etc.
CONTROL_ALL_AUDIO   = 1               # Should Freevo take complete control of audio
MAX_VOLUME          = 90              # Set what you want maximum volume level to be.
DEFAULT_VOLUME      = 40              # Set default volume level.
TV_IN_VOLUME        = 60              # Set this to your preferred level 0-100.
VCR_IN_VOLUME       = 90              # If you use different input from TV
DEV_MIXER           = '/dev/mixer'    # mixer device 

START_FULLSCREEN_X  = 0               # Start in fullscreen mode if using x11 or xv.

#
# Physical ROM drives, multiple ones can be specified
# by adding comma-seperated and quoted entries.
#
# Format [ ('mountdir1', 'devicename1', 'displayed name1'),
#          ('mountdir2', 'devicename2', 'displayed name2'), ...]
#
# Leave empty to autodetect drives in during startup from /etc/fstab
ROM_DRIVES = []

ROM_SPEED = 0                         # try to set the drive speed of the rom
                                      # drive a good value for playing movies
                                      # with a silent drive is 8


SHUTDOWN_SYS_CMD = 'shutdown -h now'  # set this to 'sudo shutdown -h now' if
                                      # you don't have the permissions to
                                      # shutdown

# ======================================================================
# Freevo directory settings:
# ======================================================================

# You can change all this variables in the skin.xml on a per folder
# basis

#
# Should playlists be available for movies, and all movies in a directory
# be played in succession (unless you press STOP/EXIT)?
#
MOVIE_PLAYLISTS = 0

#
# Should a Random Playlist be generated for Music?
#
AUDIO_RANDOM_PLAYLIST = 1

#
# Should directories sorted by date instead of filename
#
DIRECTORY_SORT_BY_DATE = 0

#
# Should freevo autoplay the item if only one item is in the directory
#
DIRECTORY_AUTOPLAY_SINGLE_ITEM = 1

# ======================================================================
# Freevo movie settings:
# ======================================================================

#
# Where the movie files can be found.
#
DIR_MOVIES = [ ('Test Movies', 'testfiles/Movies') ]

#
# This is where recorded video is written.
#
DIR_RECORD = './testfiles/Movies/Recorded'

#
# Directory for XML definitions for DVDs and VCDs. Items in this
# directory won't be in the MOVIE MAIN MENU, but will be used to find
# titles and images for the current DVD/VCD
#
MOVIE_DATA_DIR = 'movie-data/'

#
# Directory containing images for tv shows. A tv show maches the regular
# expression TV_SHOW_REGEXP, e.g. "Name 3x10 - Title". If an image
# name.(png|jpg) (lowercase) is in this directory, it will be taken as cover
# image
#
TV_SHOW_IMAGES = "testfiles/tv-show-images/"

#
# Directory for cover images for CD/VCD/DVD and music CDs or when you can't
# add a cover image to the dir you want. Not for replacing the normal
# cover file function.
#
COVER_DIR = 'testfiles/Covers/'

#
# The list of filename suffixes that are used to match the files that
# are played wih MPlayer.
# 
SUFFIX_VIDEO_FILES = [ 'avi', 'mpg', 'mpeg', 'wmv', 'bin', 'rm',
                       'divx', 'ogm', 'vob', 'asf', 'm2v', 'm2p',
                       'mp4', 'viv', 'nuv', 'mov' ]

# ======================================================================
# Freevo audio settings:
# ======================================================================

#
# The program to play audiofiles. Currently supports MPLAYER and XMMS
#
MUSICPLAYER          = 'MPLAYER'   # Must be 'XMMS' or 'MPLAYER'

#
# Where the Audio (mp3, ogg) files can be found.
# Format: [ ('Title1', 'directory1', 'mplayer options'),
#           ('Title2', 'directory2'), ... ]
# The 'mplayer options' field can be omitted.
#
DIR_AUDIO = [ ('Test Files', 'testfiles/Music') ]

#
# The list of filename suffixes that are used to match the files that
# are played as audio.
# 
SUFFIX_AUDIO_FILES     = [ 'mp3', 'ogg', 'wav' ]
SUFFIX_AUDIO_PLAYLISTS = [ 'm3u' ]

# This regexp should recognize filenames which are likely to be covers
# for an album. This example will match front.jpg and cover-f.jpg, but
# not back.jpg nor cover-b.jpg
#
AUDIO_COVER_REGEXP = 'front|-f'

# ======================================================================
# Freevo image viewer settings:
# ======================================================================

#
# Where the image files can be found.
#
DIR_IMAGES = [ ('Test Images', './testfiles/Images') ]

# Temporarily disabled, doesn't work
#DIR_IMAGES = [ ('Test Images', './testfiles/Images'),
#               ('Test Show',  'testfiles/Images/CA_Coast.ssr') ]

#
# The list of filename suffixes that are used to match the files that
# are used for the image viewer.
# 
SUFFIX_IMAGE_FILES = [ 'jpg' ]

# The viewer now supports a new type of menu entry, a slideshow file.
# It also has the slideshow alarm signal handler for automated shows.
# It uses a new configuration option:

SUFFIX_IMAGE_SSHOW = [ 'ssr' ]

# This defines the file extensions of slideshow playlists. When DIR_IMAGES
# is parsed, it will look for entries that match the SUFFIX_IMAGE_SSHOW
# patterns. If it finds a match, then it will classify that entry as a
# slideshow playlist instead of a directory of images. For example:

# DIR_IMAGES = [ ('Arizona 2002', '/video/SlideShows/arizona-2002.ssr'),
#                ('Carmel 2002',  '/video/SlideShows/carmel.ssr'),
#                ('Pics',  '/video/SlideShows') ]


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
# Note: You must have the "rominfo" app from rominfosrc compiled and
# placed in the main freevo dir first. This is not done by the regular
# Makefile, you must do it by hand. Read the rominfosrc/rominfo.txt
# for further instructions on more steps that are required to use MAME!
# 
# SNES stands for Super Nintendo Entertainment System.  Freevo relies
# on other programs that are not included in Freevo to play these games.
# 
# Where the mame and snes files can be found.
# 

DIR_GAMES = [ ('Test Games', './testfiles/Mame') ]

#
# The list of filename suffixes that are used to match the files that
# are used for the Mame arcade emulator. 
# 
SUFFIX_MAME_FILES = [ 'zip' ]
SUFFIX_SNES_FILES = [ 'smc', 'fig' ]

MAME_CMD         = CONF.xmame_SDL
SNES_CMD         = CONF.snes

GAMES_NICE        = -20       # Priority of the game process. 0 is unchanged,
                              # <0 is higher prio, >0 lower prio. 
                              # prio <0 has no effect unless run as root.

# XXX Removed '-ef 1', doesn't work on my older version of mame...  /Krister
MAME_ARGS_DEF     = ('-nosound -fullscreen -modenumber 6 ')

# This example is a set of arguments for zsnes.
SNES_ARGS_DEF     = ("-m -r 3 -k 100 -1 3 -2 3 -cs -t")


# ======================================================================
# freevo OSD section:
# ======================================================================

#
# Skin file that contains the actual skin code. This is imported
# from skin.py
#
OSD_SKIN = 'skins/main1/skin_main1.py'

#
# XML file for the skin
#
SKIN_XML_FILE = 'blue_round1'

ENABLE_SHUTDOWN_SYS = 0  # Performs a whole system shutdown at SHUTDOWN!
                         # For standalone boxes.

#
# OSD default font. It is only used for debug/error stuff, not regular skinning.
#
OSD_DEFAULT_FONTNAME = 'skins/fonts/bluehigh.ttf'
OSD_DEFAULT_FONTSIZE = 18

# Font aliases, all names must be lowercase!
# All alternate fonts must be in './skins/fonts/'
OSD_FONT_ALIASES = { 'arial_bold.ttf' : 'kimberly_alt.ttf' }

OSD_SDL_EXEC_AFTER_STARTUP = ""

# Exec a script after the osd startup. Matrox G400 users who wants to
# use the framebuffer and have a PAL tv may set this to
# './matrox_g400/mga_pal_768x576.sh' OSD_SDL_EXEC_AFTER_STARTUP=''
if CONF.display == 'mga':
    OSD_SDL_EXEC_AFTER_STARTUP='./fbcon/mga_%s_%s.sh' % (CONF.tv, CONF.geometry)

OVERSCAN_X = 0
OVERSCAN_Y = 0

if CONF.display == 'dfbmga' or CONF.display == 'dxr3':
    OVERSCAN_X = 30
    OVERSCAN_Y = 30


# ======================================================================
# Remote control section
# ======================================================================


#
# Config file for the remote. This file should contain RC_CMDS and
# RC_MPLAYER_CMDS. The location of the file is rc_client, right now the only
# remote in there is realmagic.py. The choose this remote, set the variable to
# 'realmagic'. Please send files for other remotes to the freevo mailing list
#

REMOTE = ''


#
# If you use the new lirc client library method of remote control, you need a
# lircrc file, like this:
#
# begin
#       prog = freevo
#       button = select
#       config = SELECT
# end
#
LIRCRC = '/etc/freevo/lircrc'

#
# Remote control commands translation table. Replace this with the commands that
# lirc sends for your remote. NB: The .lircrc file is not used.
#
# Change the commands in the *LEFT* column, the right column is what Freevo
# expects to see! If the lirc command is identical (case insensitiv) with the
# Freevo commands, the commands don't need to be in this list
#
# Universal remote "ONE FOR ALL", model "Cinema 7" (URC-7201B00 on the back),
# bought from Walmart ($17.00).
# Programmed to code TV "0150". (VCR needs to be programmed too?)
#
# There is a config file for lirc for this remote in freevo/boot/URC-7201B00.
# Please see the Freevo website for information about buying or building a
# remote control receiver.
#
RC_CMDS = {
    'prog_guide'  : 'GUIDE',
    'sel'         : 'SELECT',
    'tv_vcr'      : 'EJECT',
    'ff'          : 'FFWD',
    }

#
# List of mplayer commands
#
RC_MPLAYER_CMDS = {}

# XXX This is experimental, please send in testreports!
# XXX If you want to use it you need to uncomment a line
# XXX in the "freevo" start-script!
# 
#
# Set the Joy device to 0 to disable, 1 for js0, 2 for js1, etc...
# Supports as many buttons as your controller has,
# but make sure there is a corresponding entry in your config
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
# MPlayer section:
# ======================================================================

# Set to 1 to log mplayer output to ./mplayer_stdout.log and
# ./mplayer_stderr.log
MPLAYER_DEBUG = 0

MPLAYER_CMD = CONF.mplayer
print 'Using MPlayer: %s' % MPLAYER_CMD
    
MPLAYER_AO_DEV       = 'oss:/dev/dsp'  # e.g.: oss,sdl,alsa, see mplayer docs

if CONF.display == 'x11':
    MPLAYER_VO_DEV       = 'xmga,xv,x11,'  # X11 drivers in order of preference
else:
    MPLAYER_VO_DEV       = CONF.display    # e.g.: x11,mga,fbdev, see mplayer docs

MPLAYER_VO_DEV_OPTS  = ''	       # e.g.: ':some_var=vcal'

DVD_LANG_PREF        = 'en,se,no'      # Order of preferred languages on DVD.
DVD_SUBTITLE_PREF    = ''              # Order of preferred subtitles on DVD.

# Priority of mplayer process. 0 is unchanged, <0 is higher prio, >0 lower prio.
# prio <0 has no effect unless run as root.
MPLAYER_NICE         = -20             

if CONF.display == 'dfbmga':
    MPLAYER_ARGS_DEF     = ('-ac mad, -autosync 100 -nolirc ' +
                            '-autoq 100 -fs -vsync -double')
else:
    MPLAYER_ARGS_DEF     = (('-ac mad, -autosync 100 -nolirc -autoq 100 -screenw %s '
                             + '-screenh %s -fs') % (CONF.width, CONF.height))

MPLAYER_ARGS_DVD     = '-cache 8192 -dvd %s'
MPLAYER_ARGS_VCD     = '-cache 4096 -vcd %s'
MPLAYER_ARGS_MPG     = '-cache 5000 '
MPLAYER_ARGS_TVVIEW  = '-nocache'
MPLAYER_ARGS_DVDNAV  = '-dvdnav'
MPLAYER_USE_WID      = 1

#
# The runtime version of MPlayer/MEncoder are patched to disable DVD
# protection override (a.k.a decss) by using the flag
# "-nodvdprotection-override". This flag is set by default if the runtime version
# of MPlayer is used to play DVDs, since it is illegal (TBC) to use it in some
# countries. You can modify the program to use the protection override,
# but only if you're 100% sure that it is legal in your jurisdiction!
#
MPLAYER_DVD_PROTECTION = 1

# ======================================================================
# XMMS section:
# ======================================================================

# Priority of xmms process. 0 is unchanged, <0 is higher prio, >0 lower prio.
# prio <0 has no effect unless run as root.
XMMS_NICE            = -20
XMMS_CMD             = 'xmms'


# ======================================================================
# TV:
# ======================================================================

#
# Watching TV
#
# XXX You must change this to fit your local conditions!
#
# TV/VCR_SETTINGS = 'NORM INPUT CHANLIST DEVICE'
#
# NORM: ntsc, pal, secam
# INPUT: television, composite1
# CHANLIST: One of the following:
#
# us-bcast, us-cable, us-cable-hrc, japan-bcast, japan-cable, europe-west,
# europe-east, italy, newzealand, australia, ireland, france, china-bcast,
# southafrica, argentina, canada-cable
#
# DEVICE: Usually /dev/video0, but might be /dev/video1 instead for multiple
# boards.
#
TV_SETTINGS = '%s television %s /dev/video0' % (CONF.tv, CONF.chanlist)

#
# XXX Recording is still work in progress. You need to change
# XXX the entire string below to fit your local settings.
# XXX Eventually TV norm (PAL/NTSC) etc will be taken from the
# XXX other flags. VCR_xxx and TV_REC_xxx is not used yet!
# XXX You also need to have the recording daemon running, see
# XXX the website docs or the mailing lists if that fails.
#
# XXX Please see the mencoder docs for more info about the settings
# XXX below. Some stuff must be changed (adevice), others probably
# XXX should be ("Change"), or could be in some cases ("change?")
VCR_CMD = ('/usr/local/bin/mencoder ' +    # Change. Absolute path to the runtime
           '-tv on:driver=v4l:input=0' +   # Input 0 = Comp. V. in
           ':norm=NTSC' +                  # Change
           ':channel=%s' +                 # Filled in by Freevo
           ':chanlist=us-cable' +          # Change
           ':width=320:height=240' +       # Change if needed
           ':outfmt=yv12' +                # Prob. ok, yuy2 might be faster
           ':device=/dev/video0' +         # CHANGE!
           ':adevice=/dev/dsp4' +          # CHANGE!
           ':audiorate=32000' +            # 44100 for better sound
           ':forceaudio:forcechan=1:' +    # Forced mono for bug in my driver
           'buffersize=64' +               # 64 Megabyte capture buffer, change?
           ' -ovc lavc -lavcopts ' +       # Mencoder lavcodec video codec
           'vcodec=mpeg4' +                # lavcodec mpeg-4
           ':vbitrate=1200:' +             # Change lower/higher, bitrate
           'keyint=30 ' +                  # Keyframe every 10 secs, change?
           '-oac mp3lame -lameopts ' +     # Use Lame for MP3 encoding
           'br=128:cbr:mode=3 ' +          # MP3 const. bitrate, 128 kbit/s
           '-ffourcc divx '                # Force 'divx' ident, better compat.
           '-o %s.avi ')                   # Filled in by Freevo

# XXX Not used yet
VCR_SETTINGS = '%s composite1 %s /dev/video0' % (CONF.tv, CONF.chanlist)

# TV capture size for viewing and recording. Max 768x480 for NTSC,
# 768x576 for PAL. Set lower if you have a slow computer!
TV_VIEW_SIZE = (640, 480)
# XXX Not used yet
TV_REC_SIZE = (320, 240)   # Default for slower computers

# Input formats for viewing and recording. The format affect viewing
# and recording performance. It is specific to your hardware, so read
# the MPlayer docs and experiment with mplayer to see which one fits
# your computer best.
TV_VIEW_OUTFMT = 'yuy2'   # Better quality, slower on pure FB/X11
# XXX Not used yet
TV_REC_OUTFMT = 'yuy2'

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
# This list also determines the order in which the channels are displayed!
# N.B.: You must delete the XMLTV cache file (e.g. /tmp/TV.xml.pickled)
#       if you make changes here and restart!
#
# Format: [('xmltv channel id', 'freevo display name', 'tv channel name'), ...]
#
# If you want to generate a list of all the channels in the XMLTV guide in
# this format you can run the following command:
#    "freevo execute src/tv/epg_xmltv.py config"
# You must have an XMLTV listing in /tmp/TV.xml before running it, and
# TV_CHANNELS below must be set to None. The output contains guesses for the
# displayed name and TV channel name. You can edit this list, delete lines,
# reorder it, etc. For instance, put all your favorite channels first.
# Don't forget to actually update TV_CHANNELS afterwards, it won't work
# if it is set to None!
#
# All channels listed here will be displayed on the TV menu, even if they're
# not present in the XMLTV listing.
# 
#
# Timedependent channels:
#
# The TV_CHANNELS-list can look like this:
#
# TV_CHANNELS = [('21', 'SVT1',              'E5'),
#                ('22', 'SVT2',              'E3'),
#                ('26', 'TV3',               'E10'),
#                ('27', 'TV4',               'E6'),
#                ('10', 'Kanal 5',           'E7'),
#                ('60', 'Fox Kids',          'E8', ('1234567','0600','1659')),
#                ('16', 'TV6',               'E8', ('1234567','1700','2359'), 
#                                                  ('1234567','0000','0300')),
#                ('14', 'MTV Europe',        'E11') ]
#
# As you can see the list takes optional tuples:
# ( 'DAYS', 'START','END')
#
# 1234567 in days means all days.
# 12345 would mean monday to friday.
#
# It will display "Fox Kids" from 06:00 to 16:59 and "TV6" from 17:00 to 03:00. 
# 03:00 to 06:00 it won't be displayed at all.
#

TV_CHANNELS = [('69 COMEDY', 'COMEDY', '69'),
               ('56 HISTORY', 'HISTORY', '56'),
               ('2 KTVI', 'KTVI', '2'),
               ('4 KMOV', 'KMOV', '4'),
               ('5 KSDK', 'KSDK', '5'),
               ('6 TBS', 'TBS', '6'),
               ('11 KPLR', 'KPLR', '11'),
               ('12 KDNL', 'KDNL', '12'),
               ('29 LIFE', 'LIFE', '29'),
               ('49 USA', 'USA', '49'),
               ('30 HALMRK', 'HALMRK', '30'),
               ('42 TNT', 'TNT', '42'),
               ('41 FX', 'FX', '41'),
               ('59 TLC', 'TLC', '59'),
               ('31 TECHTV', 'TECHTV', '31'),
               ('57 DSC', 'DSC', '57'),
               ('66 ETV', 'ETV', '66'),
               ('75 MTV', 'MTV', '75'),
               ('77 VH1', 'VH1', '77'),
               ('32 TNN', 'TNN', '32'),
               ('43 CNN', 'CNN', '43'),
               ('44 CNNH', 'CNNH', '44'),
               ('46 CNBC', 'CNBC', '46'),
               ('47 MSNBC', 'MSNBC', '47'),
               ('48 FNC', 'FNC', '48'),
               ('45 TWC', 'TWC', '45'),
               ('35 ESPN', 'ESPN', '35'),
               ('36 ESPN2', 'ESPN2', '36'),
               ('37 GOLF', 'GOLF', '37'),
               ('38 SPEED', 'SPEED', '38'),
               ('40 FSM', 'FSM', '40'),
               ('7 WGNSAT', 'WGNSAT', '7'),
               ('8 LOOR008', 'LOOR008', '8'),
               ('9 KETC', 'KETC', '9'),
               ('15 CSPAN', 'CSPAN', '15'),
               ('16 CSPAN2', 'CSPAN2', '16'),
               ('22 TBN', 'TBN', '22'),
               ('33 NGC', 'NGC', '33'),
               ('34 INSP', 'INSP', '34'),
               ('50 FAM', 'FAM', '50'),
               ('51 NIK', 'NIK', '51'),
               ('52 DISN', 'DISN', '52'),
               ('53 TOOND', 'TOOND', '53'),
               ('54 TOON', 'TOON', '54'),
               ('55 ARTS', 'ARTS', '55'),
               ('58 ANIMAL', 'ANIMAL', '58'),
               ('60 TCM', 'TCM', '60'),
               ('61 OXYGEN', 'OXYGEN', '61'),
               ('62 FOOD', 'FOOD', '62'),
               ('63 HGTV', 'HGTV', '63'),
               ('64 TRAV', 'TRAV', '64'),
               ('65 WE', 'WE', '65'),
               ('67 SOAP', 'SOAP', '67'),
               ('68 BET', 'BET', '68'),
               ('70 TVLAND', 'TVLAND', '70'),
               ('71 AMC', 'AMC', '71'),
               ('72 BRAVO', 'BRAVO', '72'),
               ('73 SCIFI', 'SCIFI', '73'),
               ('74 COURT', 'COURT', '74'),
               ('76 CMTV', 'CMTV', '76'),
               ('78 FMC', 'FMC', '78'),
               ('96 LOOR096', 'TV Guide', '96'),
               ('101 Station 1a', 'Station 1a', '101', ('123', '0000', '1759')),
               ('101 Station 1b', 'Station 1b', '101', ('123', '1800', '2359')),
               ('102 Station 2a', 'Station 2a', '102',
                ('12345', '0000', '2359')),
               ('102 Station 2b', 'Station 2b', '102', ('67', '0000', '2359')),
               ('103 Station 3a', 'Station 3a', '103',
                ('1234567', '0000', '1559'), ('1234567', '2200', '2359')),
               ('103 Station 3b', 'Station 3b', '103',
                ('1234567', '1600', '2159'))]

# ======================================================================
# Internal stuff, you shouldn't change anything here unless you know
# what you are doing
# ======================================================================

#
# Config for xml support in the movie browser
# the regexp has to be with ([0-9]|[0-9][0-9]) so we can get the numbers
#
SUFFIX_VIDEO_DEF_FILES = [ 'fxd' ]
TV_SHOW_REGEXP = "s?([0-9]|[0-9][0-9])[xe]([0-9]|[0-9][0-9])[^0-9]"


#
# Remote control daemon. The server is in the Freevo main application,
# and the client is a standalone application in rc_client/
#
REMOTE_CONTROL_HOST = '127.0.0.1'
REMOTE_CONTROL_PORT = 16310

# Cache for Freevo data

if os.path.isdir('/var/cache/freevo'):
    FREEVO_CACHEDIR = '/var/cache/freevo'
else:
    if not os.path.isdir('/tmp/freevo/cache'):
        os.makedirs('/tmp/freevo/cache')
    FREEVO_CACHEDIR = '/tmp/freevo/cache'

import os
MAME_CACHE = '%s/romlist-%s.pickled' % (FREEVO_CACHEDIR, os.getuid())

#
# XMLTV File
#
# This is the XMLTV file that can be optionally used for TV listings
#
XMLTV_FILE = '/tmp/TV.xml'

#
# XML TV Logo Location
#
# Use the "makelogos.py" script to download all the
# Station logos into a directory. And then put the path
# to those logos here
if os.path.isdir('/var/cache/xmltv/logos'):
    TV_LOGOS = '/var/cache/xmltv/logos'
else:
    if not os.path.isdir('/tmp/freevo/xmltv/logos'):
        os.makedirs('/tmp/freevo/xmltv/logos')
    TV_LOGOS = '/tmp/freevo/xmltv/logos'

