#if 0
# -----------------------------------------------------------------------
# local_conf.py - Edit this file for your local system settings
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   This file contains a few of the options from freevo_config.py that
#   you might want to change to suit your system. Remove the '#' to
#   uncomment the setting(s) you want to change. There are more options
#   in freevo_config.py, copy those that must be changed to this file.
#
#   Then put this file in ~/.freevo/ or /etc/freevo to make upgrades easier.
#   Freevo will look in those folders first for this file.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
# Please see the file freevo/COPYING for license info.
#
# -----------------------------------------------------------------------
#endif

CONFIG_VERSION = 3.5

MPLAYER_AO_DEV        = 'oss:/dev/em8300_ma'


# How Freevo finds the config files (freevo.conf, local_conf.py, local_skin.xml)
# ==============================================================================
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


# ======================================================================
# General freevo settings:
# ======================================================================

#AUDIO_DEVICE        = '/dev/dsp'      # e.g.: /dev/dsp0, /dev/audio, /dev/alsa/?
#DEV_MIXER           = '/dev/mixer'    # mixer device 

#
# Physical ROM drives, multiple ones can be specified
# by adding comma-seperated and quoted entries.
# Should be autodetected.
#
# Format [ ('mountdir1', 'devicename1', 'displayed name1'),
#          ('mountdir2', 'devicename2', 'displayed name2'), ...]
#

#ROM_DRIVES = []

#ROM_SPEED = 8

# ======================================================================
# Freevo skin settings:
# ======================================================================

# Adjust overscan for tv out
#OVERSCAN_X = 0
#OVERSCAN_Y = 0

# XML skin to use. Press DISPLAY in the main menu to preview all skins
#SKIN_XML_FILE = 'blue_round2'


# ======================================================================
# Freevo movie settings:
# ======================================================================

#
# Where the movie files can be found.
#
DIR_MOVIES = [ ('Incoming TV Shows', '/home/dmeyer/video/incoming'), \
               ('Trailer', '/home/dmeyer/video/Trailer'),
               ('Test', '/home/dmeyer/video/Series'),
               ('Current Movies', '/home/dmeyer/video/movie'),
               ('Misc Movies/Shows', '/home/dmeyer/video/misc'),
               ('All Movies/Shows on Disc', '/home/dmeyer/video') ] + DIR_MOVIES

DIR_AUDIO = [ ('Music Collection', '/local/mp3/') ] + DIR_AUDIO

DIR_IMAGES = [ ('My Photos', '/home/dmeyer/images') ] + DIR_IMAGES

TV_SHOW_DATA_DIR = "/home/dmeyer/etc/tv-show-images/"
MOVIE_DATA_DIR   = '/home/dmeyer/etc/movie-data/'

TV_CHANNELS = [
    ('ard.szing.at','ARD','0') ,
    ('cnn.szing.at','CNN','0') ,
    ('kabel-1.szing.at','KABEL 1','0') ,
    ('n-tv.szing.at','N-TV','0') ,
    ('nord-3.szing.at','NORD 3','0') ,
    ('pro-7.szing.at','PRO 7','0') ,
    ('rtl-2.szing.at','RTL 2','0') ,
    ('rtl.szing.at','RTL','0') ,
    ('sat.1.szing.at','SAT.1','0') ,
    ('super-rtl.szing.at','SUPER RTL','0') ,
    ('zdf.szing.at','ZDF','0') ]

MPLAYER_AO_HWAC3_DEV = 'oss:/dev/em8300_ma-0'
MPLAYER_USE_WID      = 0

MPLAYER_ARGS_DEF = ('-nobps -monitoraspect 4:3 -nolirc -screenw %s -screenh %s ' %
                    (CONF.width, CONF.height))

CONTROL_ALL_AUDIO = 0
MAJOR_AUDIO_CTRL  = 'None'

ROM_SPEED = 16

RC_MPLAYER_CMDS = {
    'SUB'         : ( 'sub_visibility', 'Toggle subtitle visibility' )
}

# ======================================================================
# TV:
# ======================================================================

