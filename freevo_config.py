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
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.82  2002/10/17 04:16:16  krister
# Changed the 'nice' command so that it is built into runapp instead. Made default prio -20.
#
# Revision 1.81  2002/10/16 18:04:28  krister
# Made it easier to use epg_xmltv.py to generate the list of channels for freevo_config.py.
#
# Revision 1.80  2002/10/16 04:58:16  krister
# Changed the main1 skin to use Gustavos new extended menu for TV guide, and Dischis new XML code. grey1 is now the default skin, I've tested all resolutions. I have not touched the blue skins yet, only copied from skin_dischi1 to skins/xml/type1.
#
# Revision 1.79  2002/10/15 21:44:31  krister
# Added a font alias list, substitute missing non-free fonts with free alternates.
#
# Revision 1.78  2002/10/09 12:52:40  dischi
# made infor(mation) complete
#
# Revision 1.77  2002/10/08 12:19:27  krister
# Added more remote control info
#
# Revision 1.76  2002/10/08 04:32:36  krister
# Reformatted comments.
#
# Revision 1.75  2002/10/07 05:26:25  outlyer
# Added recursive playlist support from Alex Polite <m2@plusseven.com>
#
# Revision 1.74  2002/10/06 14:39:53  dischi
# Removed older log messages and added MPLAYER_USE_WID to turn on/off
# the usage of -wid (on by default)
#
# Revision 1.73  2002/10/03 17:34:37  dischi
# Small update to support more resolutions. I tried to get 720x576 working,
# but for some reason I can't see a freevo on my tv, mplayer works fine.
# Strange....
#
# Revision 1.72  2002/10/02 02:40:55  krister
# Applied Alex Polite's patch for using XMMS instead of MPlayer for
# music playing and visualization.
#
# Revision 1.71  2002/10/01 01:55:06  krister
# Changed the TV channel list to contain examples for Per Wigren's
# patch for multiple TV stations on the same channel on different
# times.
#
# Revision 1.70  2002/09/29 19:57:59  dischi
# Added SHUTDOWN_SYS_CMD to freevo_config to set the shutdown command
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

RANDOM_PLAYLIST     = 1               # Random playlist in all music folders
RECURSIVE_PLAYLIST  = 0               # Random playlist in all music folders 
                                      # including all files below the current folder

#
# Physical ROM drives, multiple ones can be specified
# by adding comma-seperated and quoted entries.
#
# Format [ ('mountdir1', 'devicename1', 'displayed name1'),
#          ('mountdir2', 'devicename2', 'displayed name2'), ...]
#
ROM_DRIVES = [ ('/mnt/cdrom', '/dev/cdrom', 'CD-1'),
               ('/mnt/dvd', '/dev/dvd', 'CD-2') ]


SHUTDOWN_SYS_CMD = 'shutdown -h now'  # set this to 'sudo shutdown -h now' if you
                                      # don't have the permissions to shutdown

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
# The program to play audiofiles. Currently supports MPLAYER and XMMS
#
MUSICPLAYER          = 'MPLAYER'   # Must be 'XMMS' or 'MPLAYER'

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

MAME_CMD         = CONF.xmame_SDL

MAME_NICE        = -20           # Priority of mplayer process. 0 is unchanged,
                                 # <0 is higher prio, >0 lower prio. 
                                 # prio <0 has no effect unless run as root.

# XXX Removed '-ef 1', doesn't work on my older version of mame...  /Krister
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
SKIN_XML_FILE = 'skins/xml/type1/grey1_%s.xml' % CONF.geometry

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

# Font aliases, all names must be lowercase!
# All alternate fonts must be in './skins/fonts/'
OSD_FONT_ALIASES = { 'arial_bold.ttf' : 'kimberly_alt.ttf' }

OSD_SDL_EXEC_AFTER_STARTUP = ""

# Exec a script after the osd startup. Matrox G400 users who wants to
# use the framebuffer and have a PAL tv may set this to
# './matrox_g400/mga_pal_768x576.sh' OSD_SDL_EXEC_AFTER_STARTUP=''
if CONF.display == 'mga':
    OSD_SDL_EXEC_AFTER_STARTUP='./fbcon/mga_%s_%s.sh' % (CONF.tv, CONF.geometry)


# ======================================================================
# MPlayer section:
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
MPLAYER_NICE         = -20             # Priority of mplayer process. 0 is unchanged,
                                       # <0 is higher prio, >0 lower prio.
                                       # prio <0 has no effect unless run as root.

MPLAYER_ARGS_DEF     = ('-nobps -framedrop -nolirc -screenw %s -screenh %s -fs' %
                        (CONF.width, CONF.height))

MPLAYER_ARGS_DVD     = '-cache 8192 -dvd %s'
MPLAYER_ARGS_VCD     = '-cache 4096 -vcd %s'
MPLAYER_ARGS_MPG     = '-cache 5000 -idx'
MPLAYER_ARGS_TVVIEW  = '-nocache'
MPLAYER_ARGS_DVDNAV  = ''
MPLAYER_USE_WID      = 1

# ======================================================================
# XMMS section:
# ======================================================================

XMMS_NICE            = -20
XMMS_CMD             = 'xmms'   # Priority of the XMMS process. 0 is unchanged,
                                # <0 is higher prio, >0 lower prio.
                                # prio <0 has no effect unless run as root.


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
#    "freevo execute epg_xmltv.py config"
# You must have an XMLTV listing in /tmp/TV.xml before running it, and
# TV_CHANNELS below must be set to None. The output contains guesses for the
# displayed name and TV channel name. You can edit this list, delete lines,
# reorder it, etc. For instance, put all your favorite channels first.
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
               ('102 Station 2a', 'Station 2a', '102', ('12345', '0000', '2359')),
               ('102 Station 2b', 'Station 2b', '102', ('67', '0000', '2359')),
               ('103 Station 3a', 'Station 3a', '103', ('1234567', '0000', '1559'), ('1234567', '2200', '2359')),
               ('103 Station 3b', 'Station 3b', '103', ('1234567', '1600', '2159'))]

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
#
# Change the commands in the *LEFT* column, the right column is what Freevo
# expects to see!
#
# Universal remote "ONE FOR ALL", model "Cinema 7" (URC-7201B00 on the back),
# bought from Walmart ($17.00).
# Programmed to code TV "0150". (VCR needs to be programmed too?)
#
# There is a config file for lirc for this remote in freevo/boot/URC-7201B00.
# Please see the Freevo website for information about buying or building a remote
# control receiver.
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

