#
# config.py
#
# $Id$
#
# System configuration, e.g. where to look for MP3:s, AVI files, etc.
# XXX Change this to a regular config file, not a Python source file

#
# Config values for the video tools
#
MPLAYER_CMD = ''
MPLAYER_ARGS_MPG = ''
MPLAYER_ARGS_DVD = ''
VIDREC_MQ = ''
VIDREC_HQ = ''

# XXX Add DVD ripping:
# XXX This is using the XviD encoder
# /usr/local/bin/mencoder -ovc divx4 -divx4opts br=800:key=300:q=5 -oac mp3lame -lameopts br=80:cbr -sws 2 -x 576 -y 432 -o moviename.avi -dvd 1 -alang en
#
# 1.33  576x432
# 1.78  688x384
#
#
# FFMPEG encoder, better?
# /usr/local/bin/mencoder -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=800:keyint=300:vhq -oac mp3lame -lameopts br=80:cbr -sws 2 -vop scale=576:432 -o tst.avi -dvd 1 -ffourcc divx -alang en
#
#Scale and crop a 2.35:1 DVD
#/usr/local/bin/mencoder -ovc divx4 -divx4opts br=800:key=300:q=5 -oac mp3lame -lameopts br=80:cbr -sws 2 -vop scale=848:336,crop=720:336:0:72 -o tst.avi -dvd 1 -alang en

# XXX Need to do ratio and scaling

def ConfigInit(videotools = 'sim'):
    print 'VIDEOTOOLS = %s' % videotools

    global MPLAYER_CMD, MPLAYER_ARGS_MPG, MPLAYER_ARGS_DVD, MPLAYER_ARGS_DVDNAV, VIDREC_MQ, VIDREC_HQ
    
    if videotools == 'real':
        MPLAYER_CMD = '/usr/local/bin/mplayer'
        MPLAYER_ARGS_MPG = '-nolirc -nobps -idx -framedrop -cache 10000 -vo mga -screenw 768 -screenh 576 -fs -ao oss:/dev/dsp0'
        MPLAYER_ARGS_DVD = '-nolirc -nobps -framedrop -cache 10000 -vo mga -ao oss:/dev/dsp0 -dvd %s -alang en,se  -screenw 768 -screenh 576 -fs '
        VIDREC_MQ_TV = '/usr/local/bin/DIVX4rec -F 300000 -norm NTSC -input Television -m -r 22050 -w 320 -h 240 -ab 80 -vg 100 -vb 800 -H 50 -o %s'
        VIDREC_MQ_VCR = '/usr/local/bin/DIVX4rec -F 300000 -norm NTSC -input Composite1 -m -r 22050 -w 320 -h 240 -ab 80 -vg 100 -vb 1000 -H 50 -o %s'
        VIDREC_MQ = VIDREC_MQ_TV
    else:
        MPLAYER_CMD = '/usr/local/bin/mplayer'
        MPLAYER_ARGS_MPG = '-nobps -idx -framedrop -cache 512 -vo xv -screenw 768 -screenh 576 -fs -ao oss:/dev/dsp0'
        MPLAYER_ARGS_DVD = '-nobps -framedrop -cache 4096 -vo xv -ao oss:/dev/dsp0 -dvd %s -alang en,se  -screenw 768 -screenh 576 -fs '
        VIDREC_MQ = '/usr/local/bin/DIVX4rec -F 300000 -norm NTSC -input Composite1 -m -r 22050 -w 320 -h 240 -ab 80 -vg 300 -vb 800 -H 50 -o %s'
        
#
# The list of filename suffixes that are used to match the files that
# are played wih MPlayer. They are used as the argument to glob.glob()
# 
SUFFIX_MPLAYER_FILES = [ '/*.[aA][vV][iI]',
                         '/*.[mM][pP][gG]',
                         '/*.[mM][pP][eE][gG]',
                         '/*.[bB][iI][nN]' ]

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
        
#
# The mpg123 application
#
MPG123_APP = '/usr/bin/mpg123'

#
# The list of filename suffixes that are used to match the files that
# are played wih mpg123. They are used as the argument to glob.glob()
# 
SUFFIX_MPG123_FILES = [ '/*.[mM][pP]3' ]
SUFFIX_MPG123_PLAYLISTS = [ '/*.[mM]3[uU]' ]

#
# Watching TV
#
# You must change this to fit your local conditions! Check out the
# file matrox_g400/frequencies.[ch] for possible choices.
#
TV_SETTINGS = 'ntsc television us-cable'
VCR_SETTINGS = 'ntsc composite1 us-cable'
TV_CHANNELS = ['2', '4', '5', '6', '8', '9', '10', '11', '13', 
               '16', '17', '18', '19', '20', '21', '22', '23', '24',
               '25', '26', '27', '28', '29', '31', '32', '33', '34',
               '35', '36', '37', '38', '41', '42', '43', '44', '45', '46', '50',
               '53', '56', '57', '58', '59', '60', '61',
               '62', '64', '65', '66', '67', '69', 
               '70', '71', '72', '73', '74',
               '75', '99']
# XXX There might be a bug in this application that could cause problems on some systems,
# XXX it is disabled while I'm checking into it the next few days (2002-05-09)
WATCH_TV_APP = '/bin/echo'   # XXX Dummy
#WATCH_TV_APP = './matrox_g400/v4l1_to_mga'

#
# Where the MP3 files can be found.
#
# Format: [ ('Title1', 'directory1'), ('Title2', 'directory2'), ... ]
#
DIR_MP3 = [ ('Krister', '/hdc/krister_mp3/mp3'),
            ('Mary', '/hdc/mary') ]

#
# Where the movie files can be found.
#
DIR_MOVIES = [ ('Local', '/movies_local'),
               ('Linux Movies', '/movies'),
               ('Linux HDC Movies', '/hdc/Movies'),
               ('Linux HDC Unsorted', '/hdc/Unsorted'),
               ('Linux HDD', '/hdd/Movies'),
               ('CD-ROM files', '/dev/cdrom'),
               ]

#
# This is where recorded video is written.
#
DIR_RECORD = '/movies_local/recorded'


#
# Electronic Program Guide (EPG) settings
#
# This setting will download TV listings for Charter Cable in St Charles, MO
# from yahoo.com. It will not work outside the US as of now.
# 
EPG_URL = 'http://tv.yahoo.com/grid?.intl=us&zip=63303&.done=&lineup=us_MO24526&dur=6'