#
# Watching TV
#
# XXX You must change this to fit your local conditions!
#
# TV_SETTINGS  = 'NORM INPUT CHANLIST DEVICE'
# VCR_SETTINGS = 'NORM INPUT CHANLIST DEVICE'
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
#TV_SETTINGS = '%s television %s /dev/video0' % (CONF.tv, CONF.chanlist)

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
#VCR_CMD = ('/usr/local/bin/mencoder ' +    # Change. Absolute path to the runtime
#            '-tv on:driver=v4l:input=0' +   # Input 0 = Comp. V. in
#            ':norm=NTSC' +                  # Change
#            ':channel=%(channel)s' +        # Filled in by Freevo
#            ':chanlist=us-cable' +          # Change
#            ':width=320:height=240' +       # Change if needed
#            ':outfmt=yv12' +                # Prob. ok, yuy2 might be faster
#            ':device=/dev/video0' +         # CHANGE!
#            ':adevice=/dev/dsp4' +          # CHANGE!
#            ':audiorate=32000' +            # 44100 for better sound
#            ':forceaudio:forcechan=1:' +    # Forced mono for bug in my driver
#            'buffersize=64' +               # 64 Megabyte capture buffer, change?
#            ' -ovc lavc -lavcopts ' +       # Mencoder lavcodec video codec
#            'vcodec=mpeg4' +                # lavcodec mpeg-4
#            ':vbitrate=1200:' +             # Change lower/higher, bitrate
#            'keyint=30 ' +                  # Keyframe every 10 secs, change?
#            '-oac mp3lame -lameopts ' +     # Use Lame for MP3 encoding
#            'br=128:cbr:mode=3 ' +          # MP3 const. bitrate, 128 kbit/s
#            '-ffourcc divx '                # Force 'divx' ident, better compat.
#            '-o %(filename)s.avi ')         # Filled in by Freevo

# TV capture size for viewing and recording. Max 768x480 for NTSC,
# 768x576 for PAL. Set lower if you have a slow computer!
#TV_VIEW_SIZE = (640, 480)

#
# FREQUENCY_TABLE - This is only used when Freevo changes the channel natively.
# This is only the case if you are using V4L2 and any of the following plugins:
# timeshift, ivtv_record, ivtv_basic_tv.
# For the standard frequancy tables see src/tv/freq.py.  To add your own just
# replace tuner_id in the following example with a valid tuner id (ie: '5' or
# 'BBC1') and a frequency in KHz.  You may have as many entries as you like,
# anything here will simply override a coresponding entry in your standard
# frequency table and you can also have entries here that are not present i
# there.
# FREQUENCY_TABLE = {
#     'tuner_id'   :    55250,
# }


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

# TV_CHANNELS = [('69 COMEDY', 'COMEDY', '69'),
#                ('56 HISTORY', 'HISTORY', '56'),
#                ('2 KTVI', 'KTVI', '2'),
#                ('4 KMOV', 'KMOV', '4'),
#                ('5 KSDK', 'KSDK', '5'),
#                ('6 TBS', 'TBS', '6'),
#                ('11 KPLR', 'KPLR', '11'),
#                ('12 KDNL', 'KDNL', '12'),
#                ('29 LIFE', 'LIFE', '29'),
#                ('49 USA', 'USA', '49'),
#                ('30 HALMRK', 'HALMRK', '30'),
#                ('42 TNT', 'TNT', '42'),
#                ('41 FX', 'FX', '41'),
#                ('59 TLC', 'TLC', '59'),
#                ('31 TECHTV', 'TECHTV', '31'),
#                ('57 DSC', 'DSC', '57'),
#                ('66 ETV', 'ETV', '66'),
#                ('75 MTV', 'MTV', '75'),
#                ('77 VH1', 'VH1', '77'),
#                ('32 TNN', 'TNN', '32'),
#                ('43 CNN', 'CNN', '43'),
#                ('44 CNNH', 'CNNH', '44'),
#                ('46 CNBC', 'CNBC', '46'),
#                ('47 MSNBC', 'MSNBC', '47'),
#                ('48 FNC', 'FNC', '48'),
#                ('45 TWC', 'TWC', '45'),
#                ('35 ESPN', 'ESPN', '35'),
#                ('36 ESPN2', 'ESPN2', '36'),
#                ('37 GOLF', 'GOLF', '37'),
#                ('38 SPEED', 'SPEED', '38'),
#                ('40 FSM', 'FSM', '40'),
#                ('7 WGNSAT', 'WGNSAT', '7'),
#                ('8 LOOR008', 'LOOR008', '8'),
#                ('9 KETC', 'KETC', '9'),
#                ('15 CSPAN', 'CSPAN', '15'),
#                ('16 CSPAN2', 'CSPAN2', '16'),
#                ('22 TBN', 'TBN', '22'),
#                ('33 NGC', 'NGC', '33'),
#                ('34 INSP', 'INSP', '34'),
#                ('50 FAM', 'FAM', '50'),
#                ('51 NIK', 'NIK', '51'),
#                ('52 DISN', 'DISN', '52'),
#                ('53 TOOND', 'TOOND', '53'),
#                ('54 TOON', 'TOON', '54'),
#                ('55 ARTS', 'ARTS', '55'),
#                ('58 ANIMAL', 'ANIMAL', '58'),
#                ('60 TCM', 'TCM', '60'),
#                ('61 OXYGEN', 'OXYGEN', '61'),
#                ('62 FOOD', 'FOOD', '62'),
#                ('63 HGTV', 'HGTV', '63'),
#                ('64 TRAV', 'TRAV', '64'),
#                ('65 WE', 'WE', '65'),
#                ('67 SOAP', 'SOAP', '67'),
#                ('68 BET', 'BET', '68'),
#                ('70 TVLAND', 'TVLAND', '70'),
#                ('71 AMC', 'AMC', '71'),
#                ('72 BRAVO', 'BRAVO', '72'),
#                ('73 SCIFI', 'SCIFI', '73'),
#                ('74 COURT', 'COURT', '74'),
#                ('76 CMTV', 'CMTV', '76'),
#                ('78 FMC', 'FMC', '78'),
#                ('96 LOOR096', 'TV Guide', '96'),
#                ('101 Station 1a', 'Station 1a', '101', ('123', '0000', '1759')),
#                ('101 Station 1b', 'Station 1b', '101', ('123', '1800', '2359')),
#                ('102 Station 2a', 'Station 2a', '102',
#                 ('12345', '0000', '2359')),
#                ('102 Station 2b', 'Station 2b', '102', ('67', '0000', '2359')),
#                ('103 Station 3a', 'Station 3a', '103',
#                 ('1234567', '0000', '1559'), ('1234567', '2200', '2359')),
#                ('103 Station 3b', 'Station 3b', '103',
#                 ('1234567', '1600', '2159'))]


