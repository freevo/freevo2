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
# Revision 1.44  2002/08/11 08:13:00  dischi
# New variable SKIN_XML_FILE, where to find the xml file for the skin
#
# Revision 1.43  2002/08/10 17:44:20  dischi
# Added OSD_SDL_EXEC_AFTER_STARTUP. The script in this variable will
# be executed after the SDL interface is started. You can use this to
# correct the fbset settings on framebuffer
#
# Revision 1.42  2002/08/08 06:05:32  outlyer
# Small changes:
#  o Made Images menu a config file option "ENABLE_IMAGES"
#  o Removed the redundant fbset 640x480-60 which doesn't even exist in the
#    fbset.db (?)
#
# Revision 1.41  2002/08/07 04:53:01  krister
# Changed shutdown to just exit freevo. A new config variable can be set to shutdown the entire machine.
#
# Revision 1.40  2002/08/05 00:43:10  tfmalt
# o Changed DIR_MP3 to DIR_AUDIO
#
# Revision 1.39  2002/08/03 20:20:54  krister
# Nice cannot be used as non-root to raise the prio! Set to 0 as default. Changed mplayer settings from dsp0+mga to dsp+xv which is better for newbie desktop users (mplayer cannot play mp3s if -vo is set wrong!) Fixed speling errors.
#
# Revision 1.38  2002/08/03 18:55:44  outlyer
# Last change to config file :)
#
# o You can now set the priority of the mplayer process via a nice setting
# o This involves two lines in the config file: NICE and MPLAYER_NICE for the
# 	path to 'nice' and the actual numeric priority where '-10' is the
# 	default (high priority) set it to 0 for normal priority or +10 for
# 	low priority.
#
# Revision 1.37  2002/08/03 18:14:16  dischi
# Lots of changes:
# o added the patch from Thomas Malt with the new audio control
# o removed the ConfigInit stuff, you can have two version of freevo on
#   one disc if you need to videotools
# o added all the options to MPLAYER_ARGS_*
# o added DVD_SUBTITLE_PREF
#
# If you want to change some things for your personal setup, please
# write this in a file called local_conf.py in the same directory.
#
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



AUDIO_DEVICE        = '/dev/dsp'      # e.g.: /dev/dsp0, /dev/audio, /dev/alsa/??
MAJOR_AUDIO_CTRL    = 'PCM'           # Freevo takes control over one audio ctrl
                                      # 'VOL', 'PCM' 'OGAIN' etc.
CONTROL_ALL_AUDIO   = 1               # Should Freevo take complete control of audio
MAX_VOLUME          = 100             # Set what you want maximum volume level to be.
DEFAULT_VOLUME      = 40              # Set default volume level.
TV_IN_VOLUME        = 60              # Set this to your preferred level 0-100.
VCR_IN_VOLUME       = 90              # If you use different input from TV
                    
MPLAYER_CMD         = 'mplayer'       # A complete path may be nice.
MPLAYER_AO_DEV      = 'oss:/dev/dsp'  # e.g.: oss,sdl,alsa, see mplayer docs
MPLAYER_VO_DEV      = 'xv'            # e.g.: xv,x11,mga, see mplayer docs
DVD_LANG_PREF       = 'en,se,no'      # Order of preferred languages on DVD.
DVD_SUBTITLE_PREF   = ''              # Order of preferred subtitles on DVD.
NICE		    = '/usr/bin/nice' # Priority setting app
MPLAYER_NICE	    = '0'	      # Priority of mplayer process. 0 is unchanged,
                                      # <0 is higher prio, >0 lower prio. You must run
                                      # freevo as root to use prio <0 !


