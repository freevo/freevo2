#if 0
# -----------------------------------------------------------------------
# freevo_config.py - System configuration
# -----------------------------------------------------------------------
# $Id$
#
# Notes:    This file contains the freevo settings. To change the settings
#           you can edit this file, or better, put a file named
#           local_conf.py in the same directory and add your changes there.
#           E.g.: when you want a alsa as mplayer audio out, just put
#           "MPLAYER_AO_DEV = 'alsa9'" in local_conf.py
#
# Todo:     o a nice configure or install script to ask these things
#           o different settings for MPG, AVI, VOB, etc
#             Reason: maybe you want to enable hwac3 on some files
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.67  2002/09/23 16:53:33  dischi
# check mplayer, nice, jpegtrans and xmame.SDL in configure
#
# Revision 1.66  2002/09/19 10:17:46  dischi
# Added mp4, viv and nuv to SUFFIX_MPLAYER_FILES
#
# Revision 1.65  2002/09/14 16:49:19  dischi
# Add support for hwac3. If MPLAYER_AO_HWAC3_DEV is set hwac3 will be
# enabled for DVDs and VOB files
#
# Revision 1.64  2002/09/08 18:26:03  krister
# Applied Andrew Drummond's MAME patch. It seems to work OK on X11, but still needs some work before it is ready for prime-time...
#
# Revision 1.63  2002/09/08 16:40:33  krister
# Added some docs for the new ROM_DRIVES format.
#
# Revision 1.62  2002/09/07 06:15:30  krister
# Added wav-files to the list of music-formats.
#
# Revision 1.61  2002/09/04 19:24:51  dischi
# Added a 3rd parameter to ROM_DRIVES: mountpoint, device, name. I also
# named the drives CD-1 and CD-2 to avoid missunderstandings about the
# name DVD.
#
# Revision 1.60  2002/09/04 05:32:32  krister
# Added some helptext for the remote control config.
#
# Revision 1.59  2002/09/04 04:09:10  krister
# Added the movie suffix *.M2V which is for SVCDs.
#
# Revision 1.58  2002/09/04 03:59:11  krister
# Removed the obsolete ENABLE_TV and ENABLE_IMAGES options, they're in the skin now.
#
# Revision 1.57  2002/09/01 18:12:46  dischi
# mplayer can play movs, too. The current CVS version is very good at
# it, only one file from my ten I tried is not playable.
#
# Revision 1.56  2002/09/01 05:15:55  krister
# Switched to the new freely distributable fonts.
#
# Revision 1.55  2002/08/30 02:29:53  krister
# Added joystick support from Dan Eriksen. Untested!
#
# Revision 1.54  2002/08/22 04:46:03  krister
# Select between the freevo_apps mplayer and a generic one from the path.
#
# Revision 1.53  2002/08/21 04:58:26  krister
# Massive changes! Obsoleted all osd_server stuff. Moved vtrelease and matrox stuff to a new dir fbcon. Updated source to use only the SDL OSD which was moved to osd.py. Changed the default TV viewing app to mplayer_tv.py. Changed configure/setup_build.py/config.py/freevo_config.py to generate and use a plain-text config file called freevo.conf. Updated docs. Changed mplayer to use -vo null when playing music. Fixed a bug in music playing when the top dir was empty.
#
# Revision 1.52  2002/08/19 05:50:39  krister
# Added helptext for configuring the TV.
#
# Revision 1.51  2002/08/19 02:15:44  krister
# Added settings for TV viewing/recording.
#
# Revision 1.50  2002/08/18 06:10:58  krister
# Converted tabs to spaces. Please use tabnanny in the future!
#
# Revision 1.49  2002/08/18 04:09:38  krister
# Made the main skin always the default.
#
# Revision 1.48  2002/08/13 09:56:18  dischi
# configure has three new parameters for the new OSD_SDL:
# --output=x11_800x600 | --output=mga_pal | --output=mga_ntcs
#
# If you choose one of them and no osd=... configure will write a file called
# configure_conf.py (I couldn't think of a better name). This file
# may contain the OUTPUT variable and freevo_config.py will set some
# things based on this variable.
#
# Revision 1.47  2002/08/13 09:22:51  dischi
# Added a variable OUTPUT to set some values automaticly. This variable
# should be set by configure
#
# Revision 1.46  2002/08/13 08:39:58  dischi
# Sorted the config file into several groups. Now it's easier to find
# something. Also added RESOLUTION to set the OSD resolution for OSD_SDL
#
# Revision 1.45  2002/08/12 07:12:33  dischi
# moved xml to subdir type1
#
# Revision 1.44  2002/08/11 08:13:00  dischi
# New variable SKIN_XML_FILE, where to find the xml file for the skin
#
# Revision 1.38  2002/08/03 18:55:44  outlyer
# Last change to config file :)
#
# o You can now set the priority of the mplayer process via a nice setting
# o This involves two lines in the config file: NICE and MPLAYER_NICE for the
#       path to 'nice' and the actual numeric priority where '-10' is the
#       default (high priority) set it to 0 for normal priority or +10 for
#       low priority.
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
# write this in a file called local_conf.py in the same directory.
########################################################################