# ======================================================================
# Freevo Web Interface:
# ======================================================================

#
# To activate the build in web server, please activate the www plugin:
#
# plugin.activate('www')

#
# Web server port number. 80 is the standard port, but is often
# taken already by apache, and cannot be used unless the server
# runs as root. Use port 8080 as the default, change to 80 if
# needed.
#
# WWW_PORT = 8080

#
# Username / Password combinations to login to the web interface.
# These should be overridden in local_conf.py
# 
# WWW_USERS = { "user1" : "changeme", 
#            "optional" : "changeme2" }
#

OVERSCAN_X = 0 # 20
OVERSCAN_Y = 10

#OSD_SKIN = 'skins/dischi1/skin_dischi1.py'

#SKIN_XML_FILE = 'blue_round2'
SKIN_XML_FILE = 'blue'
# SKIN_XML_FILE = 'info'
SKIN_XML_FILE = 'noia'
#SKIN_XML_FILE = 'barbieri'

#plugin.remove(plugin_tv)
plugin.remove('tv.mplayer')
plugin.activate('tv.tvtime')

plugin.activate('idlebar.interface')

plugin.activate('idlebar.mail',    level=10, args=('/var/spool/mail/dmeyer', ))
plugin.activate('idlebar.tv',      level=20)
plugin.activate('idlebar.weather', level=30, args=('EDDW',))
plugin.activate('idlebar.clock',   level=50)
plugin.activate('idlebar.cdstatus',   level=20)
plugin.activate('idlebar.holidays',   level=20)


plugin.activate('video.mover', args=('/home/dmeyer/video/incoming',
                                     '/home/dmeyer/video/Series'))

plugin.activate('usb')
plugin.activate('image.camera', args=('Finepix', '04cb:0100', '/mnt/camera'))

plugin.activate('df')

EVENTS['menu']['1'] = Event(MENU_CALL_ITEM_ACTION, arg='imdb_search_or_cover_search')
EVENTS['video']['1'] = Event(VIDEO_SEND_MPLAYER_CMD, arg='sub_visibility')

#plugin.activate('www')
WWW_USERS = { 'dmeyer' : 'online' }
plugin.activate('audio.coversearch')
MPLAYER_SOFTWARE_SCALER = '-xy %s -sws 2 -vop scale:-1:-1:-1:100' % CONF.width

IMDB_REMOVE_FROM_SEARCHSTRING = ('the', 'a', 'dvdrip', 'dvd', 'proper', 'sharereactor')

#OVERSCAN_X = 20
#OVERSCAN_Y = 20
MPLAYER_VO_DEV = 'x11'

plugin.activate('video.xine')

EVENTS['dvd']['LANG']  = VIDEO_NEXT_AUDIOLANG
#EVENTS['dvd']['MENU']  = DVDNAV_MENU
EVENTS['dvd']['TITLE'] = DVDNAV_TITLEMENU

EVENTS['dvd']['1'] = VIDEO_NEXT_AUDIOLANG