#---- You should really _NOT_ need to change these settings  ----
MPLAYER_ARGS_DEF     = '-nobps -framedrop -nolirc -screenw 768 -screenh 576 -fs'
MPLAYER_ARGS_DVD     = '-cache 8192 -dvd %s'
MPLAYER_ARGS_VCD     = '-cache 4096 -vcd %s'
MPLAYER_ARGS_MPG     = '-cache 5000 -idx'
MPLAYER_ARGS_DVDNAV  = ''
#---- End of settings you really _NOT_ should need to change ----


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
# General settings
# 
# XXX Move to a file ("autoconf.py"?) that is create during "./configure"
# from the parameters to it.
#
ENABLE_TV = 1            # Disable this if you don't have a tv card
ENABLE_SHUTDOWN = 1      # Enable main menu choice for Linux shutdown. Exits Freevo.
ENABLE_SHUTDOWN_SYS = 0  # Performs a whole system shutdown! For standalone boxes.
ENABLE_IMAGES = 1	 # Disable this if you don't want/use the Image Browser

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
			 '/*.[aA][sS][fF]' ]

#
# Config for xml support in the movie browser
# the regexp has to be with ([0-9]|[0-9][0-9]) so we can get the numbers
#

SUFFIX_FREEVO_FILES = [ '/*.[xX][mM][lL]' ]
TV_SHOW_REGEXP = "s?([0-9]|[0-9][0-9])[xe]([0-9]|[0-9][0-9])[^0-9]"
TV_SHOW_IMAGES = "tv-show-images/"

#
# Directory for XML definitions for DVDs and VCDs. Items in this
# directory won't be in the MOVIE MAIN MENU, but will be used to find
# titles and images for the current DVD/VCD
#
MOVIE_DATA_DIR = 'movie-data/'

#
# Skin file that contains the actual skin code. This is imported
# from skin.py
#
OSD_SKIN = 'skins/main1/skin_main1.py'
SKIN_XML_FILE = 'skins/xml/768x576.xml'

# OSD default font. It is only used for debug/error stuff, not regular
# skinning.
OSD_DEFAULT_FONTNAME = 'skins/fonts/Cultstup.ttf'
OSD_DEFAULT_FONTSIZE = 14

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
# Mixer device
#
DEV_MIXER = '/dev/mixer'

#
# Physical ROM drives, multiple ones can be specified
# by adding comma-seperated and quoted entries.

ROM_DRIVES = [ ('/mnt/cdrom', 'CD'),
               ('/mnt/dvd', 'DVD') ]

#
# The list of filename suffixes that are used to match the files that
# are played as audio. They are used as the argument to glob.glob()
# 
SUFFIX_AUDIO_FILES     = [ '/*.[mM][pP]3',
                           '/*.[oO][gG][gG]' ]
SUFFIX_AUDIO_PLAYLISTS = [ '/*.[mM]3[uU]' ]


#
# The list of filename suffixes that are used to match the files that
# are used for the image viewer. They are used as the argument to glob.glob()
# 
SUFFIX_IMAGE_FILES = [ '/*.[jJ][pP][gG]' ]


#
# Watching TV
#
# XXX You must change this to fit your local conditions! Check out the
# file matrox_g400/frequencies.[ch] for possible choices.
#
TV_SETTINGS = 'ntsc television us-cable'
VCR_SETTINGS = 'ntsc composite1 us-cable'

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

WATCH_TV_APP = './matrox_g400/v4l1_to_mga'

#
# Where the Audio (mp3, ogg) files can be found.
#
# Format: [ ('Title1', 'directory1'), ('Title2', 'directory2'), ... ]
#
DIR_AUDIO = [ ('Test Files', 'testfiles/Music') ]

#
# Where the movie files can be found.
#
DIR_MOVIES = [ ('Test Movies', 'testfiles/Movies') ]

#
# Where the image files can be found.
#
DIR_IMAGES = [ ('Test Images', './testfiles/Images') ]

#
# This is where recorded video is written.
#
DIR_RECORD = './testfiles/Movies/Recorded'

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



# Exec a script after the osd startup. This only works with the OSD_SDL
# osd server. Matrox G400 users who wants to use the framebuffer and have
# a PAL tv may set this to './matrox_g400/mga_pal_768x576.sh'

OSD_SDL_EXEC_AFTER_STARTUP=""