# ======================================================================
# General freevo settings:
# ======================================================================

AUDIO_DEVICE        = '/dev/dsp'      # e.g.: /dev/dsp0, /dev/audio, /dev/alsa/??
MAJOR_AUDIO_CTRL    = 'VOL'           # Freevo takes control over one audio ctrl
                                      # 'VOL', 'PCM' 'OGAIN' etc.
CONTROL_ALL_AUDIO   = 1               # Should Freevo take complete control of audio
MAX_VOLUME          = 100             # Set what you want maximum volume level to be.
DEFAULT_VOLUME      = 40              # Set default volume level.
TV_IN_VOLUME        = 60              # Set this to your preferred level 0-100.
VCR_IN_VOLUME       = 90              # If you use different input from TV
DEV_MIXER           = '/dev/mixer'    # mixer device 
                    
#
# Physical ROM drives, multiple ones can be specified
# by adding comma-seperated and quoted entries.
#
# Format [ ('mountdir1', 'devicename1', 'displayed name1'),
#          ('mountdir2', 'devicename2', 'displayed name2'), ...]
#
ROM_DRIVES = [ ('/mnt/cdrom', '/dev/cdrom', 'CD-1'),
               ('/mnt/dvd', '/dev/dvd', 'CD-2') ]


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
# expression TV_SHOW_REGEXP, e.g. "Name 3x10 - Title". If an image name.(png|jpg)
# (lowercase) is in this directory, it will be taken as cover image
#
TV_SHOW_IMAGES = "tv-show-images/"

#
# The list of filename suffixes that are used to match the files that
# are played wih MPlayer. They are used as the argument to glob.glob()
# 
SUFFIX_MPLAYER_FILES = [ '/*.[aA][vV][iI]',
                         '/*.[mM][pP][gG]',
                         '/*.[mM][pP][eE][gG]',
                         '/*.[wW][mM][vV]',
                         '/*.[bB][iI][nN]',
                         '/*.[rR][mM]',
                         '/*.[dD][iI][vV][xX]',
                         '/*.[oO][gG][mM]',
                         '/*.[vV][oO][bB]',
                         '/*.[aA][sS][fF]',
                         '/*.[mM][2][vV]',
                         '/*.[mM][pP][4]',
                         '/*.[vV][iI][vV]',
                         '/*.[nN][uU][vV]',
                         '/*.[mM][oO][vV]']


# ======================================================================
# Freevo audio settings:
# ======================================================================

#
# Where the Audio (mp3, ogg) files can be found.
# Format: [ ('Title1', 'directory1'), ('Title2', 'directory2'), ... ]
#
DIR_AUDIO = [ ('Test Files', 'testfiles/Music') ]

#
# The list of filename suffixes that are used to match the files that
# are played as audio. They are used as the argument to glob.glob()
# 
SUFFIX_AUDIO_FILES     = [ '/*.[mM][pP]3',
                           '/*.[oO][gG][gG]',
                           '/*.[wW][aA][vV]' ]
SUFFIX_AUDIO_PLAYLISTS = [ '/*.[mM]3[uU]' ]


# ======================================================================
# Freevo image viewer settings:
# ======================================================================

#
# Where the image files can be found.
#
DIR_IMAGES = [ ('Test Images', './testfiles/Images') ]

