#
# freevo_config.py
#
# $Id$
#
# System configuration, e.g. where to look for MP3:s, AVI files, etc.

#
# Config values for the video tools
#
MPLAYER_CMD = ''
MPLAYER_ARGS_MPG = ''
MPLAYER_ARGS_DVD = ''
VIDREC_MQ = ''
VIDREC_HQ = ''

def ConfigInit(videotools = 'sim'):
    print 'VIDEOTOOLS = %s' % videotools

    global MPLAYER_CMD, MPLAYER_ARGS_MPG, MPLAYER_ARGS_DVD, MPLAYER_ARGS_VCD
    global MPLAYER_ARGS_DVDNAV, VIDREC_MQ, VIDREC_HQ

    #
    # There are two sets of tool settings, one for a real box,
    # and one for development.
    # 
    if videotools == 'real':
        MPLAYER_CMD = 'mplayer'
        MPLAYER_ARGS_MPG = ('-nolirc -nobps -idx -framedrop -cache 5000 ' +
                            '-vo mga -screenw 768 -screenh 576 -fs ' +
                            ' -ao oss:/dev/dsp0')
        MPLAYER_ARGS_DVD = ('-nolirc -nobps -framedrop -cache 5000 -vo mga ' +
                            '-ao oss:/dev/dsp0 -dvd %s -alang en,se  ' +      
                            '-screenw 768 -screenh 576 -fs ')
        MPLAYER_ARGS_VCD = ('-nolirc -nobps -framedrop -cache 5000 -vo mga ' +
                            '-ao oss:/dev/dsp0 -vcd %s -alang en,se  ' +      
                            '-screenw 768 -screenh 576 -fs ')
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
    else:
        MPLAYER_CMD = 'mplayer'
        MPLAYER_ARGS_MPG = ('-nobps -idx -framedrop -cache 512 -vo xv ' +
                            ' -screenw 768 -screenh 576 -fs -ao oss:/dev/dsp0')
        MPLAYER_ARGS_DVD = ('-nobps -framedrop -cache 4096 -vo xv ' +
                            '-ao oss:/dev/dsp0 -dvd %s -alang en,se ' +
                            '  -screenw 768 -screenh 576 -fs ')
        MPLAYER_ARGS_VCD = ('-nobps -framedrop -cache 4096 -vo xv ' +
                            '-ao oss:/dev/dsp0 -vcd %s -alang en,se ' +
                            '  -screenw 768 -screenh 576 -fs ')
        VIDREC_MQ = ('DIVX4rec -F 300000 -norm NTSC ' +
                     '-input Composite1 -m -r 22050 -w 320 -h 240 -ab 80 ' +
                     '-vg 300 -vb 800 -H 50 -o %s')
        
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
						 '/*.[oO][gG][mM]' ]

#
# Config for xml support in the movie browser
# the regexp has to be with ([0-9]|[0-9][0-9]) so we can get the numbers
#

SUFFIX_FREEVO_FILES = [ '/*.[xX][mM][lL]' ]
TV_SHOW_REGEXP = "s?([0-9]|[0-9][0-9])[xe]([0-9]|[0-9][0-9])[^0-9]"
TV_SHOW_IMAGES = "tv-show-images/"


#
# Skin file that contains the actual skin code. This is imported
# from skin.py
#
OSD_SKIN = 'skins/test2/skin_test2.py'

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
# The mpg123 application
#
MPG123_APP = 'mpg123'

#
# Mixer device
#
DEV_MIXER = '/dev/mixer'

#
# CD mount point
#
CD_MOUNT_POINT = '/mnt/cdrom'

#
# The list of filename suffixes that are used to match the files that
# are played wih mpg123. They are used as the argument to glob.glob()
# 
SUFFIX_MPG123_FILES = [ '/*.[mM][pP]3' ]
SUFFIX_MPG123_PLAYLISTS = [ '/*.[mM]3[uU]' ]


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
# Where the MP3 files can be found.
#
# Format: [ ('Title1', 'directory1'), ('Title2', 'directory2'), ... ]
#
DIR_MP3 = [ ('Test Music', './testfiles/Music') ]

#
# Where the movie files can be found.
#
DIR_MOVIES = [ ('Test Movies', './testfiles/Movies') ]

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