#
# The list of filename suffixes that are used to match the files that
# are used for the image viewer. They are used as the argument to glob.glob()
# 
SUFFIX_IMAGE_FILES = [ '/*.[jJ][pP][gG]' ]

# ======================================================================
# Freevo mame settings:
# ======================================================================

#
# MAME is an emulator for old arcade video games. It supports almost
# 2000 different games! The actual emulator is not included in Freevo,
# you'll need to download and install it separately. The main MAME
# website is at http://www.mame.net, but the version that is used here
# is at http://x.mame.net since the regular MAME is for Windows.
#

#
# Where the mame files can be found.
#
# Note: You must have the "rominfo" app from rominfosrc compiled and
# placed in the main freevo dir first. This is not done by the regular
# Makefile, you must do it by hand. Read the rominfosrc/rominfo.txt
# for further instructions on more steps that are required to use MAME!
#
DIR_MAME = [ ('Test Games', './testfiles/Mame') ]

#
# The list of filename suffixes that are used to match the files that
# are used for the image viewer. They are used as the argument to glob.glob()
# 
SUFFIX_MAME_FILES = [ '/*.[zZ][iI][pP]' ]

MAME_CMD	 = CONF.xmame_SDL

MAME_NICE        = '0'             # Priority of mplayer process. 0 is unchanged,
                                      # <0 is higher prio, >0 lower prio. You must run
                                      # freevo as root to use prio <0 !

# XXX Removed '-ef 1', doesn't work on my older version of mame...
MAME_ARGS_DEF     = ('-nosound -fullscreen -modenumber 6 ')



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
SKIN_XML_FILE = 'skins/xml/type1/%s.xml' % CONF.geometry

# XXX The options to disable TV and Images have been removed. This must be
# XXX done in the skin instead (visible="no").
ENABLE_SHUTDOWN = 1      # Enable main menu choice for Linux shutdown. Exits Freevo.
ENABLE_SHUTDOWN_SYS = 0  # Performs a whole system shutdown! For standalone boxes.

#
# OSD default font. It is only used for debug/error stuff, not regular   XXX remove
# skinning.
#
OSD_DEFAULT_FONTNAME = 'skins/fonts/bluehigh.ttf'
OSD_DEFAULT_FONTSIZE = 18


#
# Exec a script after the osd startup. This only works with the OSD_SDL
# osd server. Matrox G400 users who wants to use the framebuffer and have
# a PAL tv may set this to './matrox_g400/mga_pal_768x576.sh'
#
OSD_SDL_EXEC_AFTER_STARTUP=''

if CONF.display == 'mga':
    if CONF.tv == 'ntsc':
        OSD_SDL_EXEC_AFTER_STARTUP='./fbcon/mga_ntsc_768x576.sh'
    elif CONF.tv == 'pal':
        OSD_SDL_EXEC_AFTER_STARTUP='./fbcon/mga_pal_768x576.sh'


# ======================================================================
# mplayer section:
# ======================================================================

if os.path.isfile('../freevo_apps/mplayer/mplayer'):
    MPLAYER_CMD = '../freevo_apps/mplayer/mplayer' # Binary dist
    print 'Using ../freevo_apps/mplayer'
else:
    MPLAYER_CMD = CONF.mplayer
    print 'Using system MPlayer'
    
MPLAYER_AO_DEV       = 'oss:/dev/dsp'  # e.g.: oss,sdl,alsa, see mplayer docs
MPLAYER_AO_HWAC3_DEV = ''              # set this to an audio device which is
                                       # capable of hwac3
MPLAYER_VO_DEV       = CONF.display    # e.g.: xv,x11,mga,fbdev, see mplayer docs

DVD_LANG_PREF        = 'en,se,no'      # Order of preferred languages on DVD.
DVD_SUBTITLE_PREF    = ''              # Order of preferred subtitles on DVD.
NICE                 = CONF.nice       # Priority setting app
MPLAYER_NICE         = '0'             # Priority of mplayer process. 0 is unchanged,
                                       # <0 is higher prio, >0 lower prio. You must run
                                       # freevo as root to use prio <0 !

MPLAYER_ARGS_DEF     = ('-nobps -framedrop -nolirc -screenw %s -screenh %s -fs' %
                        (CONF.width, CONF.height))

MPLAYER_ARGS_DVD     = '-cache 8192 -dvd %s'
MPLAYER_ARGS_VCD     = '-cache 4096 -vcd %s'
MPLAYER_ARGS_MPG     = '-cache 5000 -idx'
MPLAYER_ARGS_TVVIEW  = '-nocache'
MPLAYER_ARGS_DVDNAV  = ''



# ======================================================================
# TV:
# ======================================================================

#
# Watching TV
#
# XXX You must change this to fit your local conditions!
#
# TV/VCR_SETTINGS = 'NORM INPUT CHANLIST'
#
# NORM: ntsc, pal, secam
# INPUT: television, composite1
# CHANLIST: One of the following:
#
# us-bcast, us-cable, us-cable-hrc, japan-bcast, japan-cable, europe-west,
# europe-east, italy, newzealand, australia, ireland, france, china-bcast,
# southafrica, argentina, canada-cable
#
TV_SETTINGS = '%s television %s' % (CONF.tv, CONF.chanlist)
VCR_SETTINGS = '%s composite1 %s' % (CONF.tv, CONF.chanlist)

# TV capture size for viewing and recording. Max 768x480 for NTSC,
# 768x576 for PAL. Set lower if you have a slow computer!
TV_VIEW_SIZE = (640, 480)
TV_REC_SIZE = (320, 240)   # Default for slower computers

# Input formats for viewing and recording. The format affect viewing
# and recording performance. It is specific to your hardware, so read
# the MPlayer docs and experiment with mplayer to see which one fits
# your computer best.
TV_VIEW_OUTFMT = 'yuy2'   # Better quality, slower on pure FB/X11
TV_REC_OUTFMT = 'yuy2'

#
# TV Channels. This list contains a mapping from the displayed channel name
# to the actual channel name as used by the TV watching application.
# The display name is taken from the XMLTV names, and the TV application
# names can be found in matrox_g400/frequencies.c
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
# Use "TV_CHANNELS = None" to get all channels when running epg_xmltv.py standalone!
#
# All channels listed here will be displayed on the TV menu, even if they're
# not present in the XMLTV listing.
# 
TV_CHANNELS = [('2 KTVI', 'KTVI', '2'),
               ('4 KMOV', 'KMOV', '4'),
               ('5 KSDK', 'KSDK', '5'),
               ('6 TBS', 'TBS', '6'),
               ('8 KDNL', 'KDNL', '8'),
               ('9 KETC', 'KETC', '9'),
               ('10 KNLC', 'KNLC', '10'),
               ('11 KPLR', 'KPLR', '11'),
               ('13 GOAC013', 'GOAC013', '13'),
               ('16 WGNSAT', 'WGNSAT', '16'),
               ('17 FNC', 'FNC', '17'),
               ('18 LIFE', 'LIFE', '18'),
               ('20 DSC', 'DSC', '20'),
               ('21 FX', 'FX', '21'),
               ('22 FAM', 'FAM', '22'),
               ('23 AMC', 'AMC', '23'),
               ('24 HALMRK', 'HALMRK', '24'),
               ('25 USA', 'USA', '25'),
               ('26 TNN', 'TNN', '26'),
               ('27 ESPN2', 'ESPN2', '27'),
               ('28 ESPN', 'ESPN', '28'),
               ('29 ARTS', 'ARTS', '29'),
               ('31 TECHTV', 'TECHTV', '31'),
               ('32 TWC', 'TWC', '32'),
               ('33 TNT', 'TNT', '33'),
               ('34 NIK', 'NIK', '34'),
               ('35 CNN', 'CNN', '35'),
               ('36 CNBC', 'CNBC', '36'),
               ('37 TLC', 'TLC', '37'),
               ('38 DISN', 'DISN', '38'),
               ('41 ETV', 'ETV', '41'),
               ('42 FSM', 'FSM', '42'),
               ('43 HISTORY', 'HISTORY', '43'),
               ('44 COMEDY', 'COMEDY', '44'),
               ('45 VH1', 'VH1', '45'),
               ('46 TVGOS', 'TVGOS', '46'),
               ('50 CNNH', 'CNNH', '50'),
               ('53 EWTN', 'EWTN', '53'),
               ('', 'MSNBC 1', '56'),
               ('58 LOOR058', 'LOOR058', '58'),
               ('61 WPXS', 'WPXS', '61'),
               ('64 MSNBC', 'MSNBC 2', '64'),
               ('65 OXYGEN', 'OXYGEN', '65'),
               ('66 LOOR066', 'LOOR066', '66'),
               ('67 MTV', 'MTV', '67'),
               ('69 HGTV', 'HGTV', '69'),
               ('70 TVLAND', 'TVLAND', '70'),
               ('71 ESPNCL', 'ESPNCL', '71'),
               ('72 OLN', 'OLN', '72'),
               ('73 SCIFI', 'SCIFI', '73'),
               ('74 BRAVO', 'BRAVO', '74'),
               ('75 TOOND', 'TOOND', '75'),
               ('99', 'TEST', '99')]


# ======================================================================
# Internal stuff, you shouldn't change anything here unless you know
# what you are doing
# ======================================================================

VIDREC_MQ_TV = ('DIVX4rec -F 300000 -norm NTSC ' +
                '-input Television -m -r 22050 -w 320 -h 240 ' +
                '-ab 80 -vg 100 -vb 800 -H 50 -o %s')

# Under development
VIDREC_MQ_VCR = ('DIVX4rec -F 300000 -norm NTSC ' +
                 '-input Composite1 -m -r 22050 -w 320 -h 240 ' +
                 ' -ab 80 -vg 100 -vb 1000 -H 50 -o %s')

# Under development
VIDREC_MQ_NUVTV = ('-F 10000 -norm NTSC -input Television -m ' +
                   '-r 44100 -w 320 -h 240 -vg 100 -vq 90 -H 50 ' +
                   '-mixsrc /dev/dsp:line -mixvol /dev/dsp:line:80 -o %s')

VIDREC_MQ = VIDREC_MQ_TV
VIDREC_HQ = ''

#
# Config for xml support in the movie browser
# the regexp has to be with ([0-9]|[0-9][0-9]) so we can get the numbers
#
SUFFIX_FREEVO_FILES = [ '/*.[xX][mM][lL]' ]
TV_SHOW_REGEXP = "s?([0-9]|[0-9][0-9])[xe]([0-9]|[0-9][0-9])[^0-9]"


#
# OSD server, standalone application in osd_server/
#
OSD_HOST = '127.0.0.1'      # The remote host
OSD_PORT = 16480            # The daemon port, osd_server/osd_fb/main.c has
                            # to be changed manually!

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

#
# Remote control commands translation table. Replace this with the commands that
# lirc sends for your remote. NB: The .lircrc file is not used.
# Change the commands in the *LEFT* column, the right column is what Freevo
# expects to see!
#
# Universal remote "ONE FOR ALL", model "Cinema 7" (URC-7201B00 on the back),
# bought from Walmart ($17.00).
# Programmed to code TV "0150". (VCR needs to be programmed too?)
#
RC_CMDS = {
    'sleep'       : 'SLEEP',
    'menu'        : 'MENU',
    'prog_guide'  : 'GUIDE',
    'exit'        : 'EXIT',
    'up'          : 'UP',
    'down'        : 'DOWN',
    'left'        : 'LEFT',
    'right'       : 'RIGHT',
    'sel'         : 'SELECT',
    'power'       : 'POWER',
    'mute'        : 'MUTE',
    'vol+'        : 'VOL+',
    'vol-'        : 'VOL-',
    'ch+'         : 'CH+',
    'ch-'         : 'CH-',
    '1'           : '1',
    '2'           : '2',
    '3'           : '3',
    '4'           : '4',
    '5'           : '5',
    '6'           : '6',
    '7'           : '7',
    '8'           : '8',
    '9'           : '9',
    '0'           : '0',
    'display'     : 'DISPLAY',
    'enter'       : 'ENTER',
    'prev_ch'     : 'PREV_CH',
    'pip_onoff'   : 'PIP_ONOFF',
    'pip_swap'    : 'PIP_SWAP',
    'pip_move'    : 'PIP_MOVE',
    'tv_vcr'      : 'EJECT',
    'rew'         : 'REW',
    'play'        : 'PLAY',
    'ff'          : 'FFWD',
    'pause'       : 'PAUSE',
    'stop'        : 'STOP',
    'rec'         : 'REC',
    'eject'       : 'EJECT'
    }

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

